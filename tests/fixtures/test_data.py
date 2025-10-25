#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Standardized test data fixtures for ABSESpy tests.

This module provides standardized test datasets and fixtures for consistent
testing across different test modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import numpy as np
import xarray as xr

if TYPE_CHECKING:
    pass


# Test data constants
SMALL_GRID_SIZE = (10, 10)
MEDIUM_GRID_SIZE = (50, 50)
LARGE_GRID_SIZE = (100, 100)

SMALL_AGENT_COUNT = 10
MEDIUM_AGENT_COUNT = 100
LARGE_AGENT_COUNT = 500


def create_test_raster_data(
    shape: Tuple[int, int], data_type: str = "temperature", seed: Optional[int] = None
) -> np.ndarray:
    """Create standardized test raster data.

    Args:
        shape: Shape of the raster data (height, width).
        data_type: Type of data to generate ("temperature", "elevation", "resources").
        seed: Optional random seed for reproducibility.

    Returns:
        Numpy array with test data.
    """
    if seed is not None:
        np.random.seed(seed)

    if data_type == "temperature":
        # Temperature gradient (warmer in center)
        center_y, center_x = shape[0] // 2, shape[1] // 2
        data = np.zeros(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                distance = np.sqrt((i - center_y) ** 2 + (j - center_x) ** 2)
                data[i, j] = 30.0 - distance * 0.5
        return data

    elif data_type == "elevation":
        # Elevation data (mountain-like)
        center_y, center_x = shape[0] // 2, shape[1] // 2
        data = np.zeros(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                distance = np.sqrt((i - center_y) ** 2 + (j - center_x) ** 2)
                data[i, j] = max(0, 100 - distance * 2)
        return data

    elif data_type == "resources":
        # Resource data (clustered)
        data = np.random.uniform(50, 100, shape)
        # Add some clustering
        for _ in range(3):
            center_y = np.random.randint(shape[0] // 4, 3 * shape[0] // 4)
            center_x = np.random.randint(shape[1] // 4, 3 * shape[1] // 4)
            radius = np.random.randint(3, 8)

            for i in range(max(0, center_y - radius), min(shape[0], center_y + radius)):
                for j in range(
                    max(0, center_x - radius), min(shape[1], center_x + radius)
                ):
                    distance = np.sqrt((i - center_y) ** 2 + (j - center_x) ** 2)
                    if distance <= radius:
                        data[i, j] = min(100, data[i, j] + 20)
        return data

    elif data_type == "slope":
        # Slope data
        return np.random.uniform(0, 20, shape)

    elif data_type == "water":
        # Water data (boolean-like)
        return np.random.choice([0, 1], shape, p=[0.9, 0.1]).astype(float)

    else:
        # Default: random data
        return np.random.uniform(0, 100, shape)


def create_test_xarray_data(
    shape: Tuple[int, int],
    data_type: str = "temperature",
    crs: str = "EPSG:4326",
    seed: Optional[int] = None,
) -> xr.DataArray:
    """Create standardized test xarray data.

    Args:
        shape: Shape of the data (height, width).
        data_type: Type of data to generate.
        crs: Coordinate reference system.
        seed: Optional random seed for reproducibility.

    Returns:
        xarray DataArray with test data.
    """
    data = create_test_raster_data(shape, data_type, seed)

    # Create coordinates
    y_coords = np.linspace(shape[0] - 0.5, 0.5, shape[0])
    x_coords = np.linspace(0.5, shape[1] - 0.5, shape[1])

    # Create DataArray
    xda = xr.DataArray(
        data,
        dims=["y", "x"],
        coords={"y": y_coords, "x": x_coords},
    )

    # Set CRS
    xda.rio.write_crs(crs, inplace=True)

    return xda


def create_test_config(
    model_name: str = "test_model",
    time_end: int = 100,
    additional_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized test configuration.

    Args:
        model_name: Name of the model.
        time_end: End time for the model.
        additional_params: Additional parameters to include.

    Returns:
        Dictionary with test configuration.
    """
    config = {"model": {"name": model_name}, "time": {"end": time_end}}

    if additional_params:
        config.update(additional_params)

    return config


def create_test_agent_data(
    count: int, agent_type: str = "TestActor", seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Create standardized test agent data.

    Args:
        count: Number of agents to create.
        agent_type: Type of agent.
        seed: Optional random seed for reproducibility.

    Returns:
        List of dictionaries with agent data.
    """
    if seed is not None:
        np.random.seed(seed)

    agents = []
    for i in range(count):
        agent_data = {
            "unique_id": f"{agent_type}_{i}",
            "breed": agent_type,
            "size": float(i + 1),
            "wealth": float((i + 1) * 10),
            "age": i,
            "is_active": i % 2 == 0,
            "performance_metric": float(i % 100),
        }
        agents.append(agent_data)

    return agents


def create_test_spatial_data(
    shape: Tuple[int, int],
    data_types: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> Dict[str, np.ndarray]:
    """Create standardized test spatial data.

    Args:
        shape: Shape of the spatial data.
        data_types: List of data types to generate.
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary mapping data type names to numpy arrays.
    """
    if data_types is None:
        data_types = ["temperature", "elevation", "resources", "slope"]

    spatial_data = {}
    for data_type in data_types:
        spatial_data[data_type] = create_test_raster_data(shape, data_type, seed)

    return spatial_data


def create_test_module_data(
    shape: Tuple[int, int],
    resolution: float = 1.0,
    data_types: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Create standardized test module data.

    Args:
        shape: Shape of the module.
        resolution: Resolution of the module.
        data_types: List of data types to generate.
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary with module data.
    """
    if data_types is None:
        data_types = ["temperature", "elevation", "resources"]

    spatial_data = create_test_spatial_data(shape, data_types, seed)

    module_data = {
        "shape": shape,
        "resolution": resolution,
        "spatial_data": spatial_data,
        "cell_count": shape[0] * shape[1],
    }

    return module_data


def create_test_experiment_data(
    num_runs: int = 5, num_steps: int = 10, seed: Optional[int] = None
) -> Dict[str, Any]:
    """Create standardized test experiment data.

    Args:
        num_runs: Number of experiment runs.
        num_steps: Number of steps per run.
        seed: Optional random seed for reproducibility.

    Returns:
        Dictionary with experiment data.
    """
    if seed is not None:
        np.random.seed(seed)

    experiment_data = {"num_runs": num_runs, "num_steps": num_steps, "runs": []}

    for run in range(num_runs):
        run_data = {"run_id": f"run_{run}", "steps": []}

        for step in range(num_steps):
            step_data = {
                "step": step,
                "agent_count": np.random.randint(80, 120),
                "temperature_mean": np.random.uniform(20, 30),
                "resource_mean": np.random.uniform(60, 90),
            }
            run_data["steps"].append(step_data)

        experiment_data["runs"].append(run_data)

    return experiment_data


def create_test_performance_data(
    operation_name: str,
    execution_times: List[float],
    memory_usage: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Create standardized test performance data.

    Args:
        operation_name: Name of the operation.
        execution_times: List of execution times in seconds.
        memory_usage: Optional list of memory usage in bytes.

    Returns:
        Dictionary with performance data.
    """
    performance_data = {
        "operation": operation_name,
        "execution_times": execution_times,
        "mean_time": np.mean(execution_times),
        "std_time": np.std(execution_times),
        "min_time": np.min(execution_times),
        "max_time": np.max(execution_times),
    }

    if memory_usage is not None:
        performance_data.update(
            {
                "memory_usage": memory_usage,
                "mean_memory": np.mean(memory_usage),
                "std_memory": np.std(memory_usage),
                "min_memory": np.min(memory_usage),
                "max_memory": np.max(memory_usage),
            }
        )

    return performance_data


def create_test_fixture_data() -> Dict[str, Any]:
    """Create comprehensive test fixture data.

    Returns:
        Dictionary with all test fixture data.
    """
    fixture_data = {
        "grid_sizes": {
            "small": SMALL_GRID_SIZE,
            "medium": MEDIUM_GRID_SIZE,
            "large": LARGE_GRID_SIZE,
        },
        "agent_counts": {
            "small": SMALL_AGENT_COUNT,
            "medium": MEDIUM_AGENT_COUNT,
            "large": LARGE_AGENT_COUNT,
        },
        "test_configs": {
            "small": create_test_config("small_test", 50),
            "medium": create_test_config("medium_test", 100),
            "large": create_test_config("large_test", 200),
        },
        "spatial_data": {
            "small": create_test_spatial_data(SMALL_GRID_SIZE),
            "medium": create_test_spatial_data(MEDIUM_GRID_SIZE),
            "large": create_test_spatial_data(LARGE_GRID_SIZE),
        },
        "agent_data": {
            "small": create_test_agent_data(SMALL_AGENT_COUNT),
            "medium": create_test_agent_data(MEDIUM_AGENT_COUNT),
            "large": create_test_agent_data(LARGE_AGENT_COUNT),
        },
    }

    return fixture_data


def save_test_data_to_file(data: Any, filepath: Path, format: str = "npy") -> None:
    """Save test data to file.

    Args:
        data: Data to save.
        filepath: Path to save the data.
        format: Format to save in ("npy", "npz", "json").
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if format == "npy":
        np.save(filepath, data)
    elif format == "npz":
        np.savez(filepath, **data)
    elif format == "json":
        import json

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_test_data_from_file(filepath: Path, format: str = "npy") -> Any:
    """Load test data from file.

    Args:
        filepath: Path to load the data from.
        format: Format to load from ("npy", "npz", "json").

    Returns:
        Loaded data.
    """
    if format == "npy":
        return np.load(filepath)
    elif format == "npz":
        return np.load(filepath)
    elif format == "json":
        import json

        with open(filepath, "r") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported format: {format}")


# Pre-defined test datasets
SMALL_TEST_DATA = create_test_fixture_data()["spatial_data"]["small"]
MEDIUM_TEST_DATA = create_test_fixture_data()["spatial_data"]["medium"]
LARGE_TEST_DATA = create_test_fixture_data()["spatial_data"]["large"]

SMALL_AGENT_DATA = create_test_agent_data(SMALL_AGENT_COUNT)
MEDIUM_AGENT_DATA = create_test_agent_data(MEDIUM_AGENT_COUNT)
LARGE_AGENT_DATA = create_test_agent_data(LARGE_AGENT_COUNT)


# Test data validation functions
def validate_test_data(data: Any, data_type: str) -> bool:
    """Validate test data.

    Args:
        data: Data to validate.
        data_type: Type of data expected.

    Returns:
        True if data is valid, False otherwise.
    """
    if data_type == "raster":
        return isinstance(data, np.ndarray) and len(data.shape) == 2
    elif data_type == "agent":
        return isinstance(data, dict) and "unique_id" in data
    elif data_type == "config":
        return isinstance(data, dict) and "model" in data
    else:
        return True


def get_test_data_info(data: Any) -> Dict[str, Any]:
    """Get information about test data.

    Args:
        data: Data to analyze.

    Returns:
        Dictionary with data information.
    """
    info = {"type": type(data).__name__, "size": None, "shape": None, "dtype": None}

    if isinstance(data, np.ndarray):
        info.update({"size": data.size, "shape": data.shape, "dtype": str(data.dtype)})
    elif isinstance(data, (list, tuple)):
        info["size"] = len(data)
    elif isinstance(data, dict):
        info["size"] = len(data)
        info["keys"] = list(data.keys())

    return info
