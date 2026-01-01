#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Integration tests for MainModel configuration validation."""

from __future__ import annotations

import pytest
from omegaconf import OmegaConf

from abses import MainModel
from abses.utils.errors import ConfigurationError


def test_main_model_validation_strict_raises() -> None:
    """Strict validation should raise on invalid config."""
    cfg = OmegaConf.create(
        {
            "exp": {"repeats": 0},
            "tracker": {"model": {"m": 123}},
        }
    )
    validate_cfg = OmegaConf.create({"enabled": True, "strict": True})
    cfg.validate = validate_cfg
    with pytest.raises(ConfigurationError):
        MainModel(parameters=cfg)


def test_main_model_normalizes_reports() -> None:
    """reports should be accepted and normalized to tracker."""
    cfg = OmegaConf.create(
        {
            "reports": {"model": {"n_agents": "n_agents"}},
            "time": {"end": 1},
        }
    )
    model = MainModel(parameters=cfg)
    assert "n_agents" in model.datacollector.model_reporters
