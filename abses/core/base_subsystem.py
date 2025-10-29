#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Base classes for subsystems in ABSESpy.

This module contains the base implementation for subsystems (Nature/Human).
"""

from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from abses.core.base_module import BaseModule
from abses.core.primitives import State
from abses.core.protocols import (
    ActorsListProtocol,
    AgentsContainerProtocol,
    MainModelProtocol,
    SubSystemProtocol,
)
from abses.utils.func import iter_apply_func_to


class BaseSubSystem(BaseModule, SubSystemProtocol, ABC):
    """Base subsystem implementation.

    Manages a collection of modules and provides access to agents.
    Subsystems (Nature and Human) organize related modules and coordinate
    their lifecycle.

    Attributes:
        model: Parent ABSESpy model.
        modules: Dictionary of module name to module instance.
        major_layer: The primary/default layer for this subsystem.
        agents: All agents in the model.
        actors: Agents currently on the earth (in cells).
        opening: Whether any module in subsystem is active.
        is_empty: Whether subsystem has no modules.
    """

    def __init__(self, model: MainModelProtocol, name: Optional[str] = None) -> None:
        """Initialize base subsystem.

        Args:
            model: Parent ABSESpy model.
            name: Optional subsystem name.
        """
        super().__init__(model, name=name)
        self._modules: dict[str, BaseModule] = {}
        self._major_layer: Optional[BaseModule] = None

    @property
    def agents(self) -> AgentsContainerProtocol:
        """Get all agents in the subsystem.

        Returns:
            Agents container from the model.
        """
        return self.model.agents

    @property
    def actors(self) -> ActorsListProtocol:
        """Get all actors (agents on earth).

        Returns:
            List of agents currently in patch cells.
        """
        return self.agents.select("on_earth")

    @property
    def modules(self) -> dict[str, BaseModule]:
        """Get all modules in this subsystem.

        Returns:
            Dictionary mapping module names to module instances.
        """
        return self._modules

    @property
    def opening(self) -> bool:
        """Check if subsystem is active.

        A subsystem is active if any of its modules are active.

        Returns:
            True if any module is active.
        """
        return any(module.opening for module in self.modules.values())

    @property
    def is_empty(self) -> bool:
        """Check if subsystem is empty.

        Returns:
            True if subsystem has no modules.
        """
        return len(self.modules) == 0

    @iter_apply_func_to("modules")
    def set_state(self, state: State):
        """Set state for subsystem and all modules.

        Args:
            state: State to set.

        Returns:
            Result of parent set_state call.
        """
        return super().set_state(state)

    @iter_apply_func_to("modules")
    def _initialize(self):
        """Initialize subsystem and all modules."""
        self.initialize()
        super().set_state(State.INIT)

    @iter_apply_func_to("modules")
    def _setup(self):
        """Setup subsystem and all modules."""
        self.setup()
        super().set_state(State.READY)

    @iter_apply_func_to("modules")
    def _step(self):
        """Step subsystem and all modules."""
        self.step()

    @iter_apply_func_to("modules")
    def _end(self):
        """End subsystem and all modules."""
        self.end()
        super().set_state(State.COMPLETE)

    def __repr__(self) -> str:
        flag = "open" if self.opening else "closed"
        return f"<{self.name} ({str(self.major_layer)}): {flag}>"

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to modules or major_layer when not found.

        Args:
            name: Name of the attribute being accessed.

        Returns:
            Value of the attribute from modules dict or major_layer.

        Raises:
            AttributeError: If attribute not found in modules or major layer.
        """
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            # First, check if it's a module name
            if name in self._modules:
                return self._modules[name]

            # Then, try to delegate to major_layer if it exists
            if self._major_layer is None:
                raise AttributeError(
                    f"Attribute '{name}' not found in {self.__class__.__name__},"
                    "and no major layer is set."
                ) from e
            try:
                return getattr(self._major_layer, name)
            except AttributeError as e2:
                raise AttributeError(
                    f"Attribute '{name}' not found in either {self.__class__.__name__} or major layer ({self._major_layer.name})"
                ) from e2

    @property
    def major_layer(self) -> Optional[BaseModule]:
        """Get primary raster layer of the subsystem.

        Returns:
            The current major layer, or None if not set.
        """
        return self._major_layer

    @major_layer.setter
    def major_layer(self, layer: BaseModule) -> None:
        """Set the major layer for this subsystem.

        Args:
            layer: Module instance to set as major layer.

        Raises:
            ValueError: If layer is not in this subsystem or not a BaseModule.
        """
        if not isinstance(layer, BaseModule):
            raise ValueError(f"{layer} is not a valid BaseModule.")
        if layer.name not in self.modules:
            raise ValueError(f"{layer} is not in {self}.")
        self._major_layer = layer

    def add_module(self, module: BaseModule):
        """Add a module to the subsystem.

        Args:
            module: Module to add.

        Returns:
            The added module.
        """
        was_empty = bool(self.is_empty)
        # check name
        self.model.add_name(module.name, check="unique")
        # attach to model
        self.attach(module)
        # add to modules dict
        self.modules[module.name] = module
        if was_empty:
            self.major_layer = module
        return module

    @abstractmethod
    def create_module(
        self,
        module_cls: Type[BaseModule],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Create a module and add it to the subsystem.

        Args:
            module_cls: Module class to instantiate.
            *args: Positional arguments for module constructor.
            **kwargs: Keyword arguments for module constructor.

        Returns:
            Created module instance.
        """
        # Backward compatibility: support deprecated 'how' argument from 0.7.x
        # The 'how' parameter used to determine the creation method. It is no longer
        # needed in >=0.8.0 and will be ignored with a deprecation warning.
        if "how" in kwargs:
            _ = kwargs.pop("how")
            warnings.warn(
                (
                    "Argument 'how' is deprecated and will be removed in a future "
                    "version. It is no longer used when creating modules. "
                    "Please remove 'how' from your call to create_module()."
                ),
                DeprecationWarning,
                stacklevel=2,
            )

        module = module_cls(model=self.model, *args, **kwargs)
        self.add_module(module)
        return module
