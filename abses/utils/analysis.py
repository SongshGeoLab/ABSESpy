#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Analysis utilities for Hydra multirun experiment results.

This module provides tools for analyzing and aggregating results from
Hydra multirun experiments, including reading configurations, loading
data files, and performing data aggregation.
"""

from __future__ import annotations

import logging
from functools import cached_property, lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List

import pandas as pd
import yaml  # type: ignore[import-untyped]
from omegaconf import DictConfig, ListConfig, OmegaConf

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

if TYPE_CHECKING:
    pass

PathLike: TypeAlias = str | Path

logger = logging.getLogger(__name__)


class _BaseAnalyzer:
    """Base analyzer class for experiment results.

    Provides basic functionality for path management, configuration reading,
    and value selection from Hydra configuration files.

    Attributes:
        path: Path to the experiment directory.
        config: Loaded configuration from YAML file.
    """

    def __init__(self, path: PathLike) -> None:
        """Initialize the base analyzer.

        Args:
            path: Path to the experiment directory or configuration file.
        """
        self.path = path

    @property
    def path(self) -> Path:
        """Path to the experiment directory.

        Returns:
            Path object pointing to the experiment directory.
        """
        return self._path

    @path.setter
    def path(self, path: PathLike) -> None:
        """Set the path property.

        Args:
            path: Path string or Path object to set.
        """
        path = Path(path)
        self._path = path

    @property
    def config(self) -> DictConfig | ListConfig:
        """Configuration loaded from YAML file.

        Returns:
            DictConfig or ListConfig object containing the configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        if not hasattr(self, "_config"):
            raise AttributeError("Configuration has not been loaded yet.")
        return self._config

    @config.setter
    def config(self, yaml_file_path: PathLike) -> None:
        """Load configuration from a YAML file.

        Args:
            yaml_file_path: Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        yaml_file_path = Path(yaml_file_path)
        if not yaml_file_path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {yaml_file_path}")
        self._config = OmegaConf.load(yaml_file_path)

    @cached_property
    def subdir(self) -> List[Path]:
        """List of subdirectories in the experiment path.

        Returns:
            List of Path objects for subdirectories.
        """
        if not self.path.is_dir():
            return []
        return [dir_path for dir_path in self.path.iterdir() if dir_path.is_dir()]

    def select(self, key: str) -> Any:
        """Select a value from the configuration using OmegaConf select.

        Args:
            key: Configuration key path (e.g., "model.density").

        Returns:
            The value at the specified key path.

        Raises:
            AttributeError: If the key is not found in the configuration.
        """
        return OmegaConf.select(self.config, key=key)


class ResultAnalyzer(_BaseAnalyzer):
    """Analyzer for a single Hydra run result.

    This class analyzes the output of a single Hydra experiment run,
    including reading configuration, loading data files, and extracting
    reporter information.

    Attributes:
        data: Raw data loaded from CSV or datacollector output.
        configs: Full configuration dictionary.
        model_reporter: Model-level reporter configuration.
        agent_reporter: Agent-level reporter configuration.
        final_reporter: Final reporter configuration.
    """

    def __init__(self, path: PathLike) -> None:
        """Initialize the result analyzer.

        Args:
            path: Path to the single run output directory.

        Raises:
            FileNotFoundError: If the path is not a valid directory.
        """
        # Initialize attributes
        self.configs: Dict[str, Any] = {}
        self.model_reporter: Dict[str, Any] = {}
        self.agent_reporter: Dict[str, Dict[str, Any]] = {}
        self.final_reporter: Dict[str, Any] = {}

        super().__init__(path=path)
        if not self.path.is_dir():
            raise FileNotFoundError(f"{path} is not a directory.")
        self._hydra = self.path / ".hydra"
        if self._hydra.is_dir():
            self.config = self._hydra / "config.yaml"
            self._load_hydra_cfg(self._hydra)
        else:
            # If no .hydra directory, try to find config.yaml in the path
            config_path = self.path / "config.yaml"
            if config_path.is_file():
                self.config = config_path
                self._load_hydra_cfg(self.path)
            else:
                raise FileNotFoundError(
                    f"No configuration found in {path}. Expected .hydra/config.yaml or config.yaml"
                )
        self.read_data()

    @property
    def data(self) -> pd.DataFrame:
        """Raw data loaded from CSV or datacollector output.

        Returns:
            DataFrame containing the raw data.

        Raises:
            AttributeError: If data has not been loaded yet.
        """
        if not hasattr(self, "_data"):
            raise AttributeError(
                "Data has not been loaded yet. Call read_data() first."
            )
        return self._data

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        """Set the data property.

        Args:
            data: DataFrame to set as the data.

        Raises:
            TypeError: If data is not a DataFrame.
        """
        self._check_data(data)
        self._data = data

    @staticmethod
    def _check_data(data: pd.DataFrame) -> None:
        """Check if data is a valid DataFrame.

        Args:
            data: Data to check.

        Raises:
            TypeError: If data is not a DataFrame.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"{type(data)} is not a DataFrame.")

    def _load_hydra_cfg(self, path: PathLike) -> None:
        """Load Hydra configuration and extract reporter information.

        Args:
            path: Path to the directory containing config.yaml.
        """
        config_path = Path(path) / "config.yaml"
        if not config_path.is_file():
            # Try alternative locations
            config_path = Path(path).parent / "config.yaml"
            if not config_path.is_file():
                logger.warning(f"Could not find config.yaml in {path}")
                self.configs = {}
                self.model_reporter = {}
                self.agent_reporter = {}
                self.final_reporter = {}
                return

        with open(config_path, "r", encoding="utf-8") as f:
            loaded_configs = yaml.safe_load(f)
            self.configs = loaded_configs if loaded_configs is not None else {}

        # Extract reporter information (support both 'reports' and 'tracker')
        reporters: Dict[str, Any] = self.configs.get("reports", {}) or self.configs.get(
            "tracker", {}
        )
        self.model_reporter = reporters.get("model", {})
        self.agent_reporter = reporters.get("agents", {})
        self.final_reporter = reporters.get("final", {})

    def read_data(self) -> None:
        """Read data from CSV files or datacollector output.

        This method attempts to find and load data files in the following order:
        1. Common CSV filenames (cities.csv, 1_cities.csv, etc.)
        2. Datacollector output files if available
        3. User-specified files

        Raises:
            FileNotFoundError: If no data file is found.
        """
        # Try common CSV filenames
        common_names = ["cities.csv", "1_cities.csv", "data.csv", "results.csv"]
        for name in common_names:
            csv_path = self.path / name
            if csv_path.is_file():
                self.data = self.read_csv(csv_path)
                logger.info(f"Loaded data from {csv_path}.")
                return

        # Try to find any CSV file in the directory
        csv_files = list(self.path.glob("*.csv"))
        if csv_files:
            # Use the first CSV file found
            self.data = self.read_csv(csv_files[0])
            logger.info(f"Loaded data from {csv_files[0]}.")
            return

        # If no CSV found, try to load from datacollector output
        # This would require the datacollector to have saved its output
        # For now, we'll raise an error
        raise FileNotFoundError(
            f"No data file found in {self.path}. "
            f"Expected CSV files or datacollector output."
        )

    def read_csv(self, path: PathLike) -> pd.DataFrame:
        """Read a CSV file into a DataFrame.

        Args:
            path: Path to the CSV file.

        Returns:
            DataFrame containing the CSV data.

        Raises:
            FileNotFoundError: If the file does not exist or is invalid.
        """
        if isinstance(path, str):
            path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"CSV file not found: {path}")
        if path.suffix != ".csv":
            raise FileNotFoundError(f"File is not a CSV: {path}")

        # Try reading with index_col=0, fallback to no index
        try:
            return pd.read_csv(path, index_col=0)
        except (ValueError, IndexError):
            return pd.read_csv(path)

    @lru_cache(maxsize=1)
    def get_data(self, **kwargs: Any) -> pd.DataFrame:
        """Get processed data with optional transformations.

        This method can be overridden or extended to support different
        aggregation levels or data transformations.

        Args:
            **kwargs: Additional arguments for data processing.

        Returns:
            Processed DataFrame.
        """
        return self.data.copy()

    def select(self, key: str) -> Any:
        """Select a value from the configuration.

        Args:
            key: Configuration key path.

        Returns:
            The value at the specified key path.
        """
        return OmegaConf.select(self.config, key=key)


