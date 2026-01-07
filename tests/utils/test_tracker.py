#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for tracker factory and default tracker."""

from __future__ import annotations

from unittest.mock import MagicMock

from omegaconf import OmegaConf

from abses.utils.tracker.default import DefaultTracker
from abses.utils.tracker.factory import (
    create_tracker,
    prepare_tracker_run_name,
    prepare_tracker_tags,
    start_tracker_run,
)


def test_create_tracker_default() -> None:
    """Default tracker is returned when backend not set."""
    tracker = create_tracker(OmegaConf.create({}), model=None)
    assert isinstance(tracker, DefaultTracker)


def test_create_tracker_unknown_backend_fallback() -> None:
    """Unknown backend should fall back to default."""
    tracker = create_tracker(OmegaConf.create({"backend": "unknown"}), model=None)
    assert isinstance(tracker, DefaultTracker)


# --- Tests for prepare_tracker_run_name ---


def test_prepare_tracker_run_name_default_with_run_id() -> None:
    """Default run name includes model name and run id."""
    cfg = OmegaConf.create({})
    run_name = prepare_tracker_run_name(cfg, "TestModel", "1.0.0", 42)
    assert run_name == "TestModel_run_42"


def test_prepare_tracker_run_name_default_without_run_id() -> None:
    """Default run name is model name when no run id."""
    cfg = OmegaConf.create({})
    run_name = prepare_tracker_run_name(cfg, "TestModel", "1.0.0", None)
    assert run_name == "TestModel"


def test_prepare_tracker_run_name_custom_template() -> None:
    """Custom run name template is formatted correctly."""
    cfg = OmegaConf.create({"run_name": "{model_name}_v{version}_{run_id}"})
    run_name = prepare_tracker_run_name(cfg, "TestModel", "1.0.0", 5)
    assert run_name == "TestModel_v1.0.0_5"


def test_prepare_tracker_run_name_invalid_template() -> None:
    """Invalid template returns template as-is."""
    cfg = OmegaConf.create({"run_name": "{invalid_key}_test"})
    run_name = prepare_tracker_run_name(cfg, "TestModel", "1.0.0", 1)
    assert run_name == "{invalid_key}_test"


# --- Tests for prepare_tracker_tags ---


def test_prepare_tracker_tags_default() -> None:
    """Default tags include model and version."""
    cfg = OmegaConf.create({})
    tags = prepare_tracker_tags(cfg, "TestModel", "1.0.0", None)
    assert tags == {"model": "TestModel", "version": "1.0.0"}


def test_prepare_tracker_tags_default_with_run_id() -> None:
    """Default tags include run_id when provided."""
    cfg = OmegaConf.create({})
    tags = prepare_tracker_tags(cfg, "TestModel", "1.0.0", 42)
    assert tags == {"model": "TestModel", "version": "1.0.0", "run_id": "42"}


def test_prepare_tracker_tags_custom() -> None:
    """Custom tags are returned from config."""
    cfg = OmegaConf.create({"tags": {"env": "test", "project": "demo"}})
    tags = prepare_tracker_tags(cfg, "TestModel", "1.0.0", None)
    assert tags == {"env": "test", "project": "demo"}


def test_prepare_tracker_tags_with_template() -> None:
    """Tags with template variables are formatted."""
    cfg = OmegaConf.create({"tags": {"model_tag": "{model_name}", "run": "{run_id}"}})
    tags = prepare_tracker_tags(cfg, "TestModel", "1.0.0", 99)
    assert tags == {"model_tag": "TestModel", "run": "99"}


# --- Tests for start_tracker_run ---


def test_start_tracker_run_with_none_tracker() -> None:
    """start_tracker_run does nothing when tracker is None."""
    # Should not raise any error
    start_tracker_run(
        tracker=None,
        tracker_cfg=OmegaConf.create({}),
        model_name="TestModel",
        version="1.0.0",
        run_id=1,
        model_params=OmegaConf.create({"param1": 1}),
    )


def test_start_tracker_run_calls_start_run() -> None:
    """start_tracker_run calls tracker.start_run with correct args."""
    mock_tracker = MagicMock()
    mock_tracker.log_params = MagicMock()

    start_tracker_run(
        tracker=mock_tracker,
        tracker_cfg=OmegaConf.create({}),
        model_name="TestModel",
        version="1.0.0",
        run_id=1,
        model_params=OmegaConf.create({"param1": 1}),
    )

    mock_tracker.start_run.assert_called_once()
    call_kwargs = mock_tracker.start_run.call_args[1]
    assert call_kwargs["run_name"] == "TestModel_run_1"
    assert "model" in call_kwargs["tags"]


def test_start_tracker_run_logs_params_dict() -> None:
    """start_tracker_run logs params as dict for non-Aim trackers."""
    mock_tracker = MagicMock()
    mock_tracker.log_params = MagicMock()
    # Ensure type name is not "AimTracker"
    type(mock_tracker).__name__ = "MockTracker"

    model_params = OmegaConf.create({"param1": 1, "param2": "value"})

    start_tracker_run(
        tracker=mock_tracker,
        tracker_cfg=OmegaConf.create({"log_params": True}),
        model_name="TestModel",
        version="1.0.0",
        run_id=1,
        model_params=model_params,
    )

    mock_tracker.log_params.assert_called_once()
    logged_params = mock_tracker.log_params.call_args[0][0]
    # Should be a plain dict, not DictConfig
    assert isinstance(logged_params, dict)
    assert logged_params["param1"] == 1
    assert logged_params["param2"] == "value"


def test_start_tracker_run_logs_params_disabled() -> None:
    """start_tracker_run does not log params when disabled."""
    mock_tracker = MagicMock()
    mock_tracker.log_params = MagicMock()

    start_tracker_run(
        tracker=mock_tracker,
        tracker_cfg=OmegaConf.create({"log_params": False}),
        model_name="TestModel",
        version="1.0.0",
        run_id=1,
        model_params=OmegaConf.create({"param1": 1}),
    )

    mock_tracker.log_params.assert_not_called()


def test_start_tracker_run_aim_tracker_with_dictconfig() -> None:
    """AimTracker receives DictConfig directly for log_params."""

    class FakeAimTracker:
        """Fake AimTracker to test type name checking."""

        def __init__(self):
            self.start_run_called = False
            self.logged_params = None

        def start_run(self, run_name=None, tags=None):
            self.start_run_called = True

        def log_params(self, params):
            self.logged_params = params

    # Rename the class to "AimTracker" for the type check
    FakeAimTracker.__name__ = "AimTracker"
    fake_tracker = FakeAimTracker()

    model_params = OmegaConf.create({"param1": 1, "nested": {"key": "value"}})

    start_tracker_run(
        tracker=fake_tracker,
        tracker_cfg=OmegaConf.create({"log_params": True}),
        model_name="TestModel",
        version="1.0.0",
        run_id=1,
        model_params=model_params,
    )

    # AimTracker should receive the DictConfig directly
    assert fake_tracker.logged_params is model_params
    from omegaconf import DictConfig

    assert isinstance(fake_tracker.logged_params, DictConfig)
