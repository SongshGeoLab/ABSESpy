#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
In `ABSESpy`, agents are also known as 'Actors'.
"""

from __future__ import annotations

from functools import cached_property, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
)

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

import mesa_geo as mg
from shapely import Point
from shapely.geometry.base import BaseGeometry

from abses._bases.errors import ABSESpyError
from abses._bases.objects import _BaseObj
from abses.links import TargetName, _LinkNodeActor

if TYPE_CHECKING:
    from abses.cells import PatchCell, Pos
    from abses.main import MainModel
    from abses.move import _Movements
    from abses.nature import PatchModule


Selection: TypeAlias = Union[str, Iterable[bool]]
Trigger: TypeAlias = Union[Callable, str]
Breeds: TypeAlias = Union[str, List[str], Tuple[str]]
GeoType: TypeAlias = Literal["Point", "Shape"]


def alive_required(method):
    """
    A decorator that only executes the method when the object's alive attribute is True.

    Args:
        method: The method to decorate.

    Returns:
        The decorated method that only executes when alive is True.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        actor = self if isinstance(self, Actor) else getattr(self, "actor")
        alive = actor.alive
        return method(self, *args, **kwargs) if alive else None

    return wrapper


def perception_result(name, result, nodata: Any = 0.0) -> Any:
    """
    Clean the result of a perception.

    Args:
        name: The name of the perception.
        result: The result of the perception.
        nodata: The value to return if the result is None.

    Returns:
        The cleaned perception result.

    Raises:
        ValueError: If the result is iterable.
    """
    if hasattr(result, "__iter__"):
        raise ValueError(
            f"Perception result of '{name}' got type {type(result)} as return."
        )
    return nodata if result is None else result


def perception(
    decorated_func: Optional[Callable[..., Any]] = None, *, nodata: Optional[Any] = None
) -> Callable[..., Any]:
    """
    Change the decorated function into a perception attribute.

    Args:
        decorated_func: The decorated function.
        nodata: The value to return if the result is None.

    Returns:
        The decorated perception attribute or a decorator.
    """

    def decorator(func) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: Actor, *args, **kwargs) -> Callable[..., Any]:
            result = func(self, *args, **kwargs)
            return perception_result(func.__name__, result, nodata=nodata)

        return wrapper

    # 检查是否有参数传递给装饰器，若没有则返回装饰器本身
    return (
        decorator(decorated_func)
        if decorated_func
        else cast(Callable[..., Any], decorator)
    )


