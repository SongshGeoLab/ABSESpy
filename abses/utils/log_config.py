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

# Logger names
ABSES_LOGGER_NAME = "abses"
MESA_LOGGER_NAME = "mesa"
MESA_FULL_LOGGER_NAME = "MESA"  # Mesa 3.3.0 uses uppercase MESA prefix


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
    level: str = "WARNING",
    fmt: str = ABSES_FORMAT,
) -> logging.StreamHandler:
    """Create console handler for logging.

    Args:
        level: Logging level.
        fmt: Format string.

    Returns:
        Configured console handler.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(fmt, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def create_file_handler(
    filepath: Path,
    level: str = "INFO",
    fmt: str = ABSES_FORMAT,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> logging.Handler:
    """Create file handler with optional rotation.

    Args:
        filepath: Path to log file.
        level: Logging level.
        fmt: Format string.
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
    formatter = logging.Formatter(fmt, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def setup_abses_logger(
    name: str = ABSES_LOGGER_NAME,
    level: str = "INFO",
    console: bool = True,
    console_level: str = "WARNING",
    file_path: Optional[Path] = None,
    file_level: str = "INFO",
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> logging.Logger:
    """Setup ABSESpy logger with handlers.

    Args:
        name: Logger name.
        level: Logger level.
        console: Whether to add console handler.
        console_level: Console handler level.
        file_path: Path to log file (if None, no file handler).
        file_level: File handler level.
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
        handler = create_console_handler(console_level)
        logger.addHandler(handler)

    # Add file handler
    if file_path:
        handler = create_file_handler(
            file_path,
            level=file_level,
            rotation=rotation,
            retention=retention,
        )
        logger.addHandler(handler)

    return logger


def setup_mesa_logger(
    level: str = "INFO",
    handlers: Optional[list[logging.Handler]] = None,
) -> tuple[logging.Logger, logging.Logger]:
    """Setup Mesa loggers to integrate with ABSESpy logging.

    Mesa 3.3.0 uses both 'mesa' and 'MESA' logger names.

    Args:
        level: Logging level for Mesa.
        handlers: Handlers to attach (if None, inherits from parent).

    Returns:
        Tuple of (mesa_logger, MESA_logger).
    """
    # Setup lowercase mesa logger
    mesa_logger = get_mesa_logger()
    mesa_logger.setLevel(level)

    # Setup uppercase MESA logger (used by Mesa 3.3.0)
    mesa_upper_logger = logging.getLogger(MESA_FULL_LOGGER_NAME)
    mesa_upper_logger.setLevel(level)

    if handlers:
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


def setup_integrated_logging(
    abses_logger_name: str = ABSES_LOGGER_NAME,
    level: str = "INFO",
    outpath: Optional[Path] = None,
    log_name: str = "abses",
    console: bool = True,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Setup integrated logging for ABSESpy and Mesa.

    Args:
        abses_logger_name: ABSESpy logger name.
        level: Logging level.
        outpath: Output directory for log files.
        log_name: Log file name (without extension).
        console: Whether to log to console.
        rotation: Rotation interval.
        retention: Retention period.

    Returns:
        Tuple of (abses_logger, mesa_logger, mesa_upper_logger).
    """
    # Determine file path
    file_path = outpath / f"{log_name}.log" if outpath else None

    # Setup ABSESpy logger
    abses_logger = setup_abses_logger(
        name=abses_logger_name,
        level=level,
        console=console,
        console_level="WARNING",
        file_path=file_path,
        file_level=level,
        rotation=rotation,
        retention=retention,
    )

    # Setup Mesa loggers (both 'mesa' and 'MESA') to use same handlers
    mesa_logger, mesa_upper_logger = setup_mesa_logger(
        level=level,
        handlers=list(abses_logger.handlers) if abses_logger.handlers else None,
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
