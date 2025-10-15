#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Logging module for ABSESpy.

Provides a unified logging interface using Python standard logging,
compatible with Mesa 3.3.0 and Hydra configuration.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from abses.utils.log_config import (
    ABSES_LOGGER_NAME,
    LoggerAdapter,
    get_abses_logger,
    setup_integrated_logging,
)

if TYPE_CHECKING:
    from abses.core.protocols import ExperimentProtocol

# Create default logger instance with adapter for backward compatibility
_std_logger = get_abses_logger(ABSES_LOGGER_NAME)
logger = LoggerAdapter(_std_logger)

# Legacy format constant for compatibility
FORMAT = "[{time:HH:mm:ss}][{level}][{module}] {message}\n"


def formatter(record: logging.LogRecord) -> str:
    """Customize formatter for compatibility.
    
    Args:
        record: Log record.
        
    Returns:
        Formatted string.
    """
    # This is kept for backward compatibility but not actively used
    # Standard logging uses Formatter objects instead
    return "{message}\n"


def log_session(title: str, msg: str = "") -> None:
    """Log a new session with decorative formatting.
    
    Args:
        title: Session title.
        msg: Optional message content.
    """
    first_line = "\n" + "=" * 20 + "\n"
    center_line = f"  {title}  ".center(20, "-")
    end_line = "\n" + "=" * 20 + "\n"
    ending = "".center(20, "-")
    
    # Use no_format binding for clean output
    full_message = first_line + center_line + end_line + msg + ending
    logger.bind(no_format=True).info(full_message)


def setup_logger_info(
    exp: Optional[ExperimentProtocol] = None,
) -> None:
    """Set up logger info banner.
    
    Args:
        exp: Optional experiment instance.
    """
    line_equal = "".center(40, "=") + "\n"
    line_star = "".center(40, "·") + "\n"
    content = "  ABSESpy Framework  ".center(40, "*") + "\n"
    msg = line_equal + line_star + content + line_star + line_equal
    
    logger.bind(no_format=True).info(msg)
    is_exp_env = exp is not None
    logger.bind(no_format=True).info(f"Exp environment: {is_exp_env}\n")


def setup_model_logger(
    name: str = "model",
    level: str = "INFO",
    outpath: Optional[Path] = None,
    console: bool = True,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Setup logging for a model run.
    
    Configures ABSESpy and Mesa loggers (both 'mesa' and 'MESA') with integrated handlers.
    
    Args:
        name: Log file name.
        level: Logging level.
        outpath: Output directory for log files.
        console: Whether to log to console.
        rotation: Rotation interval (e.g., "1 day", "100 MB").
        retention: Retention period (e.g., "10 days").
        
    Returns:
        Tuple of (abses_logger, mesa_logger, mesa_upper_logger).
    """
    # Convert outpath to Path if string
    if outpath and not isinstance(outpath, Path):
        outpath = Path(outpath)
    
    # Setup integrated logging
    abses_logger, mesa_logger, mesa_upper_logger = setup_integrated_logging(
        level=level,
        outpath=outpath,
        log_name=name,
        console=console,
        rotation=rotation,
        retention=retention,
    )
    
    return abses_logger, mesa_logger, mesa_upper_logger


# Legacy exports for backward compatibility
__all__ = [
    "logger",
    "formatter",
    "log_session",
    "setup_logger_info",
    "setup_model_logger",
    "FORMAT",
]
