#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Tuple

import pyproj

if TYPE_CHECKING:
    from abses.core.types import SubSystemName


class State(IntEnum):
    """状态枚举，使用整数值确保可以比较"""

    NEW = 0
    INIT = 1
    READY = 2
    COMPLETE = 3


VALID_DT_ATTRS = (
    "years",
    "months",
    "days",
    "hours",
    "minutes",
    "seconds",
)

VALID_START_FLAGS = (
    "start",
    "start_dt",
    "start_time",
)

VALID_END_FLAGS = (
    "end",
    "end_dt",
    "end_time",
)

FMT_DATE = "%Y-%m-%d"
FMT_DATETIME = "%Y-%m-%d %H:%M:%S"

DEFAULT_INIT_ORDER: Tuple[SubSystemName, ...] = ("nature", "human")
DEFAULT_RUN_ORDER: Tuple[SubSystemName, ...] = ("model", "nature", "human")


def normalize_crs(crs) -> pyproj.CRS:
    """Normalize CRS to ensure consistent representation.

    Args:
        crs: CRS specification (string, int, or CRS object)

    Returns:
        Normalized CRS object
    """
    if isinstance(crs, pyproj.CRS):
        return pyproj.CRS.from_epsg(crs.to_epsg())
    if isinstance(crs, (str, int)):
        if isinstance(crs, str) and crs.isdigit():
            crs = int(crs)
        if isinstance(crs, int):
            return pyproj.CRS.from_epsg(crs)
        return pyproj.CRS.from_string(crs)
    raise ValueError(f"Unsupported CRS specification: {crs}")


# Default coordinate reference system (WGS84)
DEFAULT_CRS = normalize_crs("epsg:4326")
