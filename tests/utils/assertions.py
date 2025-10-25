#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Custom assertion functions for ABSESpy tests.

This module provides specialized assertion functions for testing ABSESpy
components, including tolerance-based comparisons and state validation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Optional

import numpy as np
import pandas as pd

from abses import ActorsList, PatchCell

if TYPE_CHECKING:
    from abses.core.model import MainModel
    from abses.space.patch import PatchModule


def assert_actorslist_equal(
    actual: ActorsList,
    expected: ActorsList,
    msg: Optional[str] = None,
    check_order: bool = False,
) -> None:
    """Assert that two ActorsList instances are equal.

    Args:
        actual: The actual ActorsList to test.
        expected: The expected ActorsList to compare against.
        msg: Optional custom error message.
        check_order: Whether to check the order of actors.

    Raises:
        AssertionError: If the ActorsList instances are not equal.
    """
    if msg is None:
        msg = "ActorsList instances are not equal"

    # Check lengths
    assert len(actual) == len(expected), (
        f"{msg}: lengths differ ({len(actual)} vs {len(expected)})"
    )

    if len(actual) == 0:
        return  # Both empty, they're equal

    # Check types
    actual_types = {type(actor) for actor in actual}
    expected_types = {type(actor) for actor in expected}
    assert actual_types == expected_types, f"{msg}: actor types differ"

    if check_order:
        # Check order
        for i, (actual_actor, expected_actor) in enumerate(zip(actual, expected)):
            assert actual_actor.unique_id == expected_actor.unique_id, (
                f"{msg}: actor {i} differs"
            )
    else:
        # Check that all actors are present (order doesn't matter)
        actual_ids = {actor.unique_id for actor in actual}
        expected_ids = {actor.unique_id for actor in expected}
        assert actual_ids == expected_ids, f"{msg}: actor IDs differ"


def assert_raster_close(
    actual: np.ndarray,
    expected: np.ndarray,
    rtol: float = 1e-5,
    atol: float = 1e-8,
    msg: Optional[str] = None,
) -> None:
    """Assert that two raster arrays are close within tolerance.

    Args:
        actual: The actual raster array to test.
        expected: The expected raster array to compare against.
        rtol: Relative tolerance for comparison.
        atol: Absolute tolerance for comparison.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the raster arrays are not close within tolerance.
    """
    if msg is None:
        msg = "Raster arrays are not close within tolerance"

    # Check shapes
    assert actual.shape == expected.shape, (
        f"{msg}: shapes differ ({actual.shape} vs {expected.shape})"
    )

    # Check values
    if not np.allclose(actual, expected, rtol=rtol, atol=atol):
        # Find differences
        diff = np.abs(actual - expected)
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)

        raise AssertionError(
            f"{msg}: arrays differ (max diff: {max_diff:.2e}, mean diff: {mean_diff:.2e})"
        )


def assert_model_state_valid(model: "MainModel", msg: Optional[str] = None) -> None:
    """Assert that a model is in a valid state.

    Args:
        model: The model to validate.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the model is not in a valid state.
    """
    if msg is None:
        msg = "Model is not in a valid state"

    # Check basic properties
    assert hasattr(model, "agents"), f"{msg}: missing agents attribute"
    assert hasattr(model, "nature"), f"{msg}: missing nature attribute"
    assert hasattr(model, "datacollector"), f"{msg}: missing datacollector attribute"

    # Check agents
    assert isinstance(model.agents, ActorsList), f"{msg}: agents is not ActorsList"

    # Check nature
    assert model.nature is not None, f"{msg}: nature is None"

    # Check datacollector
    assert hasattr(model.datacollector, "collect"), (
        f"{msg}: datacollector missing collect method"
    )
    assert hasattr(model.datacollector, "get_model_vars_dataframe"), (
        f"{msg}: datacollector missing get_model_vars_dataframe method"
    )

    # Check that all agents are on valid cells
    for agent in model.agents:
        if agent.alive:
            assert agent.at is not None, (
                f"{msg}: agent {agent.unique_id} has no location"
            )
            assert agent in agent.at.agents, (
                f"{msg}: agent {agent.unique_id} not in cell agents"
            )


def assert_cell_state_valid(cell: PatchCell, msg: Optional[str] = None) -> None:
    """Assert that a cell is in a valid state.

    Args:
        cell: The cell to validate.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the cell is not in a valid state.
    """
    if msg is None:
        msg = "Cell is not in a valid state"

    # Check basic properties
    assert hasattr(cell, "agents"), f"{msg}: missing agents attribute"
    assert hasattr(cell, "layer"), f"{msg}: missing layer attribute"
    assert hasattr(cell, "model"), f"{msg}: missing model attribute"

    # Check agents
    assert isinstance(cell.agents, ActorsList), f"{msg}: agents is not ActorsList"

    # Check that all agents on this cell are actually on this cell
    for agent in cell.agents:
        if agent.alive:
            assert agent.at == cell, f"{msg}: agent {agent.unique_id} location mismatch"


