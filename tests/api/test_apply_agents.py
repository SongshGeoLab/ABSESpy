#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for PatchModule.apply_agents.

This suite validates the three usage modes of `apply_agents`:
- attr mode (single-agent attribute access)
- func mode (single-agent function application)
- aggregator mode (reduce cell-level ActorsList)

It also covers xarray output and edge cases (empty cells, mixed occupancy).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
import xarray as xr

from abses.agents.actor import Actor
from abses.core.model import MainModel
from abses.space.patch import PatchModule

if TYPE_CHECKING:
    pass


@pytest.fixture(name="small_grid")
def fixture_small_grid(model: MainModel) -> PatchModule:
    """Create a small 3x3 grid for testing.

    Returns:
        PatchModule: 3x3 grid with default PatchCell.
    """
    return model.nature.create_module(shape=(3, 3), name="apply_agents_grid")


class TestApplyAgentsAttr:
    """Tests for attr mode of apply_agents."""

    def test_attr_single_agent_and_empty(self, small_grid: PatchModule) -> None:
        """Attr mode returns float array with NaN on empty cells.

        Scenario:
        - Place an Actor with attribute `type` on (1,1) and (0,2)
        - Other cells remain empty
        - Call `apply_agents(attr='type')`

        Expect:
        - Float array shape (3,3)
        - Positions without agents are NaN
        - Positions with agents equal to their `type`
        """
        # arrange
        a1 = small_grid.array_cells[1, 1].agents.new(Actor, singleton=True)
        a1.type = 1
        a2 = small_grid.array_cells[0, 2].agents.new(Actor, singleton=True)
        a2.type = 0

        # act
        arr = small_grid.apply_agents(attr="type")

        # assert
        assert isinstance(arr, np.ndarray)
        assert arr.shape == small_grid.shape2d
        assert np.isnan(arr[2, 0])  # empty
        assert arr[1, 1] == pytest.approx(1.0)
        assert arr[0, 2] == pytest.approx(0.0)

    def test_attr_xarray_output(self, small_grid: PatchModule) -> None:
        """xarray output returns DataArray with coords and CRS."""
        small_grid.array_cells[2, 2].agents.new(Actor, singleton=True).type = 1
        xda = small_grid.apply_agents(attr="type", dtype="xarray", name="agent_type")
        assert isinstance(xda, xr.DataArray)
        assert set(xda.coords.keys()) >= {"x", "y"}
        assert xda.rio.crs is not None
        assert xda.name == "agent_type"

    def test_attr_missing_attribute_default_nan(self, small_grid: PatchModule) -> None:
        """Missing attribute should yield NaN by default.

        Scenario:
        - Place an Actor without `foo` attribute
        - Request attr='foo' -> NaN
        """
        small_grid.array_cells[0, 0].agents.new(Actor, singleton=True)
        arr = small_grid.apply_agents(attr="foo")
        assert np.isnan(arr[0, 0])

    def test_attr_first_agent_when_multiple(self, small_grid: PatchModule) -> None:
        """When multiple agents exist, the first is used.

        Scenario:
        - Put two agents on same cell with different `type` values
        - Expect the first created agent value to be taken
        """
        c = small_grid.array_cells[1, 2]
        a1 = c.agents.new(Actor, singleton=True)
        a1.type = 1
        a2 = c.agents.new(Actor, singleton=True)
        a2.type = 0
        arr = small_grid.apply_agents(attr="type")
        assert arr[1, 2] == pytest.approx(1.0)


