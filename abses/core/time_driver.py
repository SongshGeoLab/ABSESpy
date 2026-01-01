#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

import threading
from collections import deque
from datetime import datetime
from functools import cached_property, total_ordering, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Deque,
    Dict,
    Optional,
)

import pandas as pd
import pendulum
from pendulum import DateTime

from abses.core.base import BaseModelElement
from abses.core.primitives import (
    FMT_DATETIME,
    VALID_DT_ATTRS,
    VALID_END_FLAGS,
    VALID_START_FLAGS,
)
from abses.core.protocols import MainModelProtocol, TimeDriverProtocol
from abses.utils.func import search_unique_key
from abses.utils.logging import log_session
from abses.utils.time import is_positive_int, parse_datetime, parse_duration

if TYPE_CHECKING:
    from abses.core.types import DateOrTick, DateTimeOrStr


def time_condition(condition: dict, when_run: bool = True) -> Callable:
    """
    A decorator to run a method based on a time condition.

    Parameters:
        condition:
            A dictionary containing conditions to check against the `time` attribute.
            The keys can be ['year', 'month', 'weekday', 'freqstr'].
        when_run:
            If True, the decorated method will run when the condition is met.
            If False, the decorated method will not run when the condition is met.

    Example:
        ```
        class TestActor(Actor):
            @time_condition(condition={"month": 1, "day": 1}, when_run=True)
            def happy_new_year(self):
                print("Today is 1th, January, Happy new year!")


        parameters = {"time": {"start": "1996-12-24", "days": 1}}


        model = MainModel(parameters=parameters)
        agent = model.agents.new(TestActor, 1, singleton=True)

        for _ in range(10):
            print(f"Time now is {model.time}")
            model.time.go()
            agent.happy_new_year()
        ```
        It should be called again in the next year beginning (i.e., `1998-01-01`) if we run this model longer... It means, the function will be called when the condition is fully satisfied.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, "time"):
                raise AttributeError(
                    "The object doesn't have a TimeDriver object as `time` attribute."
                )
            time = self.time
            if not isinstance(time, TimeDriver):
                raise TypeError(
                    "Decorated function is not belonged to an object with `TimeDriver`."
                )

            ok = all(
                getattr(time.dt, unit, None) == value
                for unit, value in condition.items()
            )

            if (ok and when_run) or (not ok and not when_run):
                return func(self, *args, **kwargs)

        return wrapper

    return decorator


@total_ordering
class TimeDriver(BaseModelElement, TimeDriverProtocol):
    """TimeDriver provides the functionality to manage time.

    A wrapper around datetime that adds simulation-specific functionality while
    providing access to all datetime attributes and methods.
    """

    _instances: Dict[MainModelProtocol, TimeDriver] = {}
    _lock = threading.Lock()

    def __new__(cls, model: MainModelProtocol):
        with cls._lock:
            if not cls._instances.get(model):
                driver = super(TimeDriver, cls).__new__(cls)
                cls._instances[model] = driver
            else:
                driver = cls._instances[model]
        return driver

    def __init__(self, model: MainModelProtocol):
        super().__init__(model=model, name="time")
        self._history: Deque[DateTime] = deque()
        self._history_ticks: Deque[int] = deque()
        # End time can only be DateTime | int | None at runtime
        self._end_dt: DateTime | int | None = None
        self._parse_ticking_mode(set(self.params.keys()))
        self._parse_time_settings(self.params)
        self._dt = self.start_dt
        self._logging_setup()

    def __getattr__(self, name: str):
        """Redirect all undefined attributes to the datetime object."""
        return getattr(self.dt, name)

    def __repr__(self) -> str:
        return f"<TimeDriver: {self.dt.format(self.fmt)}>"

    def __eq__(self, other) -> bool:
        if isinstance(other, (datetime, DateTime, TimeDriver)):
            other_dt = other.dt if isinstance(other, TimeDriver) else other
            return self.dt == other_dt
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def __lt__(self, other) -> bool:
        if isinstance(other, (datetime, DateTime, TimeDriver)):
            other_dt = other.dt if isinstance(other, TimeDriver) else other
            return self.dt < other_dt
        raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

    def __add__(self, other: Any) -> "TimeDriver":
        """Support addition with numbers (for Mesa 3.4.0+ compatibility).

        Mesa 3.4.0+ tries to execute self.time += 1 in its step() wrapper.
        We ignore this and return self, as our time management is independent.

        Args:
            other: Value to add (ignored).

        Returns:
            Self, unchanged.
        """
        # Ignore Mesa's automatic time increment - we manage time ourselves
        return self

    def __iadd__(self, other: Any) -> "TimeDriver":
        """Support in-place addition with numbers (for Mesa 3.4.0+ compatibility).

        Mesa 3.4.0+ tries to execute self.time += 1 in its step() wrapper.
        We ignore this and return self, as our time management is independent.

        Args:
            other: Value to add (ignored).

        Returns:
            Self, unchanged.
        """
        # Ignore Mesa's automatic time increment - we manage time ourselves
        return self

    def __deepcopy__(self, memo):
        return self

    @cached_property
    def fmt(self) -> str:
        """String format of datetime.
        If the datetime is a date object, return the date format.
        Otherwise, return the datetime format.
        """
        return FMT_DATETIME

    @property
    def expected_ticks(self) -> Optional[int]:
        """Returns the expected ticks.

        If the end_at is an integer or None, return the end_at.
        Otherwise, calculate the expected ticks.
        """
        # If the model never ends (end_at is None), return None
        if self.end_at is None:
            return None
        # If end_at is an integer (expected ticks), return end_at
        if isinstance(self.end_at, int):
            return self.end_at
        # If end_at is a datetime object, calculate the expected ticks
        if isinstance(self.end_at, DateTime):
            if self.duration is None:
                raise RuntimeError("No duration settings.")
            # 使用 pendulum 的 diff 方法计算差异
            diff_seconds = self.end_at.diff(self.dt).in_seconds()
            step_seconds = self.duration.in_seconds()
            return diff_seconds // step_seconds
        raise TypeError(f"Unknown end time type {type(self.end_at)}.")

    @property
    def should_end(self) -> bool:
        """Should the model end or not.
        If the end_dt is a datetime object, return True if the current time is greater than or equal to the end_dt.
        If the end_dt is an integer, return True if the current tick is greater than or equal to the end_dt.
        """
        if not self.end_at:
            return False
        if isinstance(self.end_at, (datetime, DateTime)):
            return self.dt >= self.end_at
        return self.tick >= self.end_at

    @property
    def history(self) -> pd.Series:
        """Returns the history of the time driver.
        The history is a pandas Series object with the datetime as the index.
        """
        return pd.Series(
            index=self._history_ticks,
            data=self._history,
            name="datetime",
        )

    @property
    def is_tick_mode(self) -> bool:
        """Returns the tick mode."""
        return self._is_tick_mode

    def to(self, dt: DateTimeOrStr | int) -> None:
        """Specific the current time.

        If the time is a string, it will be converted to a datetime object.
        If the time is an integer, it will be interpreted as a number of ticks.
        """
        if isinstance(dt, str):
            dt = parse_datetime(dt)
        self.dt = dt

    def _go_one_tick(self) -> None:
        """Advance simulation time by one tick."""
        if self.duration is None:
            self.dt = pendulum.now(tz=None)
        else:
            # 使用 += 操作符添加 duration
            self.dt += self.duration
        if self.should_end:
            self.model.running = False

    def go(self, ticks: int = 1) -> None:
        """Advance simulation time by a given number of ticks."""
        is_positive_int(ticks, raise_error=True)
        for _ in range(ticks):
            self._go_one_tick()

    def _parse_ticking_mode(self, keys: set[str]) -> None:
        """Parse the ticking mode.

        If the params contains any of the datetime attributes or start flags,
        it is not in tick mode.
        Otherwise, it is in tick mode.

        Examples:
            >>> params = {"start": "2020-01-01", "duration": 1}
            >>> time_driver = TimeDriver(params)
            >>> time_driver.is_tick_mode
            False
        """
        # If the params contains any of the datetime attributes or start flags, it is not in tick mode
        has_flags = keys.intersection(set(VALID_DT_ATTRS) | set(VALID_START_FLAGS))
        if has_flags:
            self._is_tick_mode = False
        else:
            self._is_tick_mode = True

    def _parse_time_settings(self, params: dict) -> None:
        """Setup the time driver."""
        if self.is_tick_mode:
            end = params.get("end", None)
            if end is not None and not is_positive_int(end):
                raise ValueError(
                    f"End time must be a positive int in tick mode, got {end}."
                )
            self.end_at = end
            self._start_dt = pendulum.now(tz=None)
            self._duration = None
            return

        # Parse the start time settings
        start_flag = search_unique_key(params, VALID_START_FLAGS, default="start")
        start = params.get(start_flag, pendulum.now(tz=None))
        self.start_dt = parse_datetime(start)

        # Parse the end time settings
        end_flag = search_unique_key(params, VALID_END_FLAGS, default="end")
        end = params.get(end_flag, None)
        if end is not None:
            try:
                end = parse_datetime(end)
            except Exception as e:
                raise ValueError(
                    f"Invalid end time: {end}, tick mode: {self.is_tick_mode}."
                ) from e
        self.end_at = end

        # Parse the duration settings
        duration_flags = {k: v for k, v in params.items() if k in VALID_DT_ATTRS}
        self._duration = parse_duration(duration_flags)

    def _logging_setup(self) -> None:
        msg = (
            f"Ticking mode: {self.is_tick_mode}\n"
            f"Start time: {self.start_dt.format(self.fmt)}\n"
            f"Duration: {self.duration}\n"
            f"End time: {self.end_at}\n"
        )
        log_session(title="TimeDriver", msg=msg)

    @property
    def duration(self) -> pendulum.Duration | None:
        """Returns the duration of the time driver."""
        return self._duration

    @property
    def start_dt(self) -> DateTime:
        """Returns the starting time for the model."""
        return self._start_dt

    @start_dt.setter
    def start_dt(self, dt: Optional[DateTimeOrStr]) -> None:
        """Set the starting time."""
        if not isinstance(dt, (datetime, DateTime)):
            raise TypeError(f"Wrong type for start time: {type(dt)}.")
        if isinstance(dt, datetime) and not isinstance(dt, DateTime):
            dt = pendulum.instance(dt).replace(tzinfo=None)
        elif isinstance(dt, DateTime):
            dt = dt.replace(tzinfo=None)
        self._start_dt = dt

    @property
    def end_at(self) -> Optional[DateOrTick]:
        """
        The real-world time or the ticks when the model should be end.

        If the end time is a datetime object, it will be converted to a DateTime object.
        If the end time is an integer, it will be interpreted as a number of ticks.
        """
        return self._end_dt

    @end_at.setter
    def end_at(self, dt: Optional[DateOrTick | str]) -> None:
        """Set the end time."""
        # Normalize into DateTime | int | None
        normalized: DateTime | int | None
        if dt is None:
            normalized = None
        elif is_positive_int(dt, raise_error=False):
            normalized = int(dt)  # mypy: dt is int-like here
        else:
            # If the end time is a string / datetime object.
            if isinstance(dt, str):
                tmp = parse_datetime(dt)
            else:
                tmp = dt
            if isinstance(tmp, datetime) and not isinstance(tmp, DateTime):
                normalized = pendulum.instance(tmp).replace(tzinfo=None)
            elif isinstance(tmp, DateTime):
                normalized = tmp.replace(tzinfo=None)
            else:
                raise TypeError(f"Wrong type for end time: {type(dt)}.")
        self._end_dt = normalized

    @property
    def dt(self) -> DateTime:
        """Current simulation time.

        If assigned a start/duration/end time, it will be a datetime object representing the current simulation time.
        Otherwise, it will be a datetime object representing the tick-updated time.
        """
        return self._dt

    @dt.setter
    def dt(self, value: datetime | DateTime) -> None:
        if not isinstance(value, (datetime, DateTime)):
            raise TypeError("dt must be a datetime or DateTime object")
        if isinstance(value, datetime) and not isinstance(value, DateTime):
            value = pendulum.instance(value).replace(tzinfo=None)
        elif isinstance(value, DateTime):
            value = value.replace(tzinfo=None)
        self._dt = value
        self._history.append(value)
        self._history_ticks.append(self.tick)