def assert_module_state_valid(module: "PatchModule", msg: Optional[str] = None) -> None:
    """Assert that a module is in a valid state.

    Args:
        module: The module to validate.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the module is not in a valid state.
    """
    if msg is None:
        msg = "Module is not in a valid state"

    # Check basic properties
    assert hasattr(module, "cells_lst"), f"{msg}: missing cells_lst attribute"
    assert hasattr(module, "array_cells"), f"{msg}: missing array_cells attribute"
    assert hasattr(module, "shape2d"), f"{msg}: missing shape2d attribute"

    # Check shape consistency
    assert module.shape2d == module.array_cells.shape, f"{msg}: shape mismatch"

    # Check that all cells are valid
    for cell in module.cells_lst:
        assert_cell_state_valid(cell, f"{msg}: cell {cell.pos} invalid")


def assert_agent_properties_valid(
    agent: Any, required_properties: Iterable[str], msg: Optional[str] = None
) -> None:
    """Assert that an agent has all required properties.

    Args:
        agent: The agent to validate.
        required_properties: Iterable of required property names.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the agent is missing required properties.
    """
    if msg is None:
        msg = "Agent is missing required properties"

    missing_properties = []
    for prop in required_properties:
        if not hasattr(agent, prop):
            missing_properties.append(prop)

    if missing_properties:
        raise AssertionError(f"{msg}: missing properties {missing_properties}")


def assert_dataframe_structure_valid(
    df: pd.DataFrame,
    required_columns: Optional[Iterable[str]] = None,
    min_rows: int = 0,
    msg: Optional[str] = None,
) -> None:
    """Assert that a DataFrame has valid structure.

    Args:
        df: The DataFrame to validate.
        required_columns: Optional iterable of required column names.
        min_rows: Minimum number of rows expected.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the DataFrame structure is invalid.
    """
    if msg is None:
        msg = "DataFrame structure is invalid"

    # Check minimum rows
    assert len(df) >= min_rows, f"{msg}: insufficient rows ({len(df)} < {min_rows})"

    # Check required columns
    if required_columns is not None:
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise AssertionError(f"{msg}: missing columns {missing_columns}")


def assert_numpy_array_valid(
    arr: np.ndarray,
    expected_shape: Optional[tuple] = None,
    expected_dtype: Optional[np.dtype] = None,
    allow_nan: bool = False,
    msg: Optional[str] = None,
) -> None:
    """Assert that a numpy array is valid.

    Args:
        arr: The array to validate.
        expected_shape: Optional expected shape.
        expected_dtype: Optional expected dtype.
        allow_nan: Whether NaN values are allowed.
        msg: Optional custom error message.

    Raises:
        AssertionError: If the array is invalid.
    """
    if msg is None:
        msg = "Numpy array is invalid"

    # Check shape
    if expected_shape is not None:
        assert arr.shape == expected_shape, (
            f"{msg}: shape mismatch ({arr.shape} vs {expected_shape})"
        )

    # Check dtype
    if expected_dtype is not None:
        assert arr.dtype == expected_dtype, (
            f"{msg}: dtype mismatch ({arr.dtype} vs {expected_dtype})"
        )

    # Check for NaN values
    if not allow_nan and np.any(np.isnan(arr)):
        nan_count = np.sum(np.isnan(arr))
        raise AssertionError(f"{msg}: contains {nan_count} NaN values")


def assert_spatial_consistency(
    module: "PatchModule", msg: Optional[str] = None
) -> None:
    """Assert spatial consistency of a module.

    Args:
        module: The module to validate.
        msg: Optional custom error message.

    Raises:
        AssertionError: If spatial consistency is violated.
    """
    if msg is None:
        msg = "Spatial consistency violated"

    # Check that array_cells and cells_lst are consistent
    array_cells = module.array_cells
    cells_lst = list(module.cells_lst)

    assert len(array_cells.flat) == len(cells_lst), f"{msg}: cell count mismatch"

    # Check that positions are consistent
    for i in range(array_cells.shape[0]):
        for j in range(array_cells.shape[1]):
            cell = array_cells[i, j]
            assert cell.pos == (i, j), f"{msg}: position mismatch at ({i}, {j})"


def assert_performance_within_threshold(
    execution_time: float,
    threshold: float,
    operation_name: str,
    msg: Optional[str] = None,
) -> None:
    """Assert that execution time is within threshold.

    Args:
        execution_time: The actual execution time in seconds.
        threshold: The maximum allowed execution time in seconds.
        operation_name: Name of the operation being tested.
        msg: Optional custom error message.

    Raises:
        AssertionError: If execution time exceeds threshold.
    """
    if msg is None:
        msg = f"{operation_name} execution time exceeds threshold"

    assert execution_time <= threshold, (
        f"{msg}: {execution_time:.3f}s > {threshold:.3f}s"
    )


def assert_memory_usage_reasonable(
    memory_increase: int,
    threshold_mb: float = 100.0,
    operation_name: str = "operation",
    msg: Optional[str] = None,
) -> None:
    """Assert that memory usage increase is reasonable.

    Args:
        memory_increase: Memory increase in bytes.
        threshold_mb: Maximum allowed memory increase in MB.
        operation_name: Name of the operation being tested.
        msg: Optional custom error message.

    Raises:
        AssertionError: If memory usage exceeds threshold.
    """
    if msg is None:
        msg = f"{operation_name} memory usage exceeds threshold"

    threshold_bytes = threshold_mb * 1024 * 1024
    memory_mb = memory_increase / 1024 / 1024

    assert memory_increase <= threshold_bytes, (
        f"{msg}: {memory_mb:.1f}MB > {threshold_mb:.1f}MB"
    )
