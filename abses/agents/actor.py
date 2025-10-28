#!/usr/bin/env python3
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
    Optional,
    Sequence,
    cast,
)

import mesa_geo as mg
import numpy as np
from shapely import Point
from shapely.geometry.base import BaseGeometry

from abses.core.base import BaseModelElement
from abses.core.protocols import ActorProtocol
from abses.human.links import _LinkNodeActor
from abses.utils.errors import ABSESpyError

if TYPE_CHECKING:
    from abses import MainModel
    from abses.core.types import GeoType, TargetName
    from abses.space.cells import PatchCell, Pos
    from abses.space.move import _Movements
    from abses.space.patch import PatchModule


def alive_required(method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that only executes the method when the actor is alive.

    This decorator wraps actor methods to check their alive status before execution.
    If the actor is not alive, the method returns None instead of executing. This
    provides a clean way to prevent operations on dead actors without explicit
    checks in every method.

    Parameters:
        method: The method to decorate. Should be a method of an Actor instance
            or an object with an 'actor' attribute.

    Returns:
        The decorated method that only executes when alive is True, otherwise
        returns None.

    Example:
        ```python
        class MyActor(Actor):
            @alive_required
            def do_something(self):
                # This method only executes if the actor is alive
                pass
        ```
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        actor = self if isinstance(self, Actor) else getattr(self, "actor")
        alive = actor.alive
        return method(self, *args, **kwargs) if alive else None

    return wrapper


def perception_result(name: str, result: Any, nodata: Any = 0.0) -> Any:
    """Clean and validate the result of a perception operation.

    This function ensures that perception results are scalar values, not iterables.
    It handles None values by replacing them with a specified nodata value, making
    perception results consistent and predictable.

    Parameters:
        name: The name of the perception being processed.
        result: The raw result from the perception operation.
        nodata: The value to return if the result is None. Defaults to 0.0.

    Returns:
        The cleaned perception result - either the original result if not None,
        or the nodata value if the result is None.

    Raises:
        ValueError: If the result is iterable. Perceptions should return scalar
            values only.
    """
    if hasattr(result, "__iter__"):
        raise ValueError(
            f"Perception result of '{name}' got type {type(result)} as return."
        )
    return nodata if result is None else result


def perception(
    decorated_func: Optional[Callable[..., Any]] = None, *, nodata: Optional[Any] = None
) -> Callable[..., Any]:
    """Decorator that transforms a method into a perception attribute.

    This decorator converts actor methods into perception methods that automatically
    handle None values and validate that results are scalar. It's designed for
    creating actor perception mechanisms in agent-based models where agents need
    to sense their environment.

    The decorator can be used with or without parameters. When used without parameters,
    it uses a default nodata value. When used with parameters, it allows customization
    of the nodata value.

    Parameters:
        decorated_func: The function to decorate. If None, returns a decorator function.
        nodata: The value to return if the perception result is None. Defaults to None,
            which will use 0.0 as the default in perception_result.

    Returns:
        Either the decorated function (if decorated_func is provided) or a decorator
        function (if decorated_func is None).

    Example:
        ```python
        class MyActor(Actor):
            @perception
            def see_food(self):
                # Returns scalar value or None
                return food_amount

            @perception(nodata=-1)
            def sense_danger(self):
                # Returns scalar value, or -1 if None
                return danger_level
        ```
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


class Actor(mg.GeoAgent, _LinkNodeActor, BaseModelElement, ActorProtocol):
    """Base actor class for agent-based models in ABSESpy.

    An Actor represents an autonomous agent in a social-ecological system. It combines
    geospatial capabilities (from mesa-geo), network functionality (links), and
    ABSESpy-specific features like perception and movement. Actors can be located
    on spatial cells, form networks with other actors, and interact with their
    environment through perceptions and actions.

    Actors maintain their own state including position, alive status, age, and custom
    attributes. They can move between cells, perceive their environment, form links
    with other actors, and execute custom behaviors through overridable methods.

    The Actor class serves as a base class for creating custom agent types. Users
    should inherit from Actor and override methods like `setup()` and `initialize()`
    to define agent-specific behaviors.

    Attributes:
        breed: The breed (type) of this actor, defaults to class name.
        layer: The spatial layer where the actor is located.
        indices: The grid indices of the cell where the actor is located.
        pos: The position of the cell where the actor is located.
        on_earth: Whether the actor is positioned on a spatial cell.
        at: The specific cell where the actor is located.
        link: Proxy for managing network links with other actors.
        move: Proxy for manipulating actor's spatial location.
        geometry: The shapely geometry representing the actor's spatial form.
        alive: Whether the actor is alive (not removed from the model).
        unique_id: Unique identifier automatically assigned by Mesa.
        crs: Coordinate reference system for the actor's geometry.

    Example:
        ```python
        class Farmer(Actor):
            def setup(self):
                self.wealth = 100

            def initialize(self):
                # Called at the start of simulation
                self.plant_crops()
        ```
    """

    def __init__(self, model: MainModel, observer: bool = True, **kwargs) -> None:
        """Initialize an actor instance.

        Parameters:
            model: The ABSESpy model this actor belongs to.
            observer: Whether this actor should be observed in data collection.
                Defaults to True.
            **kwargs: Additional keyword arguments:
                - crs: Coordinate reference system. Defaults to model's CRS.
                - geometry: Shapely geometry for the actor. Defaults to None.
        """
        BaseModelElement.__init__(self, model)
        crs = kwargs.pop("crs", model.nature.crs)
        geometry = kwargs.pop("geometry", None)
        mg.GeoAgent.__init__(self, model=model, geometry=geometry, crs=crs)
        _LinkNodeActor.__init__(self)
        self._cell: Optional[PatchCell] = None
        self._alive: bool = True
        self._birth_tick: int = self.time.tick
        self._setup()

    def __repr__(self) -> str:
        """Return a string representation of the actor."""
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
        """The shapely geometry of the actor.

        If the actor is located on a cell, returns a Point at the cell's coordinate.
        Otherwise, returns the actor's custom geometry if one was assigned.
        """
        if self._cell is not None:
            return Point(self._cell.coordinate)
        return self._geometry

    @geometry.setter
    def geometry(self, value: Optional[BaseGeometry]) -> None:
        """Set the actor's geometry.

        Parameters:
            value: A shapely geometry object or None.

        Raises:
            TypeError: If value is not a valid shapely geometry or None.
        """
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
        from abses.space.move import _Movements

        return _Movements(self)

    @alive_required
    def age(self) -> int:
        """Get the age of the actor in simulation ticks.

        Returns:
            The number of ticks since the actor was born (created).
        """
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
        # if attr in self.dynamic_variables:
        #     return self.dynamic_var(attr)
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
        """Remove the actor from the model.

        This is an alias for the `die()` method, providing a more generic interface
        for removing actors from the simulation.
        """
        self.die()

    def move_to(self, to: Any = "random", layer: Any = None) -> None:
        """Move actor to a location (wrapper for move.to).

        This method allows shuffle_do to be used with move operations.

        Args:
            to: Position to move to. Can be a PatchCell, Coordinate tuple, or "random".
            layer: Layer to move to. If None, uses actor's current layer if available.
        """
        self.move.to(to=to, layer=layer)

    @alive_required
    def die(self) -> None:
        """Kill the actor and remove it from the simulation.

        This method performs a complete cleanup of the actor by:
        1. Removing all network links with other actors
        2. Removing the actor from its spatial cell (if positioned)
        3. Removing the actor from the model's agent registry
        4. Setting the actor's alive status to False

        After calling this method, the actor should no longer be used.
        """
        self.link.clean()  # 从链接中移除
        if self.on_earth:  # 如果在地上，那么从地块上移除
            self.move.off()
        super().remove()  # 从总模型里移除
        self._alive = False  # 设置为死亡状态
        del self

    def _setup(self) -> None:
        """Internal method to trigger actor setup.

        This method is called automatically during actor initialization and
        invokes the user-overridable setup() method.
        """
        self.setup()

    def setup(self) -> None:
        """Setup method called when the actor is initialized.

        Override this method to define actor-specific initialization behavior.
        This method is called automatically when the actor is created, before
        the simulation starts. Use it to set initial attributes and state.

        Example:
            ```python
            class Farmer(Actor):
                def setup(self):
                    self.wealth = 100
                    self.crops = []
            ```
        """

    def moving(self, cell: PatchCell) -> Optional[bool]:
        """Callback called before the actor moves to a new cell.

        Override this method to implement movement validation logic. Return False
        to prevent the move, True to allow it, or None to use default behavior
        (allow the move).

        Parameters:
            cell: The target cell the actor is attempting to move to.

        Returns:
            - True: explicitly allow the move
            - False: prevent the move
            - None: use default behavior (allow the move)

        Example:
            ```python
            class Farmer(Actor):
                def moving(self, cell):
                    # Only allow moving to farmland cells
                    return cell.is_farmland
            ```
        """

    def initialize(self) -> None:
        """Initialize the actor at the start of simulation.

        Override this method to define behavior that should occur when the
        simulation begins (at tick 0), as opposed to when the actor is created.
        This is useful for setting up initial conditions that depend on the
        complete model state.

        Example:
            ```python
            class Farmer(Actor):
                def initialize(self):
                    # Find and establish initial links
                    self.find_neighbors()
            ```
        """
        ...

    def evaluate(
        self,
        candidates: Any,
        scorer: Callable[["Actor", Any], Any],
        *,
        dtype: Any | None = float,
        how: Optional[str] = None,
        preserve_position: bool = False,
        preserve_attrs: Optional[Sequence[str]] = None,
    ) -> Any:
        """Evaluate a scorer across candidates and optionally choose the best.

        Workflow:
        1) Normalize candidates to a sequence (ActorsList stays as-is)
        2) For each candidate: score with optional rollback of position/attrs
        3) Return scores (ndarray) or the best candidate per 'how' ('max'/'min')
        """
        from abses.agents.sequences import ActorsList  # local import

        # 1) Normalize candidates to a single representation
        is_actors_list = isinstance(candidates, ActorsList)
        seq = (
            candidates
            if is_actors_list
            else (
                list(candidates)
                if not isinstance(candidates, np.ndarray)
                else candidates
            )
        )

        # 2) Define scoring with rollback
        def _score_with_rollback(candidate: Any) -> Any:
            original_cell = self.at if preserve_position else None
            original_attrs: dict[str, Any] = {}
            if preserve_attrs:
                for attr in preserve_attrs:
                    original_attrs[attr] = getattr(self, attr)
            try:
                return scorer(self, candidate)
            finally:
                # restore attributes
                for attr, val in original_attrs.items():
                    setattr(self, attr, val)
                # restore position
                if (
                    preserve_position
                    and original_cell is not None
                    and self.at is not original_cell
                ):
                    self.move.to(original_cell)

        # 3) Compute scores via a single code path
        if is_actors_list:
            scores = np.asarray(
                seq.apply(lambda c: _score_with_rollback(c)), dtype=dtype
            )
        else:
            scores = np.asarray([_score_with_rollback(c) for c in seq], dtype=dtype)

        if how is None:
            return scores
        if len(scores) == 0:
            return None
        idx = int(np.argmax(scores)) if how == "max" else int(np.argmin(scores))
        return seq[idx] if not is_actors_list else seq[idx]
