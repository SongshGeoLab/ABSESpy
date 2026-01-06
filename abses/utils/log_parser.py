#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Logging configuration parser for ABSESpy.

Parses the unified logging configuration structure and provides
access to different logging levels (hydra, exp, run).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from omegaconf import DictConfig, OmegaConf

if TYPE_CHECKING:
    pass

# Default values
DEFAULT_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
DEFAULT_DATEFMT = "%H:%M:%S"
DEFAULT_LEVEL = "INFO"


def get_log_mode(cfg: DictConfig | Dict[str, Any]) -> str:
    """Get logging mode from configuration.

    Args:
        cfg: Configuration dictionary.

    Returns:
        Logging mode: 'once', 'separate', or 'merge'. Defaults to 'once'.
    """
    # Handle both DictConfig and plain dict
    if isinstance(cfg, DictConfig):
        # Check if log.mode was explicitly set (not defaulted)
        mode = OmegaConf.select(cfg, "log.mode")
        if mode is None:
            # Key doesn't exist, use default and check backward compat
            mode = "once"
            old_mode = OmegaConf.select(cfg, "exp.logging.mode", default=None)
            if old_mode is not None:
                if isinstance(old_mode, str):
                    return old_mode
                elif isinstance(old_mode, dict):
                    return old_mode.get("mode", "once")
        # If mode was explicitly set, return it without checking old config
        return mode if mode else "once"
    else:
        # Plain dict: use dict.get() with nested access
        log_section = cfg.get("log", {})
        if isinstance(log_section, dict):
            # Check if "mode" key exists explicitly
            if "mode" in log_section:
                mode = log_section.get("mode", "once")
                # Explicitly set, return it without checking old config
                return mode if mode else "once"
            else:
                # Key doesn't exist, use default and check backward compat
                mode = "once"
        else:
            mode = "once"
        # Backward compatibility: check exp.logging.mode only if mode wasn't explicitly set
        exp_section = cfg.get("exp", {})
        if isinstance(exp_section, dict):
            logging_section = exp_section.get("logging", {})
            if isinstance(logging_section, dict):
                old_mode = logging_section.get("mode")
            elif isinstance(logging_section, str):
                old_mode = logging_section
            else:
                old_mode = None
            if old_mode is not None:
                if isinstance(old_mode, str):
                    return old_mode
                elif isinstance(old_mode, dict):
                    return old_mode.get("mode", "once")

    return mode if mode else "once"


def get_log_config(
    cfg: DictConfig | Dict[str, Any], level: str = "run"
) -> Dict[str, Any]:
    """Get logging configuration for a specific level.

    Args:
        cfg: Configuration dictionary.
        level: Logging level - 'hydra', 'exp', or 'run'.

    Returns:
        Dictionary with logging configuration for the specified level.
    """
    # Handle both DictConfig and plain dict
    if isinstance(cfg, DictConfig):
        log_cfg = OmegaConf.select(cfg, f"log.{level}", default={})
    else:
        # Plain dict: use dict.get() with nested access
        log_section = cfg.get("log", {})
        log_cfg = log_section.get(level, {}) if isinstance(log_section, dict) else {}

    # Handle backward compatibility for old log structure
    if not log_cfg and level == "run":
        # Try to read from old log structure
        if isinstance(cfg, DictConfig):
            old_log = OmegaConf.select(cfg, "log", default={})
        else:
            old_log = cfg.get("log", {})

        if not old_log or not isinstance(old_log, dict):
            return {}

        # Map old structure to new structure
        result = {
            "stdout": {
                "enabled": old_log.get("console", False),
                "level": old_log.get("level", DEFAULT_LEVEL),
                "format": DEFAULT_FORMAT,
                "datefmt": DEFAULT_DATEFMT,
            },
            "file": {
                "enabled": True,  # Assume enabled if log section exists
                "name": old_log.get("name", "model"),
                "level": old_log.get("level", DEFAULT_LEVEL),
                "format": DEFAULT_FORMAT,
                "datefmt": DEFAULT_DATEFMT,
                "rotation": old_log.get("rotation", None),
                "retention": old_log.get("retention", None),
            },
        }

        # Handle MESA config
        mesa_cfg = old_log.get("mesa", {})
        if isinstance(mesa_cfg, dict):
            result["mesa"] = {
                "level": mesa_cfg.get("level", None),
                "format": mesa_cfg.get("format", None),
            }
        else:
            result["mesa"] = {"level": None, "format": None}

        return result

    # Convert DictConfig to dict if needed
    if isinstance(log_cfg, DictConfig):
        log_cfg = OmegaConf.to_container(log_cfg, resolve=True)

    if not isinstance(log_cfg, dict):
        return {}

    return log_cfg


def get_stdout_config(
    cfg: DictConfig | Dict[str, Any], level: str = "run"
) -> Dict[str, Any]:
    """Get stdout logging configuration for a specific level.

    Args:
        cfg: Configuration dictionary.
        level: Logging level - 'hydra', 'exp', or 'run'.

    Returns:
        Dictionary with stdout configuration, or empty dict if disabled.
    """
    log_cfg = get_log_config(cfg, level)
    stdout_cfg = log_cfg.get("stdout", {})

    if isinstance(stdout_cfg, dict):
        enabled = stdout_cfg.get("enabled", False)
        if not enabled:
            return {}
        return {
            "enabled": True,
            "level": stdout_cfg.get("level", DEFAULT_LEVEL),
            "format": stdout_cfg.get("format", DEFAULT_FORMAT),
            "datefmt": stdout_cfg.get("datefmt", DEFAULT_DATEFMT),
        }
    return {}


def get_file_config(
    cfg: DictConfig | Dict[str, Any], level: str = "run"
) -> Dict[str, Any]:
    """Get file logging configuration for a specific level.

    Args:
        cfg: Configuration dictionary.
        level: Logging level - 'hydra', 'exp', or 'run'.

    Returns:
        Dictionary with file configuration, or empty dict if disabled.
    """
    log_cfg = get_log_config(cfg, level)
    file_cfg = log_cfg.get("file", {})

    if isinstance(file_cfg, dict):
        enabled = file_cfg.get("enabled", True)  # Default to enabled for file
        if not enabled:
            return {}
        # Default name depends on level: "experiment.log" for exp, "model" for run
        default_name = "experiment.log" if level == "exp" else "model"
        return {
            "enabled": True,
            "name": file_cfg.get("name", default_name),
            "level": file_cfg.get("level", DEFAULT_LEVEL),
            "format": file_cfg.get("format", DEFAULT_FORMAT),
            "datefmt": file_cfg.get("datefmt", DEFAULT_DATEFMT),
            "rotation": file_cfg.get("rotation", None),
            "retention": file_cfg.get("retention", None),
        }
    return {}


def get_mesa_config(
    cfg: DictConfig | Dict[str, Any], level: str = "run"
) -> Dict[str, Any]:
    """Get MESA logging configuration.

    Args:
        cfg: Configuration dictionary.
        level: Logging level (usually 'run' for MESA).

    Returns:
        Dictionary with MESA configuration.
    """
    log_cfg = get_log_config(cfg, level)
    mesa_cfg = log_cfg.get("mesa", {})

    if isinstance(mesa_cfg, dict):
        return {
            "level": mesa_cfg.get("level", None),
            "format": mesa_cfg.get("format", None),
        }
    return {"level": None, "format": None}
