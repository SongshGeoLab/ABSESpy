#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Regression tests for silent wrong results on PatchModule's hot paths (#153).

Each test pins one place that used to return plausible-looking data instead
of the right answer or an error.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pytest
import xarray as xr

from abses.agents.actor import Actor
from abses.agents.sequences import ActorsList
from abses.core.model import MainModel
from abses.space.patch import PatchModule
from abses.utils.func import set_null_values

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


@pytest.fixture(name="grid")
def fixture_grid(model: MainModel) -> PatchModule:
    """A 3x3 grid whose top-left cell is masked out."""
    module = model.nature.create_module(shape=(3, 3), name="silent_errors_grid")
    mask = np.ones((3, 3), dtype=bool)
    mask[0, 0] = False
    module.mask = mask
    return module


class TestMaskAppliesToEveryDtype:
    """`apply_mask=True` must null the masked cells whatever the dtype."""

    def test_integer_raster_is_masked(self, grid: PatchModule) -> None:
        """Integers are upcast to float, and the masked cell becomes NaN."""
        data = np.arange(9).reshape(3, 3)

        grid.apply_raster(data, attr_name="x", apply_mask=True)

        assert np.isnan(grid.array_cells[0, 0].x)
        assert grid.array_cells[1, 1].x == 4

    @pytest.mark.parametrize("dtype", [np.uint8, np.bool_], ids=["uint8", "bool"])
    def test_unsigned_and_bool_rasters_are_masked(
        self, grid: PatchModule, dtype: type
    ) -> None:
        """Unsigned integers and booleans, common raster dtypes, mask too."""
        data = np.ones((3, 3), dtype=dtype)

        grid.apply_raster(data, attr_name="x", apply_mask=True)

        assert np.isnan(grid.array_cells[0, 0].x)
        assert grid.array_cells[1, 1].x == 1

    def test_dataarray_raster_is_masked(self, grid: PatchModule) -> None:
        """The xarray path accepts `apply_mask` like the ndarray path."""
        data = xr.DataArray(
            np.arange(9, dtype=float).reshape(3, 3), coords=grid.coords
        ).rio.write_crs(grid.crs)

        grid.apply_raster(data, attr_name="x", apply_mask=True)

        assert np.isnan(grid.array_cells[0, 0].x)
        assert grid.array_cells[1, 1].x == 4

    def test_caller_array_is_left_untouched(self, grid: PatchModule) -> None:
        """Masking works on a copy, so the caller's array keeps its values."""
        data = np.arange(9, dtype=float).reshape(3, 3)

        grid.apply_raster(data, attr_name="x", apply_mask=True)

        assert data[0, 0] == 0.0

    @pytest.mark.parametrize(
        "arr, null",
        [
            pytest.param(np.array([1, 2]), np.nan, id="int"),
            pytest.param(np.array([1.0, 2.0]), np.nan, id="float"),
            pytest.param(np.array(["a", "b"]), "", id="unicode"),
            pytest.param(np.array([b"a", b"b"]), b"", id="bytes"),
        ],
    )
    def test_set_null_values_returns_a_new_array(
        self, arr: np.ndarray, null: Any
    ) -> None:
        """Every dtype gets the same contract: a new array, input unchanged."""
        original = arr.copy()

        result = set_null_values(arr, np.array([True, False]))

        assert result is not arr
        np.testing.assert_array_equal(arr, original)
        if isinstance(null, float):
            assert np.isnan(result[0])
        else:
            assert result[0] == null
        assert result[1] == original[1]


def test_apply_raster_rejects_unsupported_input(grid: PatchModule) -> None:
    """An unsupported input type raises instead of silently returning None."""
    with pytest.raises(TypeError, match="list"):
        grid.apply_raster([1, 2, 3], attr_name="x")
    assert "x" not in grid.attributes


def test_mask_change_refreshes_cells_lst(grid: PatchModule) -> None:
    """Reading `cells_lst` must not freeze the mask it was computed from."""
    assert len(grid.cells_lst) == 8

    new_mask = np.ones((3, 3), dtype=bool)
    new_mask[:, 0] = False
    grid.mask = new_mask

    assert len(grid.cells_lst) == int(grid.xda.sum()) == 6
    assert grid.array_cells[1, 0] not in grid.cells_lst


class TestApplyAgentsFailures:
    """A failing callable warns once per call, not once per cell."""

    @pytest.fixture(name="occupied")
    def fixture_occupied(self, model: MainModel) -> PatchModule:
        """A 3x3 grid with an actor on every cell."""
        module = model.nature.create_module(shape=(3, 3), name="occupied_grid")
        for cell in module.array_cells.flat:
            cell.agents.new(Actor, singleton=True)
        return module

    def test_failing_aggregator_warns_once(
        self, occupied: PatchModule, caplog: LogCaptureFixture
    ) -> None:
        """Nine failing cells give NaN everywhere and a single warning."""

        def broken(_actors: ActorsList[Actor]) -> float:
            raise RuntimeError("boom")

        with caplog.at_level(logging.WARNING, logger="abses.space.patch"):
            arr = occupied.apply_agents(aggregator=broken)

        assert np.isnan(arr).all()
        warnings = [r for r in caplog.records if r.name == "abses.space.patch"]
        assert len(warnings) == 1
        assert "9 cell(s)" in warnings[0].getMessage()
        assert "boom" in warnings[0].getMessage()

    @pytest.mark.parametrize(
        "error",
        [
            pytest.param(MemoryError, id="memory"),
            pytest.param(AttributeError, id="typo-attribute"),
            pytest.param(NameError, id="typo-name"),
        ],
    )
    def test_bug_errors_propagate(
        self, occupied: PatchModule, error: type[Exception]
    ) -> None:
        """Errors that signal a bug, not a missing value, are not hidden."""

        def failing(_agent: Actor) -> float:
            raise error

        with pytest.raises(error):
            occupied.apply_agents(func=failing)
