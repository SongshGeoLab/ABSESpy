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
    HumanSystemProtocol,
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

# 容器相关类型
if TYPE_CHECKING:
    import numpy as np
    import xarray as xr
    from shapely import Geometry

    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList

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

    SubSystemType: TypeAlias = Literal["model", "nature", "human"]
