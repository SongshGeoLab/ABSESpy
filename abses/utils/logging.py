#!/usr/bin/env python3
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
    determine_log_file_path,
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


def log_repeat_separator(run_id: int, total_repeats: int) -> None:
    """Log a separator for a new repeat run in merge mode.

    Args:
        run_id: Current repeat ID (1-indexed).
        total_repeats: Total number of repeats.
    """
    separator = "\n" + "=" * 60 + "\n"
    header = f"Repeat {run_id}/{total_repeats}".center(60) + "\n"
    footer = "=" * 60 + "\n"
    logger.bind(no_format=True).info(separator + header + footer)


def setup_model_logger(
    name: str = "model",
    level: str = "INFO",
    outpath: Optional[Path] = None,
    console: bool = True,
    console_level: Optional[str] = None,
    console_format: Optional[str] = None,
    console_datefmt: Optional[str] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
    log_file_path: Optional[Path] = None,
    logging_mode: str = "once",
    run_id: Optional[int] = None,
    file_level: Optional[str] = None,
    file_format: Optional[str] = None,
    file_datefmt: Optional[str] = None,
    mesa_format: Optional[str] = None,
    mesa_level: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Setup logging for a model run.

    Configures ABSESpy and Mesa loggers (both 'mesa' and 'MESA') with integrated handlers.
    Also configures the root logger so that user module logs (e.g., logging.getLogger(__name__))
    are written to the same model log file.

    Args:
        name: Log file name.
        level: Logging level (used if console_level/file_level not specified).
        outpath: Output directory for log files.
        console: Whether to log to console.
        console_level: Console handler level (defaults to level).
        console_format: Console format string.
        console_datefmt: Console date format string.
        rotation: Rotation interval (e.g., "1 day", "100 MB").
        retention: Retention period (e.g., "10 days").
        log_file_path: Explicit log file path (overrides automatic path determination).
        logging_mode: Logging mode - 'once', 'separate', or 'merge'.
        run_id: Repeat ID for the current run (1-indexed).
        file_level: File handler level (defaults to level).
        file_format: File format string.
        file_datefmt: File date format string.
        mesa_format: Custom format string for Mesa loggers. If None, uses ABSESpy format.
        mesa_level: Logging level for Mesa loggers. If None, uses the main level.

    Returns:
        Tuple of (abses_logger, mesa_logger, mesa_upper_logger).
    """
    # Convert outpath to Path if string
    if outpath and not isinstance(outpath, Path):
        outpath = Path(outpath)

    # Determine log file path if not explicitly provided
    if log_file_path is None:
        log_file_path = determine_log_file_path(
            outpath=outpath,
            log_name=name,
            logging_mode=logging_mode,
            run_id=run_id,
        )

    # Setup integrated logging
    abses_logger, mesa_logger, mesa_upper_logger = setup_integrated_logging(
        level=level,
        outpath=outpath,
        log_name=name,
        console=console,
        console_level=console_level,
        console_format=console_format,
        console_datefmt=console_datefmt,
        rotation=rotation,
        retention=retention,
        log_file_path=log_file_path,
        file_level=file_level,
        file_format=file_format,
        file_datefmt=file_datefmt,
        mesa_format=mesa_format,
        mesa_level=mesa_level,
    )

    # Configure root logger to use the same handlers as abses_logger
    # This ensures user module logs (e.g., logging.getLogger(__name__)) are also captured
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers from root logger to avoid duplicates
    # But keep Hydra's handlers if any (they handle other logs)
    for handler in root_logger.handlers[:]:
        # Only remove handlers that are not Hydra's
        # Hydra handlers typically have 'hydra' in their name or are configured differently
        handler_name = getattr(handler, "name", "") or ""
        if "hydra" not in handler_name.lower():
            root_logger.removeHandler(handler)

    # Add the same handlers from abses_logger to root logger
    for handler in abses_logger.handlers:
        # Create a copy of the handler to avoid sharing state
        # For FileHandler, we can share the same file
        if handler not in root_logger.handlers:
            root_logger.addHandler(handler)

    return abses_logger, mesa_logger, mesa_upper_logger


# Legacy exports for backward compatibility
__all__ = [
    "logger",
    "formatter",
    "log_session",
    "log_repeat_separator",
    "setup_logger_info",
    "setup_model_logger",
    "FORMAT",
]
