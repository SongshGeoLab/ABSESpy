#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

import statistics
from typing import Any, Dict

from abses.utils.tracker import TrackerProtocol

try:
    from aim import Run
except ImportError:
    Run = None


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

        Raises:
            ImportError: If aim is not installed.
        """
        if Run is None:
            raise ImportError(
                "Aim is not installed. Install with: pip install abses[aim] or pip install aim"
            )
        experiment = config.get("experiment", None)
        repo = config.get("repo", None)
        self._run = Run(experiment=experiment, repo=repo)
        self._params_logged = False

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

        Args:
            breed: Agent breed/class name.
            agent_vars: Dictionary of variable names to values (can be lists for aggregation).
            step: Step number (optional).
        """
        # Handle list values (aggregated agent data)
        metrics_to_log: Dict[str, float] = {}
        for key, value in agent_vars.items():
            metric_name = f"{breed}.{key}"
            if isinstance(value, (int, float)):
                metrics_to_log[metric_name] = value
            elif isinstance(value, list) and value:
                # Aggregate list values (mean, min, max)
                numeric_values = [v for v in value if isinstance(v, (int, float))]
                if numeric_values:
                    metrics_to_log[f"{metric_name}.mean"] = statistics.mean(
                        numeric_values
                    )
                    metrics_to_log[f"{metric_name}.min"] = min(numeric_values)
                    metrics_to_log[f"{metric_name}.max"] = max(numeric_values)
                    if len(numeric_values) > 1:
                        metrics_to_log[f"{metric_name}.std"] = statistics.stdev(
                            numeric_values
                        )

        if metrics_to_log:
            self.log_metrics(metrics_to_log, step=step)

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

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log hyperparameters to Aim.

        Args:
            params: Dictionary of parameter names to values.
        """
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
