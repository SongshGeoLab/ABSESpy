#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Core type aliases for ABSESpy.

This module contains all type aliases used throughout ABSESpy.
It has no dependencies on other abses modules to avoid circular imports.
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    TypeAlias,
    Union,
)

# Basic type aliases that don't depend on any ABSESpy modules
AgentID: TypeAlias = Union[str, int]
UniqueID: TypeAlias = Union[str, int]
UniqueIDs: TypeAlias = List[Optional[UniqueID]]
Position: TypeAlias = Tuple[float, float]
Pos: TypeAlias = Tuple[int, int]
Number: TypeAlias = Union[int, float]

# Geometry and spatial types
GeometryType: TypeAlias = Literal["Point", "Shape"]
GeoType: TypeAlias = Literal["Point", "Shape"]

# Model component types
SubSystemName: TypeAlias = Literal["model", "nature", "human"]
HowCheckName: TypeAlias = Literal["unique", "exists"]

# Selection and filtering
Selection: TypeAlias = Union[str, Iterable[bool], Dict[str, Any]]
HOW_TO_SELECT: TypeAlias = Literal["only", "item"]
WHEN_EMPTY: TypeAlias = Literal["raise exception", "return None"]

# Link and network types
Direction: TypeAlias = Optional[Literal["in", "out"]]
TargetName: TypeAlias = Union[Literal["cell", "actor", "self"], str]

# Trigger types
Trigger: TypeAlias = Union[Callable, str]
Breeds: TypeAlias = Union[str, List[str], Tuple[str, ...]]
