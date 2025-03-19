#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Define the core types of ABSESpy.

This module contains the core types of ABSESpy.
Including:
- time driver
- dynamic variable
- observer
- observable
- model element
- model component
- sub system
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

from abses.core.protocols import (
    ActorProtocol,
    HumanSystemProtocol,
    LinkNodeProtocol,
    MainModelProtocol,
    ModuleProtocol,
    NatureSystemProtocol,
    PatchCellProtocol,
)

# Type definitions
ComponentType = TypeVar("ComponentType", bound=ModuleProtocol)
ModelType = TypeVar("ModelType", bound=MainModelProtocol)
T = TypeVar("T", bound=PatchCellProtocol)
N = TypeVar("N", bound=NatureSystemProtocol)
H = TypeVar("H", bound=HumanSystemProtocol)
A = TypeVar("A", bound=ActorProtocol)
Link = TypeVar("Link", bound=LinkNodeProtocol)

# 容器相关类型
if TYPE_CHECKING:
    from datetime import datetime

    import numpy as np
    import xarray as xr
    from pendulum import DateTime
    from shapely import Geometry

    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList
    from abses.space.cells import PatchCell

    AgentID: TypeAlias = Union[str, int]
    Position: TypeAlias = Tuple[float, float]
    GeometryType: TypeAlias = Literal["Point", "Shape"]
    HowCheckName: TypeAlias = Literal["unique", "exists"]
    Raster: TypeAlias = Union[
        np.ndarray,
        xr.DataArray,
        xr.Dataset,
    ]
    # 将所有类型定义移到这里
    CellFilter: TypeAlias = Optional[str | np.ndarray | xr.DataArray | Geometry]
    ActorTypes: TypeAlias = Union[Type[Actor], Iterable[Type[Actor]]]
    Actors: TypeAlias = Union[Actor, ActorsList, Iterable[Actor]]
    UniqueID: TypeAlias = Union[str, int]
    UniqueIDs: TypeAlias = List[Optional[UniqueID]]

    SubSystemName: TypeAlias = Literal["model", "nature", "human"]
    DateOrTick: TypeAlias = DateTime | int
    DateTimeOrStr: TypeAlias = Union[datetime, str]

    Trigger: TypeAlias = Union[Callable, str]
    Breeds: TypeAlias = Union[str, List[str], Tuple[str]]
    GeoType: TypeAlias = Literal["Point", "Shape"]

    Selection: TypeAlias = Union[str, Iterable[bool], Dict[str, Any]]
    HOW_TO_SELECT: TypeAlias = Literal["only", "item"]
    WHEN_EMPTY: TypeAlias = Literal["raise exception", "return None"]

    LinkingNode: TypeAlias = Actor | PatchCell
    Direction: TypeAlias = Optional[Literal["in", "out"]]
    __built_in_targets__: Tuple[str, str] = ("cell", "actor")
    TargetName: TypeAlias = Union[Literal["cell", "actor", "self"], str]
    AttrGetter: TypeAlias = Union["Link", ActorsList["Link"]]
    Pos: TypeAlias = Tuple[int, int]
    Number: TypeAlias = Union[int, float]
