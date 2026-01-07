#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Unified logging configuration for ABSESpy.

Integrates Python standard logging with Mesa and Hydra frameworks.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    pass


# Standard format for ABSESpy
ABSES_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
SIMPLE_FORMAT = "%(message)s"
DATE_FORMAT = "%H:%M:%S"

# Default values (matching log_parser.py)
DEFAULT_FORMAT = ABSES_FORMAT
DEFAULT_DATEFMT = DATE_FORMAT
DEFAULT_LEVEL = "INFO"

# Logger names
ABSES_LOGGER_NAME = "abses"
MESA_LOGGER_NAME = "mesa"
MESA_FULL_LOGGER_NAME = "MESA"  # Mesa 3.3.0 uses uppercase MESA prefix

# Sentinel for log_file_path to indicate "use default"
_LOG_FILE_PATH_DEFAULT = object()


def get_abses_logger(name: str = ABSES_LOGGER_NAME) -> logging.Logger:
    """Get ABSESpy logger instance.

    Args:
        name: Logger name (default: 'abses').

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


def get_mesa_logger() -> logging.Logger:
    """Get Mesa logger instance.

    Returns:
        Mesa logger instance.
    """
    return logging.getLogger(MESA_LOGGER_NAME)


def configure_root_logger(level: str = "INFO") -> None:
    """Configure root logger with basic settings.

    Args:
        level: Logging level.
    """
    logging.basicConfig(
        level=level,
        format=ABSES_FORMAT,
        datefmt=DATE_FORMAT,
    )


def create_console_handler(
    level: str = DEFAULT_LEVEL,
    fmt: Optional[str] = None,
    datefmt: Optional[str] = None,
) -> logging.StreamHandler:
    """Create console handler for logging.

    Args:
        level: Logging level.
        fmt: Format string (defaults to DEFAULT_FORMAT).
        datefmt: Date format string (defaults to DEFAULT_DATEFMT).

    Returns:
        Configured console handler.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt or DEFAULT_FORMAT, datefmt=datefmt or DEFAULT_DATEFMT
    )
    handler.setFormatter(formatter)
    return handler


def create_file_handler(
    filepath: Path,
    level: str = DEFAULT_LEVEL,
    fmt: Optional[str] = None,
    datefmt: Optional[str] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> logging.Handler:
    """Create file handler with optional rotation.

    Args:
        filepath: Path to log file.
        level: Logging level.
        fmt: Format string (defaults to DEFAULT_FORMAT).
        datefmt: Date format string (defaults to DEFAULT_DATEFMT).
        rotation: Rotation interval (e.g., "1 day", "100 MB").
        retention: Retention period (e.g., "10 days").

    Returns:
        Configured file handler.
    """
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Parse rotation settings
    if rotation:
        if any(unit in rotation.lower() for unit in ["day", "hour", "minute"]):
            # Time-based rotation
            when_map = {"day": "D", "hour": "H", "minute": "M"}
            when = next(
                (when_map[unit] for unit in when_map if unit in rotation.lower()), "D"
            )
            interval = int("".join(c for c in rotation if c.isdigit()) or "1")
            handler = TimedRotatingFileHandler(
                filepath,
                when=when,
                interval=interval,
                backupCount=10 if retention else 0,
            )
        else:
            # Size-based rotation
            max_bytes = 10 * 1024 * 1024  # 10MB default
            if "mb" in rotation.lower():
                size = int("".join(c for c in rotation if c.isdigit()) or "10")
                max_bytes = size * 1024 * 1024
            handler = RotatingFileHandler(
                filepath,
                maxBytes=max_bytes,
                backupCount=10 if retention else 0,
            )
    else:
        # Simple file handler without rotation
        handler = logging.FileHandler(filepath)

    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt or DEFAULT_FORMAT, datefmt=datefmt or DEFAULT_DATEFMT
    )
    handler.setFormatter(formatter)
    return handler


