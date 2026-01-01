#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : ABSESpy Team
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from omegaconf import DictConfig, OmegaConf

from abses.utils.errors import ConfigurationError
from abses.utils.logging import logger


def normalize_config(config: DictConfig | Dict | None) -> DictConfig:
    """Normalize configuration for backward compatibility.

    This function converts deprecated keys to the new schema while
    preserving original data.

    Args:
        config: Raw configuration (DictConfig, dict, or None).

    Returns:
        Normalized configuration.
    """
    # Handle empty or None config
    if config is None:
        config = DictConfig({})

    if isinstance(config, dict) and not isinstance(config, DictConfig):
        config = OmegaConf.create(config)

    if not isinstance(config, DictConfig):
        raise ConfigurationError("Configuration must be a DictConfig or dict.")

    OmegaConf.set_struct(config, False)
    cfg = config

    # reports -> tracker
    if "reports" in cfg and "tracker" not in cfg:
        cfg.tracker = cfg.reports
        logger.warning(
            "Configuration key 'reports' is deprecated. Please use 'tracker' instead."
        )

    # agent -> agents inside tracker/reports
    tracker_cfg = cfg.get("tracker", {})
    if tracker_cfg and isinstance(tracker_cfg, (dict, DictConfig)):
        # Ensure tracker_cfg is DictConfig for modification
        if not isinstance(tracker_cfg, DictConfig):
            tracker_cfg = OmegaConf.create(tracker_cfg)
            cfg.tracker = tracker_cfg

        if "agent" in tracker_cfg and "agents" not in tracker_cfg:
            tracker_cfg.agents = tracker_cfg.agent
            logger.warning(
                "Configuration key 'tracker.agent' is deprecated. "
                "Please use 'tracker.agents' instead."
            )
            del tracker_cfg["agent"]
    return cfg


def validate_config(config: DictConfig, strict: bool = False) -> List[str]:
    """Validate configuration sections.

    Args:
        config: Normalized configuration.
        strict: Whether to raise on validation errors.

    Returns:
        List of validation error messages.
    """
    errors: List[str] = []
    errors.extend(_validate_time(config.get("time", {})))
    errors.extend(_validate_exp(config.get("exp", {})))
    errors.extend(_validate_model(config.get("model", {})))
    errors.extend(_validate_tracker(config.get("tracker", {})))

    if errors and strict:
        raise ConfigurationError(_format_validation_errors(errors))
    return errors


def _validate_time(time_cfg: Any) -> List[str]:
    """Validate time configuration."""
    errs: List[str] = []
    if not time_cfg:
        return errs
    if not isinstance(time_cfg, (dict, DictConfig)):
        return ["time: must be a mapping."]
    end = time_cfg.get("end", None)
    for key in ("start",):
        val = time_cfg.get(key, None)
        if val is not None and not isinstance(val, (str, datetime)):
            errs.append(f"time.{key}: expected str|datetime|null, got {type(val)}")
    if end is not None and not isinstance(end, (int, str, datetime)):
        errs.append(f"time.end: expected int|str|datetime|null, got {type(end)}")
    for key in ("days", "hours", "minutes", "seconds"):
        val = time_cfg.get(key, 0)
        if val is not None and not isinstance(val, int):
            errs.append(f"time.{key}: expected int, got {type(val)}")
        if isinstance(val, int) and val < 0:
            errs.append(f"time.{key}: must be non-negative, got {val}")
    irregular = time_cfg.get("irregular", False)
    if irregular not in (True, False):
        errs.append("time.irregular: expected bool.")
    return errs


def _validate_exp(exp_cfg: Any) -> List[str]:
    """Validate experiment configuration."""
    errs: List[str] = []
    if not exp_cfg:
        return errs
    if not isinstance(exp_cfg, (dict, DictConfig)):
        return ["exp: must be a mapping."]
    if "name" in exp_cfg and not isinstance(exp_cfg.get("name"), str):
        errs.append(f"exp.name: expected str, got {type(exp_cfg.get('name'))}")
    if "outdir" in exp_cfg and not isinstance(exp_cfg.get("outdir"), str):
        errs.append(f"exp.outdir: expected str, got {type(exp_cfg.get('outdir'))}")
    repeats = exp_cfg.get("repeats", 1)
    if not isinstance(repeats, int) or repeats <= 0:
        errs.append("exp.repeats: expected positive int.")
    seed = exp_cfg.get("seed", None)
    if seed is not None and not isinstance(seed, int):
        errs.append("exp.seed: expected int or null.")
    logging_mode = exp_cfg.get("logging", "once")
    if logging_mode not in ("once", "always", False, True, None):
        errs.append("exp.logging: expected 'once' | 'always' | bool.")
    return errs


