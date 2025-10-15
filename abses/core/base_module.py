#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Base classes for model modules in ABSESpy.

This module contains base implementations for model elements, state managers,
and modules.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, Callable, Dict, List, Optional, final

from omegaconf import DictConfig

from abses.core.base_variable import BaseDynamicVariable
from abses.core.primitives import State
from abses.core.protocols import (
    DynamicVariableProtocol,
    MainModelProtocol,
    ModelElement,
    ModuleProtocol,
    Observer,
    StateManagerProtocol,
    TimeDriverProtocol,
)
from abses.utils.regex import is_snake_name


class BaseModelElement(ABC, ModelElement):
    """Base model element implementation.

    Provides common functionality for all model elements including:
    - Reference to parent model
    - Name management
    - Parameter access
    - Dynamic variables support

    Attributes:
        model: The parent ABSESpy model.
        name: Name of this element.
        params: Configuration parameters for this element.
        tick: Current simulation tick.
        time: Time driver from the model.
        dynamic_variables: Dictionary of dynamic variables.
    """

    def __init__(self, model: MainModelProtocol, name: Optional[str] = None) -> None:
        """Initialize base model element.

        Args:
            model: Parent ABSESpy model.
            name: Optional name for this element.
        """
        self._model = model
        self._name = name
        self._dynamic_variables: Dict[str, DynamicVariableProtocol] = {}
        self._updated_ticks: List[int] = []

    @property
    def model(self) -> MainModelProtocol:
        """Get the parent model.

        Returns:
            The ABSESpy model instance.
        """
        return self._model

    @model.setter
    def model(self, model: MainModelProtocol) -> None:
        """Set the parent model (no-op for safety).

        Args:
            model: Model to set.
        """
        pass

    @property
    def name(self) -> str:
        """Get the component name.

        Returns:
            Component name (defaults to class name if not set).

        Raises:
            ValueError: If name is not a valid snake_case string.
        """
        if self._name is None:
            return self.__class__.__name__
        if not isinstance(self._name, str):
            raise ValueError(f"Name must be a string, but got {type(self._name)}")
        if not is_snake_name(self._name):
            raise ValueError(f"Name '{self._name}' is not a valid name.")
        return self._name

    @property
    def params(self) -> DictConfig:
        """Get component parameters.

        Returns configuration from model settings for this component's name.
        If no configuration exists, returns an empty DictConfig.

        Returns:
            Component parameters.
        """
        return self.model.settings.get(self.name, DictConfig({}))

    # Alias for params
    p = params

    @property
    def tick(self) -> int:
        """Get the current tick.

        Returns:
            Current simulation tick.
        """
        return self.model.steps

    @property
    def time(self) -> TimeDriverProtocol:
        """Get the current time driver.

        Returns:
            Time driver from model.
        """
        return self.model.time

    @property
    def dynamic_variables(self) -> Dict[str, DynamicVariableProtocol]:
        """Get read-only dynamic variables dictionary.

        Returns:
            Dictionary of model's dynamic variables.
        """
        return self._dynamic_variables

    def add_dynamic_variable(
        self, name: str, data: Any, function: Callable, **kwargs
    ) -> None:
        """Add a new dynamic variable.

        Parameters:
            name: Name of the variable.
            data: Data source for callable function.
            function: Function to calculate the dynamic variable.
            **kwargs: Additional attributes for the variable.
        """
        var = BaseDynamicVariable(
            obj=self,
            name=name,
            data=data,
            function=function,
            **kwargs,
        )
        self._dynamic_variables[name] = var

    def dynamic_var(self, attr_name: str) -> Any:
        """Get output of a dynamic variable.

        Parameters:
            attr_name: Dynamic variable's name.

        Returns:
            Dynamic variable value.
        """
        if self.time.tick in self._updated_ticks:
            return self._dynamic_variables[attr_name].cache
        return self._dynamic_variables[attr_name].now()


class BaseStateManager(ABC, StateManagerProtocol):
    """Base state manager implementation.

    Manages the lifecycle state of model components (NEW → INIT → READY → COMPLETE).

    Attributes:
        state: Current state of the component.
        opening: Whether the component is currently active.
    """

    def __init__(self) -> None:
        """Initialize state manager with NEW state."""
        self._state = State.NEW
        self._open = True

    @property
    def state(self) -> State:
        """Get module state.

        Returns:
            Current state.
        """
        return self._state

    @state.setter
    def state(self, state: State) -> None:
        """Set module state.

        Args:
            state: State to set.
        """
        self._state = state

    @property
    def opening(self) -> bool:
        """Check if module is active.

        Returns:
            True if module is active.
        """
        return self._open

    def set_state(self, state: State) -> None:
        """Set module state with validation.

        Args:
            state: State to set.

        Raises:
            ValueError: If trying to set same state or retreat to earlier state.
        """
        if state == self._state:
            raise ValueError(f"Setting state repeat: {self.state}!")
        if state < self._state:
            raise ValueError(f"State cannot retreat from {self.state} to {state}!")
        self._state = state

    def reset(self, opening: bool = True) -> None:
        """Reset module to NEW state.

        Args:
            opening: Whether module should be active after reset.
        """
        self._state = State.NEW
        self._open = opening

    def initialize(self) -> None:
        """Initialize module (override in subclasses)."""
        pass

    def setup(self) -> None:
        """Setup module (override in subclasses)."""
        pass

    def step(self) -> None:
        """Step module (override in subclasses)."""
        pass

    def end(self) -> None:
        """End module (override in subclasses)."""
        pass


class BaseModule(BaseModelElement, BaseStateManager, Observer, ModuleProtocol, ABC):
    """Base module implementation.

    Combines model element, state management, and observer capabilities.
    Provides lifecycle management with automatic wrapping of user methods.

    Attributes:
        model: Parent ABSESpy model.
        name: Module name.
        state: Current lifecycle state.
        opening: Whether module is active.
    """

    def __init__(
        self,
        model: MainModelProtocol,
        *,
        name: Optional[str] = None,
    ) -> None:
        """Initialize base module.

        Args:
            model: Parent ABSESpy model.
            name: Optional module name.
        """
        BaseModelElement.__init__(self, model, name)
        BaseStateManager.__init__(self)

    def __repr__(self) -> str:
        flag = "open" if self.opening else "closed"
        return f"<{self.name}: {flag}>"

    def __str__(self) -> str:
        return self.name

    @final
    def _initialize(self):
        """Internal initialization before handling parameters.

        Wraps user-defined methods to add lifecycle management.
        """
        # Wrap the user-defined step method
        self._user_setup = self.setup
        self.setup = self._setup
        self._user_step = self.step
        self.step = self._step
        self._user_end = self.end
        self.end = self._end
        self.set_state(State.INIT)
        self.initialize()

    @final
    def _setup(self, *args, **kwargs):
        """Internal setup after handling parameters.

        Args:
            *args: Positional arguments for user setup.
            **kwargs: Keyword arguments for user setup.
        """
        self._user_setup(*args, **kwargs)
        self.set_state(State.READY)

    @final
    def _step(self, *args, **kwargs):
        """Internal step method.

        Args:
            *args: Positional arguments for user step.
            **kwargs: Keyword arguments for user step.
        """
        self._user_step(*args, **kwargs)

    @final
    def _end(self, *args, **kwargs):
        """Internal end method.

        Args:
            *args: Positional arguments for user end.
            **kwargs: Keyword arguments for user end.
        """
        self._user_end(*args, **kwargs)
        self.set_state(State.COMPLETE)
