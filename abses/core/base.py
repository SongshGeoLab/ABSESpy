#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Base classes for ABSESpy components.

This module re-exports base classes from specialized modules for backward compatibility.
The actual implementations have been split into:
- base_variable.py: Variable and DynamicVariable
- base_observable.py: Observer and Observable
- base_module.py: ModelElement, StateManager, Module
- base_subsystem.py: SubSystem

Import from this module for backward compatibility, or import directly from
the specialized modules for better code organization.
"""

from __future__ import annotations

# Re-export all base classes for backward compatibility
from abses.core.base_module import (
    BaseModelElement,
    BaseModule,
    BaseStateManager,
)
from abses.core.base_observable import (
    BaseObservable,
    BaseObserver,
)
from abses.core.base_subsystem import BaseSubSystem
from abses.core.base_variable import (
    BaseDynamicVariable,
    BaseVariable,
)

# Also export protocol classes and enums that were previously imported from base
from abses.core.primitives import State
from abses.core.protocols import ModelElement

__all__ = [
    # Variables
    "BaseVariable",
    "BaseDynamicVariable",
    # Observer pattern
    "BaseObserver",
    "BaseObservable",
    # Model elements
    "BaseModelElement",
    "BaseStateManager",
    "BaseModule",
    "ModelElement",
    # Subsystems
    "BaseSubSystem",
    # State
    "State",
]
