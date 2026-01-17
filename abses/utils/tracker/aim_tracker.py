#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from typing import Any, Dict

from abses.utils.tracker import TrackerProtocol

try:
    from omegaconf import DictConfig, OmegaConf
except ImportError:
    DictConfig = None
    OmegaConf = None

try:
    from aim import Distribution, Run
except ImportError:
    Run = None
    Distribution = None


class AimTracker(TrackerProtocol):
    """Aim tracker backend (requires `aim`).

    This tracker integrates with Aim (https://aimstack.io/) for experiment tracking.
    Install with: pip install abses[aim] or pip install aim

    Example configuration:
        tracker:
          backend: aim
          aim:
            experiment: "my_experiment"
            repo: "./aim_repo"  # Optional, defaults to ~/.aim
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Aim tracker.

        Args:
            config: Aim-specific configuration dictionary. Supported keys:
                - experiment: Experiment name (optional)
                - repo: Path to Aim repository (optional, defaults to ~/.aim)
                - distribution_bin_count: Number of bins for Distribution (optional, default 64, range 1-512)
                - log_categorical_stats: Whether to log categorical statistics (optional, default True)

        Raises:
            ImportError: If aim is not installed.
        """
        if Run is None or Distribution is None:
            raise ImportError(
                "Aim is not installed. Install with: pip install abses[aim] or pip install aim"
            )
        experiment = config.get("experiment", None)
        repo = config.get("repo", None)
        self._run = Run(experiment=experiment, repo=repo)
        self._params_logged = False

        # Distribution configuration
        bin_count = config.get("distribution_bin_count", 64)
        if not isinstance(bin_count, int) or bin_count < 1 or bin_count > 512:
            raise ValueError(
                f"distribution_bin_count must be an integer between 1 and 512, got {bin_count}"
            )
        self._bin_count = bin_count
        self._log_categorical_stats = config.get("log_categorical_stats", True)

    def start_run(
        self, run_name: str | None = None, tags: Dict[str, str] | None = None
    ) -> None:
        """Start a tracking run.

        Args:
            run_name: Name for this run (optional).
            tags: Dictionary of tags to add to the run (optional).
        """
        if run_name:
            self._run.name = run_name
        if tags:
            for key, value in tags.items():
                self._run.add_tag(f"{key}:{value}")

    def log_metrics(self, metrics: Dict[str, float], step: int | None = None) -> None:
        """Log scalar metrics to Aim.

        Args:
            metrics: Dictionary of metric names to values.
            step: Step number (optional).
        """
        for name, value in metrics.items():
            # Only track numeric values as metrics
            if isinstance(value, (int, float)):
                self._run.track(value, name=name, step=step)

    def log_model_vars(
        self, model_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log model variables as metrics.

        Args:
            model_vars: Dictionary of variable names to values.
            step: Step number (optional).
        """
        # Filter numeric values for metrics
        numeric_vars = {
            k: v for k, v in model_vars.items() if isinstance(v, (int, float))
        }
        if numeric_vars:
            self.log_metrics(numeric_vars, step=step)

    def log_agent_vars(
        self, breed: str, agent_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log agent variables with breed prefix.

        Uses Aim Distribution for numeric variables and frequency statistics for categorical variables.
        Directly uses pandas Series and numpy arrays, leveraging built-in tools for type conversion
        and NaN handling.

        Args:
            breed: Agent breed/class name.
            agent_vars: Dictionary of variable names to values (can be lists, Series, or arrays).
            step: Step number (optional).
        """
        import numpy as np
        import pandas as pd

        for key, value in agent_vars.items():
            metric_name = f"{breed}.{key}"

            # Convert to pandas Series (if not already)
            if isinstance(value, list):
                series = pd.Series(value)
            elif isinstance(value, pd.Series):
                series = value
            elif isinstance(value, np.ndarray):
                series = pd.Series(value)
            elif isinstance(value, (int, float)):
                # Single scalar value
                self._run.track(value, name=metric_name, step=step)
                continue
            else:
                # Other types, try to convert
                try:
                    series = pd.Series(value)
                except (TypeError, ValueError):
                    continue

            # Skip empty Series
            if len(series) == 0:
                continue

            # Handle based on data type
            # Note: Boolean must be checked before numeric, because is_numeric_dtype
            # returns True for boolean types as well.

            # 1. Boolean type -> Convert to 0/1 then use Distribution
            # Check both bool dtype and object dtype with boolean values
            # (pandas converts bool dtype to object when None values are present)
            is_boolean_type = pd.api.types.is_bool_dtype(series) or (
                pd.api.types.is_object_dtype(series)
                and len(series.dropna()) > 0
                and all(isinstance(x, bool) for x in series.dropna())
            )
            if is_boolean_type:
                bool_series = series.dropna()
                if len(bool_series) == 0:
                    continue
                # Convert to 0/1
                numeric_series = bool_series.astype(int)
                if len(numeric_series) == 1:
                    self._run.track(numeric_series.iloc[0], name=metric_name, step=step)
                else:
                    dist = Distribution(
                        samples=numeric_series, bin_count=self._bin_count
                    )
                    self._run.track(dist, name=metric_name, step=step)
                # Additional statistics
                true_count = bool_series.sum()
                self._run.track(true_count, name=f"{metric_name}.true_count", step=step)
                self._run.track(
                    true_count / len(bool_series),
                    name=f"{metric_name}.true_ratio",
                    step=step,
                )

            # 2. Numeric types (int, float) -> Distribution
            elif pd.api.types.is_numeric_dtype(series):
                # Remove NaN (pandas handles automatically)
                numeric_series = series.dropna()
                if len(numeric_series) == 0:
                    continue
                elif len(numeric_series) == 1:
                    # Single value, log as scalar
                    self._run.track(numeric_series.iloc[0], name=metric_name, step=step)
                else:
                    # Multiple values, use Distribution
                    dist = Distribution(
                        samples=numeric_series, bin_count=self._bin_count
                    )
                    self._run.track(dist, name=metric_name, step=step)

            # 3. String type (categorical) -> Use pandas value_counts()
            elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(
                series
            ):
                if not self._log_categorical_stats:
                    continue
                # Remove NaN and empty strings
                str_series = series.dropna()
                str_series = str_series[str_series != ""]
                if len(str_series) == 0:
                    continue

                # Use pandas value_counts() for statistics
                value_counts = str_series.value_counts()
                unique_count = len(value_counts)
                total_count = len(str_series)

                # Log unique count
                self._run.track(
                    unique_count, name=f"{metric_name}.unique_count", step=step
                )

                # Log most common category
                if len(value_counts) > 0:
                    most_common = value_counts.iloc[0]
                    self._run.track(
                        most_common,
                        name=f"{metric_name}.most_common_count",
                        step=step,
                    )
                    self._run.track(
                        most_common / total_count,
                        name=f"{metric_name}.most_common_ratio",
                        step=step,
                    )

                # If category count <= 10, log each category's count
                if unique_count <= 10:
                    for category, count in value_counts.items():
                        # Clean category name (replace special characters)
                        safe_name = str(category).replace(".", "_").replace(" ", "_")
                        self._run.track(
                            count,
                            name=f"{metric_name}.{safe_name}_count",
                            step=step,
                        )

            # 4. Other types: Try to convert to numeric
            else:
                try:
                    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
                    if len(numeric_series) > 0:
                        if len(numeric_series) == 1:
                            self._run.track(
                                numeric_series.iloc[0], name=metric_name, step=step
                            )
                        else:
                            dist = Distribution(
                                samples=numeric_series, bin_count=self._bin_count
                            )
                            self._run.track(dist, name=metric_name, step=step)
                except (TypeError, ValueError):
                    # Cannot convert, skip
                    pass

    def log_final_metrics(
        self, metrics: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log final metrics.

        Args:
            metrics: Dictionary of final metric names to values.
            step: Step number (optional).
        """
        # Filter numeric values
        numeric_metrics = {
            k: v for k, v in metrics.items() if isinstance(v, (int, float))
        }
        if numeric_metrics:
            self.log_metrics(numeric_metrics, step=step)

    def log_params(self, params: Dict[str, Any] | DictConfig) -> None:
        """Log hyperparameters to Aim.

        Args:
            params: Dictionary of parameter names to values, or DictConfig.
        """
        # If params is DictConfig, use Aim's built-in OmegaConf integration
        if DictConfig is not None and isinstance(params, DictConfig):
            self._run["config"] = OmegaConf.to_container(params, resolve=True)
            return

        # Otherwise, handle as regular dict
        for key, value in params.items():
            # Aim supports various types for parameters
            if isinstance(value, (int, float, str, bool)):
                self._run.set(key, value, strict=False)
            elif isinstance(value, (list, tuple)):
                # Convert lists/tuples to strings for Aim
                self._run.set(key, str(value), strict=False)
            else:
                # Convert other types to strings
                self._run.set(key, str(value), strict=False)

    def end_run(self) -> None:
        """End the Aim run."""
        self._run.close()
