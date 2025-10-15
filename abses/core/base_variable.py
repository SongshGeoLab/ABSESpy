#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Base classes for variables in ABSESpy.

This module contains base implementations for variables and dynamic variables.
"""

from __future__ import annotations

import inspect
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, List

from abses.core.protocols import DynamicVariableProtocol, VariableProtocol

if TYPE_CHECKING:
    # Avoid circular import
    from abses.core.base_module import BaseModelElement
    from abses.core.protocols import TimeDriverProtocol


class BaseVariable(ABC, VariableProtocol):
    """Base variable implementation.

    This is currently a minimal implementation that can be extended
    as needed for tracking model variables.
    """

    pass


class BaseDynamicVariable(DynamicVariableProtocol):
    """Time dependent variable.

    A time dependent function will take the model time driver as
    an input and return its value. The function can also take other
    variables as inputs. The function can be defined as a static
    method of a class or a function.

    Attributes:
        name: Name of the variable.
        obj: Object that owns this variable.
        data: Data source for the function.
        function: Callable function to compute the variable.
        attrs: Additional attributes.
        cache: Cached value from last computation.
    """

    def __init__(
        self,
        name: str,
        obj: BaseModelElement,
        data: Any,
        function: Callable,
        **kwargs,
    ) -> None:
        """Initialize dynamic variable.

        Args:
            name: Name of the variable.
            obj: Model element that owns this variable.
            data: Data source for callable function.
            function: Function to calculate the dynamic variable.
            **kwargs: Additional attributes.
        """
        self._name: str = name
        self._obj: BaseModelElement = obj
        self._data: Any = data
        self._function: Callable = function
        self._cached_data: Any = None
        self.attrs = kwargs
        self.now()

    def __str__(self) -> str:
        return f"<{self.name}: {type(self.now())}>"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """Get the name of the variable.

        Returns:
            name: str
        """
        return self._name

    @property
    def obj(self) -> BaseModelElement:
        """Returns a base object instance.

        Returns:
            obj: BaseModelElement
        """
        return self._obj

    @obj.setter
    def obj(self, obj: BaseModelElement):
        if not isinstance(obj, BaseModelElement):
            raise TypeError("Only accept observer object")
        self._obj = obj

    @property
    def data(self) -> Any:
        """Returns unused data.

        Returns:
            data: Any
        """
        return self._data

    @property
    def function(self) -> Callable:
        """Get the function that calculates the variable.

        Returns:
            function: Callable
        """
        return self._function

    @property
    def time(self) -> TimeDriverProtocol:
        """Get the model time driver.

        Returns:
            time: abses.time.TimeDriver
        """
        return self.obj.time

    def get_required_attributes(self, function: Callable) -> List[str]:
        """Get the function required attributes.

        Returns:
            required_attributes: list[str]
        """
        # Get the source code of the function
        source_code = inspect.getsource(function)
        return [attr for attr in ["data", "obj", "time", "name"] if attr in source_code]

    def now(self) -> Any:
        """Return the dynamic variable function's output.

        Returns:
            The dynamic data value now.
        """
        required_attrs = self.get_required_attributes(self.function)
        args = {attr: getattr(self, attr) for attr in required_attrs}
        result = self.function(**args)
        self._cached_data = result
        return result

    @property
    def cache(self) -> Any:
        """Return the dynamic variable's cache"""
        return self._cached_data