class ExpAnalyzer(_BaseAnalyzer):
    """Analyzer for a group of Hydra multirun experiment results.

    This class analyzes multiple experiment runs from a Hydra multirun,
    including parsing configuration overrides, aggregating data, and
    comparing differences between runs.

    Attributes:
        overrides: Dictionary of configuration overrides from multirun.yaml.
        results: Generator yielding ResultAnalyzer for each run.
    """

    def __init__(self, path: PathLike, enable_logger: bool = True) -> None:
        """Initialize the experiment analyzer.

        Args:
            path: Path to the multirun output directory.
            enable_logger: Whether to enable logging (default: True).
        """
        super().__init__(path=path)
        multirun_config = self.path / "multirun.yaml"
        if multirun_config.is_file():
            self.config = multirun_config
        else:
            # Try alternative location
            multirun_config = self.path.parent / "multirun.yaml"
            if multirun_config.is_file():
                self.config = multirun_config
            else:
                if enable_logger:
                    logger.warning(
                        f"multirun.yaml not found in {self.path}. "
                        f"Some features may not work correctly."
                    )
                # Create an empty config
                self._config = OmegaConf.create({})

    @property
    def overrides(self) -> Dict[str, List[str]]:
        """Configuration overrides from multirun.yaml.

        Parses the hydra.overrides.task section to extract parameter
        overrides and their values.

        Returns:
            Dictionary mapping parameter names to lists of values.
        """
        try:
            overrides_lst = OmegaConf.select(self.config, "hydra.overrides.task")
            if overrides_lst is None:
                return {}

            # Convert OmegaConf object to native Python types
            if hasattr(OmegaConf, "to_container"):
                overrides_lst = OmegaConf.to_container(overrides_lst, resolve=True)

            if not isinstance(overrides_lst, (list, tuple)):
                overrides_lst = [overrides_lst]

            result: Dict[str, List[str]] = {}
            for override in overrides_lst:
                # Convert to string and handle different formats
                override_str = str(override).strip()

                # Remove list brackets if present
                if override_str.startswith("[") and override_str.endswith("]"):
                    override_str = override_str[1:-1]
                if "=" not in override_str:
                    continue

                key, value = override_str.split("=", 1)
                # Strip key and remove quotes
                key = key.strip().strip("'\"")
                # Handle comma-separated values
                values = [v.strip().strip("'\"") for v in value.split(",")]
                if key:  # Only add if key is not empty
                    result[key] = values
            return result
        except Exception as e:
            logger.warning(f"Failed to parse overrides: {e}")
            return {}

    @property
    def results(self) -> Generator[ResultAnalyzer, None, None]:
        """Generator yielding ResultAnalyzer for each run.

        Yields:
            ResultAnalyzer instance for each subdirectory in the multirun output.
        """
        for subdir in self.subdir:
            try:
                yield ResultAnalyzer(subdir)
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Skipping {subdir}: {e}")
                continue

    @cached_property
    def _results_list(self) -> List[ResultAnalyzer]:
        """Cached list of ResultAnalyzer instances.

        This property caches the results to avoid generator exhaustion
        when results are accessed multiple times.
        """
        return list(self.results)

    @cached_property
    def diff_runs(self) -> pd.DataFrame:
        """DataFrame showing configuration differences between runs.

        Returns:
            DataFrame with columns for each override parameter and rows
            for each run, showing the actual values used.

        Raises:
            NotImplementedError: If unexpected configuration values are found.
        """
        runs: Dict[str, List[str]] = {}
        for key, expected_values in self.overrides.items():
            if len(expected_values) <= 1:
                continue
            values = []
            for res in self._results_list:
                try:
                    value = res.select(key)
                    if value is None:
                        values.append("")
                    else:
                        values.append(str(value))
                except Exception as e:
                    logger.warning(f"Failed to select {key} from {res.path}: {e}")
                    values.append("")

            # Only validate if we have non-empty values
            non_empty_values = [v for v in values if v]
            if non_empty_values:
                # Convert expected values to strings for comparison
                expected_str = [str(v) for v in expected_values]
                unexpected_values = set(non_empty_values) - set(expected_str)
                if unexpected_values:
                    raise NotImplementedError(
                        f"Some unexpected config values {unexpected_values} in '{key}'."
                    )
            # Always add the key, even if all values are empty
            runs[key] = values

        if not runs:
            return pd.DataFrame()
        return pd.DataFrame(runs)

    @cached_property
    def agg_data(self) -> pd.DataFrame:
        """Aggregated data from all runs.

        This property aggregates data from all runs and adds configuration
        override columns to identify each run.

        Returns:
            DataFrame containing aggregated data from all runs.

        Note:
            This is a cached property. To refresh, delete the attribute
            or use a new instance.
        """
        datasets: List[pd.DataFrame] = []
        for res in self._results_list:
            try:
                data = res.get_data()
                # Add override columns
                for key in self.overrides:
                    try:
                        value = res.select(key)
                        if value is not None:
                            data[key] = value
                    except Exception:
                        # If key not found, skip
                        pass
                datasets.append(data)
            except Exception as e:
                logger.warning(f"Failed to get data from {res.path}: {e}")
                continue

        if not datasets:
            return pd.DataFrame()
        return pd.concat(datasets, ignore_index=True)

    def apply(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> pd.Series:
        """Apply a function to each run's ResultAnalyzer.

        Args:
            func: Function to apply. Should accept ResultAnalyzer as first argument.
            *args: Additional positional arguments for the function.
            **kwargs: Additional keyword arguments for the function.

        Returns:
            Series with results from applying the function to each run.
        """
        results = []
        for run in self._results_list:
            try:
                result = func(run, *args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to apply {func.__name__} to {run.path}: {e}")
                results.append(None)

        return pd.Series(results, name=func.__name__)