def _validate_model(model_cfg: Any) -> List[str]:
    """Validate model parameters (basic checks and ranges)."""
    errs: List[str] = []
    if not model_cfg:
        return errs
    if not isinstance(model_cfg, (dict, DictConfig)):
        return ["model: must be a mapping."]
    for key, val in model_cfg.items():
        if isinstance(val, (dict, DictConfig)):
            if _is_range_node(val):
                errs.extend(_validate_range_node(key, val))
            else:
                errs.extend(_validate_model(val))
    return errs


def _is_range_node(val: Dict[str, Any]) -> bool:
    """Check if a node looks like a range definition."""
    return {"min", "max", "step"} & set(val.keys()) != set()


def _validate_range_node(name: str, node: Dict[str, Any]) -> List[str]:
    """Validate a range node with min/max/step."""
    errs: List[str] = []
    min_val = node.get("min", None)
    max_val = node.get("max", None)
    step = node.get("step", None)
    for field_name, field_val in (("min", min_val), ("max", max_val), ("step", step)):
        if field_val is not None and not isinstance(field_val, (int, float)):
            errs.append(
                f"model.{name}.{field_name}: expected number, got {type(field_val)}"
            )
    if (
        isinstance(min_val, (int, float))
        and isinstance(max_val, (int, float))
        and min_val >= max_val
    ):
        errs.append(f"model.{name}: min should be < max (min={min_val}, max={max_val})")
    if isinstance(step, (int, float)) and step <= 0:
        errs.append(f"model.{name}.step: must be > 0, got {step}")
    return errs


def _validate_tracker(tracker_cfg: Any) -> List[str]:
    """Validate tracker configuration."""
    errs: List[str] = []
    if tracker_cfg is None:
        return errs
    if not isinstance(tracker_cfg, (dict, DictConfig)):
        return ["tracker: must be a mapping."]
    if "backend" in tracker_cfg:
        backend = tracker_cfg.get("backend")
        if backend not in ("default", "aim", "mlflow", None):
            errs.append(
                "tracker.backend: expected 'default' | 'aim' | 'mlflow' | null."
            )
    for section in ("model", "agents", "final"):
        sub = tracker_cfg.get(section, {})
        if not sub:
            continue
        if not isinstance(sub, (dict, DictConfig)):
            errs.append(f"tracker.{section}: must be a mapping.")
            continue
        if section == "agents":
            for breed, reporters in sub.items():
                if not isinstance(reporters, (dict, DictConfig)):
                    # Convert breed to string to avoid bytes formatting issue
                    breed_str = breed if isinstance(breed, str) else str(breed)
                    errs.append(f"tracker.agents.{breed_str}: must be a mapping.")
                    continue
                for name, reporter in reporters.items():
                    # Convert keys to strings to avoid bytes formatting issue
                    breed_str = breed if isinstance(breed, str) else str(breed)
                    name_str = name if isinstance(name, str) else str(name)
                    errs.extend(
                        _validate_tracker_entry(
                            f"agents.{breed_str}.{name_str}", reporter
                        )
                    )
        else:
            for name, reporter in sub.items():
                # Convert name to string to avoid bytes formatting issue
                name_str = name if isinstance(name, str) else str(name)
                errs.extend(_validate_tracker_entry(f"{section}.{name_str}", reporter))
    return errs


def _validate_tracker_entry(path: str, reporter: Any) -> List[str]:
    """Validate a single tracker entry."""
    errs: List[str] = []
    if isinstance(reporter, str):
        if not reporter:
            errs.append(f"tracker.{path}: reporter string cannot be empty.")
        return errs
    if isinstance(reporter, (dict, DictConfig)):
        if "source" not in reporter:
            errs.append(f"tracker.{path}: missing 'source'.")
        else:
            src = reporter.get("source")
            if not isinstance(src, str) or not src:
                errs.append(f"tracker.{path}.source: expected non-empty string.")
        aggregate = reporter.get("aggregate", None)
        if aggregate is not None and aggregate not in (
            "mean",
            "sum",
            "count",
            "min",
            "max",
            "std",
        ):
            errs.append(f"tracker.{path}.aggregate: invalid value '{aggregate}'.")
        return errs
    errs.append(f"tracker.{path}: expected string or mapping, got {type(reporter)}")
    return errs


def _format_validation_errors(errors: List[str]) -> str:
    """Format validation errors for display."""
    return "\n".join(f"- {err}" for err in errors)


def apply_validation(config: DictConfig) -> None:
    """Apply validation to configuration if enabled.

    Args:
        config: Normalized configuration to validate.

    Raises:
        ConfigurationError: If validation fails in strict mode.
    """
    validate_cfg = config.get("validate", {})
    validate_enabled = validate_cfg.get("enabled", False)
    strict_validation = validate_cfg.get("strict", False)

    if not validate_enabled:
        return

    validation_errors = validate_config(config, strict=False)
    if not validation_errors:
        return

    error_msg = _format_validation_errors(validation_errors)
    if strict_validation:
        raise ConfigurationError(error_msg)
    logger.warning("Configuration validation warnings:\n%s", error_msg)
