#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from typing import Any, Dict, Protocol


class TrackerProtocol(Protocol):
    """Protocol for tracker backends."""

    def start_run(
        self, run_name: str | None = None, tags: Dict[str, str] | None = None
    ) -> None:
        """Start a tracking run."""

    def log_metrics(self, metrics: Dict[str, float], step: int | None = None) -> None:
        """Log scalar metrics."""

    def log_model_vars(
        self, model_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log model-level variables."""

    def log_agent_vars(
        self, breed: str, agent_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log agent-level variables."""

    def log_final_metrics(
        self, metrics: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log final metrics."""

    def end_run(self) -> None:
        """End the tracking run."""