class Actor(mg.GeoAgent, _BaseObj, _LinkNodeActor):
    """
    An actor in a social-ecological system (or "Agent" in an agent-based model.)

    Attributes:
        breed: The breed of this actor (by default, class name).
        layer: The layer where the actor is located.
        indices: The indices of the cell where the actor is located.
        pos: The position of the cell where the actor is located.
        on_earth: Whether the actor is standing on a cell.
        at: The cell where the actor is located.
        link: The link manipulating proxy.
        move: The movement manipulating proxy.

    Methods:
        get:
            Gets the value of an attribute from the actor or its cell.
        set:
            Sets the value of an attribute on the actor or its cell.
        die:
            Kills the actor.
    """

    def __init__(
        self, model: MainModel[Any, Any], observer: bool = True, **kwargs
    ) -> None:
        _BaseObj.__init__(self, model, observer=observer)
        crs = kwargs.pop("crs", model.nature.crs)
        geometry = kwargs.pop("geometry", None)
        mg.GeoAgent.__init__(self, model=model, geometry=geometry, crs=crs)
        _LinkNodeActor.__init__(self)
        self._cell: Optional[PatchCell] = None
        self._alive: bool = True
        self._birth_tick: int = self.time.tick
        self._setup()

    def __repr__(self) -> str:
        return f"<{self.breed} [{self.unique_id}]>"

    @property
    def geo_type(self) -> Optional[GeoType]:
        """The type of the geo info."""
        if self.geometry is None:
            return None
        if isinstance(self.geometry, Point):
            return "Point"
        return "Shape"

    @property
    def geometry(self) -> Optional[BaseGeometry]:
        """The geometry of the actor."""
        if self._cell is not None:
            return Point(self._cell.coordinate)
        return self._geometry

    @geometry.setter
    def geometry(self, value: Optional[BaseGeometry]) -> None:
        if not isinstance(value, BaseGeometry) and value is not None:
            raise TypeError(f"{value} is not a valid geometry.")
        self._geometry = value

    @property
    def alive(self) -> bool:
        """Whether the actor is alive."""
        return self._alive

    @property
    def layer(self) -> Optional[PatchModule]:
        """Get the layer where the actor is located."""
        return None if self._cell is None else self._cell.layer

    @property
    def on_earth(self) -> bool:
        """Whether agent stands on a cell."""
        return bool(self.geometry)

    @property
    def at(self) -> PatchCell | None:
        """Get the cell where the agent is located."""
        return self._cell if self._cell is not None else None

    @at.setter
    def at(self, cell: PatchCell) -> None:
        """Set the cell where the actor is located."""
        if self not in cell.agents:
            raise ABSESpyError(
                "Cannot set location directly because the actor is not added to the cell."
            )
        self._cell = cell
        self.crs = cell.crs

    @at.deleter
    def at(self) -> None:
        """Remove the agent from the located cell."""
        self._cell = None

    @property
    def pos(self) -> Optional[Pos]:
        """Position of the actor."""
        return None if self.at is None else self.at.pos

    @pos.setter
    def pos(self, value) -> None:
        if value is not None:
            raise ABSESpyError(
                "Set position is not allowed."
                "Please use `move.to()` to move the actor to a cell."
            )

    @property
    def indices(self) -> Optional[Pos]:
        """Indices of the actor."""
        return None if self.at is None else self.at.indices

    @cached_property
    def move(self) -> _Movements:
        """A proxy for manipulating actor's location.

        1. `move.to()`: moves the actor to another cell.
        2. `move.off()`: removes the actor from the current layer.
        3. `move.by()`: moves the actor by a distance.
        4. `move.random()`: moves the actor to a random cell.
        """
        from abses.move import _Movements

        return _Movements(self)

    @alive_required
    def age(self) -> int:
        """Get the age of the actor."""
        return self.time.tick - self._birth_tick

    @alive_required
    def get(
        self, attr: str, target: Optional[TargetName] = None, default: Any = ...
    ) -> Any:
        """
        Gets attribute value from target.

        Args:
            attr: The name of the attribute to get.
            target: The target to get the attribute from.
                If None, the agent itself is the target.
                If the target is an agent, get the attribute from the agent.
                If the target is a cell, get the attribute from the cell.
            default: Default value if attribute not found.

        Returns:
            The value of the attribute.
        """
        if attr in self.dynamic_variables:
            return self.dynamic_var(attr)
        return super().get(attr=attr, target=target, default=default)

    @alive_required
    def set(self, *args, **kwargs) -> None:
        """
        Sets the value of an attribute.

        Args:
            attr: The name of the attribute to set.
            value: The value to set the attribute to.
            target: The target to set the attribute on. If None, the agent itself is the target.
                1. If the target is an agent, set the attribute on the agent.
                2. If the target is a cell, set the attribute on the cell.

        Raises:
            TypeError: If the attribute is not a string.
            ABSESpyError: If the attribute is protected.
        """
        super().set(*args, **kwargs)

    def remove(self) -> None:
        """Remove the actor from the model."""
        self.die()

    @alive_required
    def die(self) -> None:
        """Kills the agent (self)"""
        self.link.clean()  # 从链接中移除
        if self.on_earth:  # 如果在地上，那么从地块上移除
            self.move.off()
        super().remove()  # 从总模型里移除
        self._alive = False  # 设置为死亡状态
        del self

    def _setup(self) -> None:
        """Setup the actor."""
        self.setup()

    def setup(self) -> None:
        """Overwrite this method.
        It should be called when the actor is initialized.
        """

    def moving(self, cell: PatchCell) -> Optional[bool]:
        """
        Called when the actor is about to move.

        Args:
            cell: The target cell to move to.

        Returns:
            Optional boolean indicating whether the actor can move to the cell.
            If None, the move is allowed by default.
        """
