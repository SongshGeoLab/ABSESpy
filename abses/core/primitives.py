#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Tuple

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

DEFAULT_CRS = "epsg:4326"
