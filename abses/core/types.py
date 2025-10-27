#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Define the core types of ABSESpy.

This module contains TypeVars and complex type definitions that depend on protocols.
Simple type aliases are in type_aliases.py to avoid circular imports.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    TypeAlias,
    TypeVar,
)

# Re-export common type aliases for backward compatibility

if TYPE_CHECKING:
    from datetime import datetime

    import numpy as np
    import xarray as xr
    from pendulum import DateTime
    from shapely import Geometry

    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList
    from abses.core.protocols import (
        ActorProtocol,
        HumanSystemProtocol,
        LinkNodeProtocol,
        MainModelProtocol,
        ModuleProtocol,
        NatureSystemProtocol,
        PatchCellProtocol,
    )
    from abses.space.cells import PatchCell

    # Type variables bound to protocols (only used for type checking)
    ComponentType = TypeVar("ComponentType", bound=ModuleProtocol)
    ModelType = TypeVar("ModelType", bound=MainModelProtocol)
    T = TypeVar("T", bound=PatchCellProtocol)
    N = TypeVar("N", bound=NatureSystemProtocol)
    H = TypeVar("H", bound=HumanSystemProtocol)
    A = TypeVar("A", bound=ActorProtocol)
    Link = TypeVar("Link", bound=LinkNodeProtocol)

    # Complex type aliases that depend on concrete classes
    Raster: TypeAlias = np.ndarray | xr.DataArray | xr.Dataset
    CellFilter: TypeAlias = (
        str | np.ndarray | xr.DataArray | Geometry | Dict[str, Any] | None
    )
    ActorTypes: TypeAlias = type[Actor] | list[type[Actor]]
    Actors: TypeAlias = Actor | ActorsList | list[Actor]
    DateOrTick: TypeAlias = DateTime | int
    DateTimeOrStr: TypeAlias = datetime | str
    LinkingNode: TypeAlias = Actor | PatchCell
    AttrGetter: TypeAlias = Link | ActorsList[Link]

    # Built-in targets
    __built_in_targets__: tuple[str, str] = ("cell", "actor")


# Re-export TypeVars when not type checking (for runtime use)
# These are not bound to avoid circular imports at runtime
ComponentType = TypeVar("ComponentType")
ModelType = TypeVar("ModelType")
T = TypeVar("T")
N = TypeVar("N")
H = TypeVar("H")
A = TypeVar("A")
Link = TypeVar("Link")
