#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


class ABSESpyError(Exception):
    """Raised when Agent-based modeling logic is not satisfied."""


class ConfigurationError(ABSESpyError):
    """Raised when configuration validation fails."""

    def __init__(self, message: str) -> None:
        """Initialize configuration error.

        Args:
            message: Description of the configuration issue.
        """
        super().__init__(message)
