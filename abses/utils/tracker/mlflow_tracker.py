#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from typing import Any, Dict

from abses.utils.tracker import TrackerProtocol

try:
    import mlflow
except ImportError:
    mlflow = None


class MLflowTracker(TrackerProtocol):
    """MLflow tracker backend (requires `mlflow`)."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize MLflow tracker.

        Args:
            config: MLflow-specific configuration.

        Raises:
            ImportError: If mlflow is not installed.
        """
        if mlflow is None:
            raise ImportError(
                "MLflow is not installed. Install with: pip install mlflow"
            )
        self._experiment = config.get("experiment", None)
        self._run = None

    def start_run(
        self, run_name: str | None = None, tags: Dict[str, str] | None = None
    ) -> None:
        """Start MLflow run."""
        if self._experiment:
            mlflow.set_experiment(self._experiment)
        self._run = mlflow.start_run(run_name=run_name)
        if tags:
            mlflow.set_tags(tags)

    def log_metrics(self, metrics: Dict[str, float], step: int | None = None) -> None:
        """Log metrics to MLflow."""
        mlflow.log_metrics(metrics, step=step)

    def log_model_vars(
        self, model_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log model variables as metrics."""
        float_metrics = {
            k: v for k, v in model_vars.items() if isinstance(v, (int, float))
        }
        if float_metrics:
            self.log_metrics(float_metrics, step=step)

    def log_agent_vars(
        self, breed: str, agent_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log agent variables with breed prefix."""
        float_metrics = {
            f"{breed}.{k}": v
            for k, v in agent_vars.items()
            if isinstance(v, (int, float))
        }
        if float_metrics:
            self.log_metrics(float_metrics, step=step)

    def log_final_metrics(
        self, metrics: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log final metrics."""
        self.log_metrics({f"final.{k}": v for k, v in metrics.items()})

    def end_run(self) -> None:
        """End MLflow run."""
        if self._run is not None:
            mlflow.end_run()
            self._run = None
