#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Hydra logging configuration utilities.

Generates Hydra job_logging configuration from log.hydra settings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from omegaconf import DictConfig

from abses.utils.log_parser import get_stdout_config

if TYPE_CHECKING:
    pass


def generate_hydra_job_logging(cfg: DictConfig | Dict[str, Any]) -> Dict[str, Any]:
    """Generate Hydra job_logging configuration from log.hydra settings.

    Args:
        cfg: Configuration dictionary.

    Returns:
        Dictionary with Hydra job_logging configuration.
    """
    hydra_stdout = get_stdout_config(cfg, "hydra")

    # Default configuration
    default_format = "[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
    default_datefmt = "%H:%M:%S"
    default_level = "WARNING"

    if hydra_stdout:
        format_str = hydra_stdout.get("format", default_format)
        datefmt = hydra_stdout.get("datefmt", default_datefmt)
        level = hydra_stdout.get("level", default_level)
    else:
        format_str = default_format
        datefmt = default_datefmt
        level = default_level

    return {
        "version": 1,
        "formatters": {
            "simple": {
                "format": format_str,
                "datefmt": datefmt,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "simple",
                "stream": "ext://sys.stderr",
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "disable_existing_loggers": False,
    }