def setup_abses_logger(
    name: str = ABSES_LOGGER_NAME,
    level: str = DEFAULT_LEVEL,
    console: bool = True,
    console_level: Optional[str] = None,
    console_format: Optional[str] = None,
    console_datefmt: Optional[str] = None,
    file_path: Optional[Path] = None,
    file_level: Optional[str] = None,
    file_format: Optional[str] = None,
    file_datefmt: Optional[str] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> logging.Logger:
    """Setup ABSESpy logger with handlers.

    Args:
        name: Logger name.
        level: Logger level (used if console_level/file_level not specified).
        console: Whether to add console handler.
        console_level: Console handler level (defaults to level).
        console_format: Console format string (defaults to DEFAULT_FORMAT).
        console_datefmt: Console date format (defaults to DEFAULT_DATEFMT).
        file_path: Path to log file (if None, no file handler).
        file_level: File handler level (defaults to level).
        file_format: File format string (defaults to DEFAULT_FORMAT).
        file_datefmt: File date format (defaults to DEFAULT_DATEFMT).
        rotation: Rotation interval for file handler.
        retention: Retention period for file handler.

    Returns:
        Configured logger.
    """
    logger = get_abses_logger(name)
    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to root logger

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add console handler
    if console:
        handler = create_console_handler(
            level=console_level or level,
            fmt=console_format or DEFAULT_FORMAT,
            datefmt=console_datefmt or DEFAULT_DATEFMT,
        )
        logger.addHandler(handler)

    # Add file handler
    if file_path:
        handler = create_file_handler(
            filepath=file_path,
            level=file_level or level,
            fmt=file_format or DEFAULT_FORMAT,
            rotation=rotation,
            retention=retention,
        )
        logger.addHandler(handler)

    return logger


def determine_log_file_path(
    outpath: Optional[Path],
    log_name: str,
    logging_mode: str = "once",
    run_id: Optional[int] = None,
) -> Optional[Path]:
    """Determine log file path based on logging mode.

    Args:
        outpath: Output directory for log files.
        log_name: Base log file name (without extension).
        logging_mode: Logging mode - 'once', 'separate', or 'merge'.
        run_id: Run ID for the current run (1-indexed).

    Returns:
        Path to log file, or None if logging should be disabled.
    """
    if not outpath:
        return None

    # Clean log name (remove .log extension if present)
    log_name = str(log_name).replace(".log", "")

    if logging_mode == "once":
        # Only log the first repeat
        if run_id is None or run_id == 1:
            return outpath / f"{log_name}.log"
        return None
    elif logging_mode == "separate":
        # Each repeat gets its own file
        # In separate mode, run_id must be provided
        if run_id is None:
            return None  # Don't create default file in separate mode
        return outpath / f"{log_name}_{run_id}.log"
    elif logging_mode == "merge":
        # All repeats go to the same file
        return outpath / f"{log_name}.log"
    else:
        # Unknown mode, default to once behavior
        if run_id is None or run_id == 1:
            return outpath / f"{log_name}.log"
        return None


def configure_mesa_logger_with_format(
    level: str = "INFO",
    handlers: Optional[list[logging.Handler]] = None,
    mesa_format: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger]:
    """Configure Mesa loggers with custom format.

    Args:
        level: Logging level for Mesa.
        handlers: Handlers to attach (if None, creates new handlers with format).
        mesa_format: Custom format string for Mesa loggers. If None, uses ABSES_FORMAT.

    Returns:
        Tuple of (mesa_logger, MESA_logger).
    """
    # Setup lowercase mesa logger
    mesa_logger = get_mesa_logger()
    mesa_logger.setLevel(level)

    # Setup uppercase MESA logger (used by Mesa 3.3.0)
    mesa_upper_logger = logging.getLogger(MESA_FULL_LOGGER_NAME)
    mesa_upper_logger.setLevel(level)

    # Use custom format if provided, otherwise use ABSES format
    format_str = mesa_format if mesa_format is not None else ABSES_FORMAT

    if handlers:
        # Apply format to existing handlers
        formatter = logging.Formatter(format_str, datefmt=DATE_FORMAT)
        for handler in handlers:
            handler.setFormatter(formatter)

        # Configure both loggers
        for logger_obj in [mesa_logger, mesa_upper_logger]:
            logger_obj.propagate = False
            logger_obj.handlers.clear()
            for handler in handlers:
                logger_obj.addHandler(handler)
    else:
        # Let them propagate to root logger
        mesa_logger.propagate = True
        mesa_upper_logger.propagate = True

    return mesa_logger, mesa_upper_logger


def setup_mesa_logger(
    level: str = "INFO",
    handlers: Optional[list[logging.Handler]] = None,
    mesa_format: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger]:
    """Setup Mesa loggers to integrate with ABSESpy logging.

    Mesa 3.3.0 uses both 'mesa' and 'MESA' logger names.

    Args:
        level: Logging level for Mesa.
        handlers: Handlers to attach (if None, inherits from parent).
        mesa_format: Custom format string for Mesa loggers. If None, uses ABSES_FORMAT.

    Returns:
        Tuple of (mesa_logger, MESA_logger).
    """
    return configure_mesa_logger_with_format(
        level=level, handlers=handlers, mesa_format=mesa_format
    )


def setup_integrated_logging(
    abses_logger_name: str = ABSES_LOGGER_NAME,
    level: str = DEFAULT_LEVEL,
    outpath: Optional[Path] = None,
    log_name: str = "abses",
    console: bool = True,
    console_level: Optional[str] = None,
    console_format: Optional[str] = None,
    console_datefmt: Optional[str] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
    log_file_path: Optional[Path] = _LOG_FILE_PATH_DEFAULT,
    file_level: Optional[str] = None,
    file_format: Optional[str] = None,
    file_datefmt: Optional[str] = None,
    mesa_format: Optional[str] = None,
    mesa_level: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Setup integrated logging for ABSESpy and Mesa.

    Args:
        abses_logger_name: ABSESpy logger name.
        level: Logging level (used if console_level/file_level not specified).
        outpath: Output directory for log files.
        log_name: Log file name (without extension).
        console: Whether to log to console.
        console_level: Console handler level (defaults to level).
        console_format: Console format string.
        console_datefmt: Console date format string.
        rotation: Rotation interval.
        retention: Retention period.
        log_file_path: Explicit log file path. If _LOG_FILE_PATH_DEFAULT, uses default from outpath/log_name.
                      If None, disables file logging.
        file_level: File handler level (defaults to level).
        file_format: File format string.
        file_datefmt: File date format string.
        mesa_format: Custom format string for Mesa loggers. If None, uses DEFAULT_FORMAT.
        mesa_level: Logging level for Mesa loggers. If None, uses the main level.

    Returns:
        Tuple of (abses_logger, mesa_logger, mesa_upper_logger).
    """
    # Determine file path
    if log_file_path is _LOG_FILE_PATH_DEFAULT:
        # log_file_path was not provided, use default
        file_path = outpath / f"{log_name}.log" if outpath else None
    elif log_file_path is None:
        # log_file_path was explicitly set to None, don't create file
        file_path = None
    else:
        # log_file_path was explicitly provided
        file_path = log_file_path

    # Setup ABSESpy logger
    # Clear any existing handlers from parent loggers to prevent mixing
    # This ensures experiment-level loggers don't inherit model run log handlers
    abses_logger = setup_abses_logger(
        name=abses_logger_name,
        level=level,
        console=console,
        console_level=console_level,
        console_format=console_format,
        console_datefmt=console_datefmt,
        file_path=file_path,
        file_level=file_level,
        file_format=file_format,
        file_datefmt=file_datefmt,
        rotation=rotation,
        retention=retention,
    )

    # Ensure child loggers (like abses.core.experiment) don't inherit handlers
    # by setting propagate=False on parent loggers
    for parent_name in ["abses.core", "abses.core.experiment"]:
        parent_logger = logging.getLogger(parent_name)
        parent_logger.propagate = False
        # Don't clear handlers here, as they may be configured separately

    # Setup Mesa loggers (both 'mesa' and 'MESA') to use same handlers with format
    # Use mesa_level if provided, otherwise use main level
    mesa_log_level = mesa_level if mesa_level is not None else level
    mesa_logger, mesa_upper_logger = setup_mesa_logger(
        level=mesa_log_level,
        handlers=list(abses_logger.handlers) if abses_logger.handlers else None,
        mesa_format=mesa_format,
    )

    return abses_logger, mesa_logger, mesa_upper_logger


class LoggerAdapter:
    """Adapter to make standard logging work like loguru.

    Provides a loguru-like interface for backward compatibility.
    """

    def __init__(self, logger: logging.Logger):
        """Initialize adapter.

        Args:
            logger: Standard logger to adapt.
        """
        self._logger = logger
        self._extra: Dict[str, Any] = {}

    def bind(self, **kwargs) -> LoggerAdapter:
        """Bind extra context (loguru-style).

        Args:
            **kwargs: Extra context to bind.

        Returns:
            Self for chaining.
        """
        new_adapter = LoggerAdapter(self._logger)
        new_adapter._extra = {**self._extra, **kwargs}
        return new_adapter

    def _format_message(self, message: str) -> str:
        """Format message based on extra context.

        Args:
            message: Message to format.

        Returns:
            Formatted message.
        """
        if self._extra.get("no_format"):
            return message
        return message

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(self._format_message(message), *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self._logger.info(self._format_message(message), *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(self._format_message(message), *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self._logger.error(self._format_message(message), *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(self._format_message(message), *args, **kwargs)

    def add(self, *args, **kwargs) -> int:
        """Add handler (loguru-style compatibility).

        Returns:
            Handler ID (always 0 for compatibility).
        """
        # This is for loguru compatibility, actual handler management
        # is done through standard logging configuration
        return 0

    def remove(self, handler_id: Optional[int] = None) -> None:
        """Remove handler (loguru-style compatibility).

        Args:
            handler_id: Handler ID to remove.
        """
        # For loguru compatibility
        if handler_id == 0 or handler_id is None:
            self._logger.handlers.clear()
