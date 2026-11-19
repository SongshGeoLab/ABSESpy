#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Regression tests for silent wrong results on PatchModule's hot paths (#153).

Each test pins one place that used to return plausible-looking data instead
of the right answer or an error.
"""

from __future__ import annotations

from unittest import mock

import numpy as np
import pytest

from abses.agents.actor import Actor
from abses.core.model import MainModel
from abses.space import patch as patch_module
from abses.space.patch import PatchModule
from abses.utils.func import set_null_values


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
    def test_set_null_values_returns_a_new_array(self, arr, null) -> None:
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

    assert len(grid.cells_lst) == int(new_mask.sum()) == 6
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

    def test_failing_aggregator_warns_once(self, occupied: PatchModule) -> None:
        """Nine failing cells give NaN everywhere and a single warning."""

        def broken(_actors) -> float:
            raise RuntimeError("boom")

        with mock.patch.object(patch_module.logger, "warning") as warn:
            arr = occupied.apply_agents(aggregator=broken)

        assert np.isnan(arr).all()
        assert warn.call_count == 1
        message = warn.call_args.args[0] % warn.call_args.args[1:]
        assert "9" in message and "boom" in message

    def test_memory_error_propagates(self, occupied: PatchModule) -> None:
        """Running out of memory is not a per-cell failure to paper over."""

        def exhausted(_agent) -> float:
            raise MemoryError

        with pytest.raises(MemoryError):
            occupied.apply_agents(func=exhausted)