class TestApplyAgentsFunc:
    """Tests for func mode of apply_agents."""

    def test_func_boolean_to_float(self, small_grid: PatchModule) -> None:
        """Func mode results are cast to float, NaN on empty cells.

        Scenario:
        - Place one agent with an `is_happy` attribute on (0,0)
        - Use func to map True->1.0 / False->0.0
        """
        agent = small_grid.array_cells[0, 0].agents.new(Actor, singleton=True)
        agent.is_happy = True

        arr = small_grid.apply_agents(
            func=lambda a: 1.0 if getattr(a, "is_happy", False) else 0.0
        )
        assert isinstance(arr, np.ndarray)
        assert arr.dtype == float
        assert arr[0, 0] == pytest.approx(1.0)
        assert np.isnan(arr[1, 1])

    def test_func_error_returns_nan(self, small_grid: PatchModule) -> None:
        """If func raises, casting fallback should produce NaN for that cell."""
        small_grid.array_cells[0, 0].agents.new(Actor, singleton=True)

        def bad(_a: Actor) -> float:
            raise RuntimeError("boom")

        arr = small_grid.apply_agents(func=bad)
        assert np.isnan(arr[0, 0])

    def test_func_xarray_output_name(self, small_grid: PatchModule) -> None:
        """xarray output name should apply in func mode."""
        small_grid.array_cells[2, 1].agents.new(Actor, singleton=True).value = 3.3
        xda = small_grid.apply_agents(
            func=lambda a: getattr(a, "value", np.nan), dtype="xarray", name="val"
        )
        assert isinstance(xda, xr.DataArray)
        assert xda.name == "val"


class TestApplyAgentsAggregator:
    """Tests for aggregator mode of apply_agents."""

    def test_count_agents(self, small_grid: PatchModule) -> None:
        """Aggregator can count agents per cell.

        Scenario:
        - Put 2 agents on (1,1), 1 agent on (2,0)
        - Aggregator returns len(actors)
        """
        cell_11 = small_grid.array_cells[1, 1]
        cell_11.agents.new(Actor, singleton=True)
        cell_11.agents.new(Actor, singleton=True)
        small_grid.array_cells[2, 0].agents.new(Actor, singleton=True)

        arr = small_grid.apply_agents(aggregator=lambda actors: len(actors))
        assert arr.dtype == float
        assert arr[1, 1] == pytest.approx(2.0)
        assert arr[2, 0] == pytest.approx(1.0)
        assert np.isnan(arr[0, 0])

    def test_aggregator_mean_fraction(self, small_grid: PatchModule) -> None:
        """Aggregator can compute fractions (e.g., minority proportion)."""
        c = small_grid.array_cells[1, 1]
        for t in [1, 1, 0]:
            ag = c.agents.new(Actor, singleton=True)
            ag.type = t

        def minority_frac(actors) -> float:
            if len(actors) == 0:
                return np.nan
            types = actors.array("type")
            return float((types == 1).mean())

        arr = small_grid.apply_agents(aggregator=minority_frac)
        assert arr[1, 1] == pytest.approx(2.0 / 3.0)

    def test_aggregator_non_numeric_casts_nan(self, small_grid: PatchModule) -> None:
        """Non-numeric aggregator output should be coerced to NaN by float casting."""
        small_grid.array_cells[0, 1].agents.new(Actor, singleton=True)

        def non_numeric(_actors) -> str:
            return "text"

        arr = small_grid.apply_agents(aggregator=non_numeric)
        assert np.isnan(arr[0, 1])

    @pytest.mark.parametrize(
        "positions, expected",
        [
            ([(0, 0)], 1.0),
            ([(0, 0), (0, 0)], 2.0),
            ([], np.nan),
        ],
    )
    def test_edge_cases_counts(
        self, small_grid: PatchModule, positions: list[tuple[int, int]], expected: float
    ) -> None:
        """Edge cases: zero/multiple agents on a single cell.

        Args:
            small_grid: testing grid
            positions: list of coordinates to place agents (on the same cell)
            expected: expected count at (0,0)
        """
        for _ in positions:
            small_grid.array_cells[0, 0].agents.new(Actor, singleton=True)

        arr = small_grid.apply_agents(aggregator=lambda actors: len(actors))
        val = arr[0, 0]
        if np.isnan(expected):
            assert np.isnan(val)
        else:
            assert val == pytest.approx(expected)
