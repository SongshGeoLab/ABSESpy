#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

import pandas as pd
import pendulum
from pendulum import DateTime

from abses.core.primitives import (
    VALID_DT_ATTRS,
)

if TYPE_CHECKING:
    from abses.core.types import DateTimeOrStr


def is_positive_int(value: Any, raise_error: bool = False) -> bool:
    """Check if the value is a positive integer."""
    is_positive_int = isinstance(value, int) and value >= 0
    if not is_positive_int and raise_error:
        raise ValueError(f"Expected a positive integer, but got {value}.")
    return is_positive_int


def parse_datetime(dt: DateTimeOrStr) -> DateTime:
    """Parse a string into pendulum DateTime without timezone.

    Raises:
        ValueError: If the input is an integer
        TypeError: If the input is not a datetime or a string

    Examples:
        >>> parse_datetime("2020-01-01")
        DateTime(2020, 1, 1, 0, 0, 0)
        >>> parse_datetime("2020")
        DateTime(2020, 1, 1, 0, 0, 0)
        >>> parse_datetime(1)
        ValueError: Do not support integer: 1, please use tick mode or input a datetime-like string.
    """
    if isinstance(dt, DateTime):
        # 确保没有时区信息
        return dt.replace(tzinfo=None)
    if isinstance(dt, str):
        dt = pd.to_datetime(dt).to_pydatetime()
    if isinstance(dt, datetime):
        # 使用 pendulum.instance 方法简化转换，并确保没有时区信息
        return pendulum.instance(dt, tz=None)
    if isinstance(dt, int):
        raise ValueError(
            f"Do not support integer: {dt}, please use tick mode or input a datetime-like string."
        )
    raise TypeError(f"Expected a datetime or a string, but got: {dt}.")


def parse_duration(
    kwargs: Dict[str, DateTimeOrStr],
) -> pendulum.Duration | None:
    """Set the duration using pendulum.Duration.

    Args:
        kwargs: Duration configuration containing time units

    Raises:
        ValueError: If any time unit is negative
        KeyError: If any time unit is invalid
    """
    if not kwargs:
        return None
    # 检查时间单位
    for unit, value in kwargs.items():
        if unit not in VALID_DT_ATTRS:
            raise KeyError(f"Time unit {unit} is invalid.")
        if not is_positive_int(value, raise_error=False):
            raise KeyError(f"Time unit {unit} got an invalid value: {value}.")
    # 使用 pendulum 创建 duration 对象
    return pendulum.duration(**kwargs)
