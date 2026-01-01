#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from typing import Any, Dict

from abses.utils.tracker import TrackerProtocol


class DefaultTracker(TrackerProtocol):
    """No-op tracker that keeps current in-memory behavior."""

    def start_run(
        self, run_name: str | None = None, tags: Dict[str, str] | None = None
    ) -> None:
        """Start run (no-op)."""

    def log_metrics(self, metrics: Dict[str, float], step: int | None = None) -> None:
        """Log metrics (no-op)."""

    def log_model_vars(
        self, model_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log model variables (no-op)."""

    def log_agent_vars(
        self, breed: str, agent_vars: Dict[str, Any], step: int | None = None
    ) -> None:
        """Log agent variables (no-op)."""

    def log_final_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log final metrics (no-op)."""

    def end_run(self) -> None:
        """End run (no-op)."""
