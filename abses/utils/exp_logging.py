#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Experiment-level logging configuration.

Separates experiment-level logging from model run-level logging.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from omegaconf import DictConfig, OmegaConf

from abses.utils.log_config import (
    DEFAULT_DATEFMT,
    DEFAULT_FORMAT,
    DEFAULT_LEVEL,
    create_console_handler,
    create_file_handler,
)
from abses.utils.log_parser import (
    get_file_config,
    get_log_mode,
    get_stdout_config,
)

if TYPE_CHECKING:
    pass

# Experiment-level logger name
EXP_LOGGER_NAME = "abses.core.experiment"


def setup_exp_logger(
    cfg: DictConfig | dict, logging_mode: Optional[str] = None
) -> logging.Logger:
    """Setup experiment-level logger.

    This logger is separate from model run loggers and should only
    log experiment-level information (progress, summaries, etc.).

    Args:
        cfg: Configuration dictionary.
        logging_mode: Logging mode - 'once', 'separate', or 'merge'.
                     If None, reads from config.

    Returns:
        Configured experiment logger.
    """
    logger = logging.getLogger(EXP_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't propagate to avoid mixing with model loggers

    # Clear existing handlers to ensure clean state
    logger.handlers.clear()

    # Ensure parent loggers don't add handlers
    parent_logger = logging.getLogger("abses.core")
    parent_logger.propagate = False
    parent_logger.handlers.clear()

    # Get logging mode
    if logging_mode is None:
        logging_mode = get_log_mode(cfg)

    # Get experiment-level logging configuration
    exp_stdout = get_stdout_config(cfg, "exp")
    exp_file = get_file_config(cfg, "exp")

    # Setup stdout handler
    if exp_stdout:
        stdout_handler = create_console_handler(
            level=exp_stdout.get("level", DEFAULT_LEVEL),
            fmt=exp_stdout.get("format", DEFAULT_FORMAT),
            datefmt=exp_stdout.get("datefmt", DEFAULT_DATEFMT),
        )
        logger.addHandler(stdout_handler)
    # Note: We don't add a default stdout handler if exp_stdout is disabled
    # This allows users to have file-only logging for experiments

    # Setup file handler
    if exp_file:
        # Determine log file name
        # Check if name was explicitly set in the config
        if isinstance(cfg, dict):
            exp_file_cfg_raw = cfg.get("log", {}).get("exp", {}).get("file", {})
        else:
            try:
                exp_file_cfg_raw = OmegaConf.select(cfg, "log.exp.file", default={})
            except Exception:
                exp_file_cfg_raw = {}

        name_explicitly_set = (
            isinstance(exp_file_cfg_raw, dict) and "name" in exp_file_cfg_raw
        ) or (isinstance(exp_file_cfg_raw, DictConfig) and "name" in exp_file_cfg_raw)

        exp_file_name = exp_file.get("name", "experiment.log")
        if (
            logging_mode == "separate"
            and not name_explicitly_set
            and exp_file_name == "experiment.log"
        ):
            # In separate mode, if name not explicitly set, use run.file.name
            run_file_cfg = get_file_config(cfg, "run")
            if run_file_cfg:
                log_name = str(run_file_cfg.get("name", "model")).replace(".log", "")
                exp_file_name = f"{log_name}.log"

        # Get output path
        if isinstance(cfg, dict):
            outpath = cfg.get("outpath")
        else:
            # For DictConfig, use OmegaConf.select
            try:
                outpath = OmegaConf.select(cfg, "outpath", default=None)
            except Exception:
                outpath = None

        if outpath is None:
            outpath = Path.cwd()
        elif isinstance(outpath, str):
            outpath = Path(outpath)
        elif not isinstance(outpath, Path):
            outpath = Path(str(outpath))

        file_path = outpath / exp_file_name

        file_handler = create_file_handler(
            filepath=file_path,
            level=exp_file.get("level", DEFAULT_LEVEL),
            fmt=exp_file.get("format", DEFAULT_FORMAT),
            datefmt=exp_file.get("datefmt", DEFAULT_DATEFMT),
            rotation=exp_file.get("rotation", None),
            retention=exp_file.get("retention", None),
        )
        logger.addHandler(file_handler)
    elif logging_mode == "separate":
        # In separate mode, if exp.file is not enabled, create experiment log file using run.file.name
        run_file_cfg = get_file_config(cfg, "run")
        log_name = (
            str(run_file_cfg.get("name", "model")).replace(".log", "")
            if run_file_cfg
            else "model"
        )

        # Get output path
        if isinstance(cfg, dict):
            outpath = cfg.get("outpath")
        else:
            # For DictConfig, use OmegaConf.select
            try:
                outpath = OmegaConf.select(cfg, "outpath", default=None)
            except Exception:
                outpath = None

        if outpath is None:
            outpath = Path.cwd()
        elif isinstance(outpath, str):
            outpath = Path(outpath)
        elif not isinstance(outpath, Path):
            outpath = Path(str(outpath))

        file_path = outpath / f"{log_name}.log"

        file_handler = create_file_handler(
            filepath=file_path,
            level=DEFAULT_LEVEL,
            fmt=DEFAULT_FORMAT,
            datefmt=DEFAULT_DATEFMT,
            rotation=None,
            retention=None,
        )
        logger.addHandler(file_handler)

    return logger
