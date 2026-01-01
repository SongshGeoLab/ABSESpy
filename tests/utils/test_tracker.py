#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for tracker factory and default tracker."""

from __future__ import annotations

from omegaconf import OmegaConf

from abses.utils.tracker.default import DefaultTracker
from abses.utils.tracker.factory import create_tracker


def test_create_tracker_default() -> None:
    """Default tracker is returned when backend not set."""
    tracker = create_tracker(OmegaConf.create({}), model=None)
    assert isinstance(tracker, DefaultTracker)


def test_create_tracker_unknown_backend_fallback() -> None:
    """Unknown backend should fall back to default."""
    tracker = create_tracker(OmegaConf.create({"backend": "unknown"}), model=None)
    assert isinstance(tracker, DefaultTracker)
