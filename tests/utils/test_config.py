#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for configuration normalization and validation."""

from __future__ import annotations

import pytest
from omegaconf import OmegaConf

from abses.utils.config import (
    normalize_config,
    validate_config,
)
from abses.utils.errors import ConfigurationError


def test_normalize_reports_to_tracker() -> None:
    """reports should be normalized to tracker."""
    cfg = OmegaConf.create({"reports": {"model": {"a": "a"}, "agent": {"X": {}}}})
    normalized = normalize_config(cfg)
    assert "tracker" in normalized
    assert "agent" not in normalized.tracker
    assert "agents" in normalized.tracker
    assert normalized.tracker.model.a == "a"


def test_validate_time_section() -> None:
    """Invalid time section should produce errors."""
    cfg = OmegaConf.create({"time": {"start": 123, "end": {"bad": "x"}}})
    errors = validate_config(cfg, strict=False)
    assert any("time.start" in err for err in errors)
    assert any("time.end" in err for err in errors)


def test_validate_exp_section() -> None:
    """Invalid exp section should produce errors."""
    cfg = OmegaConf.create(
        {"exp": {"repeats": -1, "seed": "bad", "logging": "invalid"}}
    )
    errors = validate_config(cfg, strict=False)
    assert any("exp.repeats" in err for err in errors)
    assert any("exp.seed" in err for err in errors)
    assert any("exp.logging" in err for err in errors)


def test_validate_model_range() -> None:
    """Model range should enforce numeric and ordering."""
    cfg = OmegaConf.create({"model": {"density": {"min": 1.0, "max": 0.5, "step": -1}}})
    errors = validate_config(cfg, strict=False)
    assert any("min should be < max" in err for err in errors)
    assert any("step: must be > 0" in err for err in errors)


def test_validate_tracker_section() -> None:
    """Tracker validation should capture invalid entries."""
    cfg = OmegaConf.create(
        {
            "tracker": {
                "backend": "unknown",
                "model": {"m": 123},
                "agents": {"X": "bad"},
                "final": {"f": {"aggregate": "invalid"}},
            }
        }
    )
    errors = validate_config(cfg, strict=False)
    assert any("tracker.backend" in err for err in errors)
    assert any("tracker.model.m" in err for err in errors)
    assert any("tracker.agents.X" in err for err in errors)
    assert any("aggregate" in err for err in errors)


def test_validate_strict_raises() -> None:
    """Strict validation should raise ConfigurationError."""
    cfg = OmegaConf.create({"exp": {"repeats": 0}})
    with pytest.raises(ConfigurationError):
        validate_config(cfg, strict=True)
