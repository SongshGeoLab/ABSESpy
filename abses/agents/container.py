#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Container for actors.
"""

from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Type,
    Union,
    cast,
)

import geopandas as gpd
import pyproj
from loguru import logger
from mesa import Model
from mesa.agent import AgentSet
from shapely.geometry.base import BaseGeometry

from abses.agents.actor import Actor
from abses.agents.sequences import ActorsList
from abses.core.protocols import ActorProtocol, MainModelProtocol
from abses.utils.errors import ABSESpyError
from abses.utils.func import IncludeFlag, clean_attrs
from abses.utils.random import ListRandom

if TYPE_CHECKING:
    from abses.core.types import Breeds, Number
    from abses.space.cells import PatchCell


class _AgentsContainer:
    """Base container for managing agents in ABSESpy models.

    This class provides a unified interface for managing actors (agents) within
    a model. It offers functionality for creating, accessing, filtering, and
    removing agents, as well as querying agent collections by breed types.
    The container integrates with Mesa's agent management system while providing
    additional ABSESpy-specific features like breed-based selection and spatial
    awareness through CRS support.

    The container supports various access patterns including iteration, indexing
    by breed, and filtering by attributes. It can optionally enforce capacity
    limits on the number of agents it can hold.

    Attributes:
        model: The ABSESpy model this container belongs to.
        crs: Coordinate reference system for spatial operations.
        random: Random number generator for stochastic operations.
        is_full: Whether the container has reached its capacity limit.
        is_empty: Whether the container contains no agents.
    """

    def __init__(self, model: MainModelProtocol, max_len: None | Number = None):
        if not isinstance(model, Model):
            raise TypeError(f"{model} is not a Mesa Model.")
        self._model: MainModelProtocol = model
        self._agents = model._all_agents
        self._max_length = max_len

    def __getattr__(self, name: str) -> Any:
        """Get an attribute from the container."""
        if not name.startswith("_") and hasattr(self._agents, name):
            return getattr(self._agents, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __len__(self) -> int:
        """Return the number of agents in the container."""
        return len(self._agents)

    def __str__(self) -> str:
        """Return a string representation of the container."""
        return f"<Handling [{len(self)}]Agents for {self.model.name}>"

    def __contains__(self, actor: object) -> bool:
        """Check if an actor is in the container."""
        return actor in self._agents

    def __iter__(self) -> Iterator[ActorProtocol]:
        """Iterate over all actors in the container."""
        return iter(self._agents)

    def __getitem__(self, breeds: Optional[Breeds]) -> ActorsList[ActorProtocol]:
        """Get agents by breed(s).

        Args:
            breeds: Single breed (str or Type) or list of breeds to retrieve

        Returns:
            AgentSet containing all agents of the specified breed(s)

        Example:
            container['Breed1']  # by string name
            container[Breed1]    # by class type
            container[['Breed1', 'Breed2']]  # multiple breeds by name
            container[[Breed1, Breed2]]      # multiple breeds by type
        """
        if isinstance(breeds, (list, tuple)):
            # 对多个 breeds 进行合并
            agents: list[ActorProtocol] = []
            for breed in breeds:
                breed_type = self._get_breed_type(breed)
                agents.extend(self._model.agents_by_type.get(breed_type, []))
            return ActorsList(model=self.model, objs=agents)

        # 单个 breed 的情况
        if not isinstance(breeds, (str, type)):
            raise TypeError(f"{breeds} is not a string or a type.")
        breed_type = self._get_breed_type(breeds)
        try:
            return ActorsList(
                model=self.model, objs=self._model.agents_by_type[breed_type]
            )
        except KeyError:
            return ActorsList(model=self.model, objs=[])

    @property
    def crs(self) -> pyproj.CRS:
        """Returns the current CRS."""
        return self._model.nature.crs

    @property
    def model(self) -> MainModelProtocol:
        """The ABSESpy model where the container belongs to."""
        return self._model

    @property
    def random(self) -> ListRandom:
        """The random number generator."""
        return ListRandom(actors=self, model=self.model)

    @property
    def is_full(self) -> bool:
        """Whether the container is full."""
        return False if self._max_length is None else len(self) >= self._max_length

    @property
    def is_empty(self) -> bool:
        """Check whether the container is empty."""
        return len(self) == 0

    def _get_breed_type(self, breed: str | Type[ActorProtocol]) -> Type[ActorProtocol]:
        """Convert breed name to breed type if necessary."""
        if isinstance(breed, str):
            # 如果是字符串，在已注册的类型中查找对应名称的类
            for breed_type in self._model.agents_by_type.keys():
                if breed_type.__name__ == breed:
                    return breed_type
            raise ABSESpyError(f"Breed '{breed}' not found")
        return breed

    def _check_full(self) -> None:
        """检查容器是否已满。

        Raises:
            ABSESpyError: 如果容器已满或模型容器已满
        """
        if self.is_full:
            raise ABSESpyError(f"{self} is full.")
        if self.model.agents.is_full:
            raise ABSESpyError(f"{self.model.agents} is full.")

    def add(self, agent: ActorProtocol) -> None:
        """Add one agent to the container.

        Parameters:
            agent: The agent to add to the container.

        Raises:
            ABSESpyError: If the container or model container is full.
        """
        self._check_full()
        self._add_one(agent)

    def _add_one(self, agent: ActorProtocol) -> None:
        """Internal method to add one agent to the underlying storage.

        Parameters:
            agent: The agent to add.
        """
        self._agents.add(agent)

    def _new_one(
        self,
        geometry: Optional[BaseGeometry] = None,
        agent_cls: Type[ActorProtocol] = ActorProtocol,
        **kwargs,
    ) -> ActorProtocol:
        """Create a new agent.

        Args:
            geometry: Optional geometry for the agent
            agent_cls: The agent class to create, must implement ActorProtocol
            **kwargs: Additional arguments to pass to the agent constructor

        Returns:
            A new agent instance
        """
        if geometry and not isinstance(geometry, BaseGeometry):
            raise TypeError("Geometry must be a Shapely Geometry")

        # 检查是否实现了 ActorProtocol
        if not isinstance(agent_cls, type):
            raise ABSESpyError(f"{agent_cls} is not a type")

        agent = agent_cls(
            model=self.model, geometry=geometry, crs=self.model.nature.crs, **kwargs
        )
        self.add(agent)
        return agent

    def new(
        self,
        breed_cls: Type[ActorProtocol] = Actor,
        num: Optional[int] = None,
        singleton: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[ActorProtocol, ActorsList[ActorProtocol]]:
        """Create one or more actors of the given breed class.

        Parameters:
            breed_cls:
                The breed class of the actor(s) to create. Defaults to `ActorProtocol`.
            num:
                The number of actors to create. Only positive integer is allowed.
                Defaults to None, which will be set to 1 and singleton to True.
            singleton (bool, optional):
                Whether to create a singleton actor.
                If singleton is True, the return value will be an actor instance.
                Otherwise, it will be an `AgentSet` instance.
                Defaults to False.
                If `num` is None, this parameter will be ignored.
            **kwargs:
                Additional keyword arguments to pass to the actor constructor.

        Returns:
            The created actor(s).

        Example:
            ```python
            from abses import ActorProtocol, MainModel
            model = MainModel()
            actor = model.agents.new(singleton=True)
            >>> type(actor)
            >>> ActorProtocol

            actors = model.agents.new(singleton=False)
            >>> type(actors)
            >>> ActorsList
            ```
        """
        # create actors.
        if num is None:
            num = 1
            if singleton is None:
                singleton = True
        if not isinstance(num, int) or num < 0:
            raise ValueError(
                f"Number of actors to create must be a non-negative integer. Got {num}."
            )
        if num == 0:
            return ActorsList(model=self.model, objs=[])
        # 创建主体
        objs = []
        for _ in range(num):
            agent = self._new_one(agent_cls=breed_cls, **kwargs)
            objs.append(agent)
        # return the created actor(s).
        actors_list: ActorsList[ActorProtocol] = ActorsList(model=self.model, objs=objs)
        logger.debug(f"{self} created {num} {breed_cls.__name__}.")
        return (
            cast(ActorProtocol, actors_list.item())
            if singleton is True
            else actors_list
        )

    def remove(self, agent: ActorProtocol) -> None:
        """Remove the given agent from the container.

        Parameters:
            agent: The agent to remove from the container.

        Raises:
            ABSESpyError: If the agent is still located on earth (has a spatial position).
                Use `agent.remove()` to properly remove agents with spatial positions.
        """
        if agent.on_earth:
            raise ABSESpyError(
                f"{agent} is still on the earth. Use `agent.remove()` instead."
            )
        self._model.deregister_agent(agent)

    def has(self, breeds: Optional[Breeds] = None) -> int:
        """Whether the container has the breed of agents.

        Parameters:
            breeds:
                The breed(s) of agents to search.

        Returns:
            int:
                The number of agents of the specified breed(s).

        Example:
            ```python
            from abses import ActorProtocol, MainModel

            class Actor1(ActorProtocol):
                # breed 1
                pass

            class Actor2(ActorProtocol):
                # breed 2
                pass

            model = MainModel()
            model.agents.new(ActorProtocol, singleton=True)
            model.agents.new(Actor1, num=2)
            model.agents.new(Actor2, num=3)

            model.agents.has('Actor1')
            >>> 2
            model.agents.has(['Actor1', 'Actor2'])
            >>> 5
            ```
        """
        if breeds is None:
            return len(self)
        if isinstance(breeds, (str, type)):
            return len(self.select(agent_type=breeds))
        if isinstance(breeds, (list, tuple)):
            return sum(len(self.select(agent_type=breed)) for breed in breeds)
        raise TypeError(f"{breeds} is not a valid breed.")

    def select(
        self,
        selection: Callable | str | Dict[str, Any] | None = None,
        agent_type: Optional[Type[ActorProtocol] | str] = None,
        **kwargs: Any,
    ) -> ActorsList:
        """Select actors that match the given selection criteria.

        This method provides flexible filtering of agents based on various criteria.
        Selection can be done by attribute names (string), custom filter functions
        (callable), or attribute-value pairs (dictionary). Results can be further
        constrained by agent type (breed) and quantity limits.

        Parameters:
            selection:
                The selection criteria. Can be:
                - A string: selects agents where the attribute equals True
                - A callable: custom filter function taking an agent and returning bool
                - A dictionary: selects agents where attributes match the key-value pairs
                - None: selects all agents (subject to agent_type filtering)
            agent_type:
                Filter by agent breed type. Can be either a class type or string name.
            **kwargs:
                Additional arguments to pass to the `AgentSet.select()` method:
                - at_most (int | float, optional): The maximum amount of agents to select.
                  - If an integer, at most the first number of matching agents are selected.
                  - If a float between 0 and 1, at most that fraction of agents are selected.
                - inplace (bool, optional): If True, modifies the current AgentSet;
                  otherwise, returns a new AgentSet. Defaults to False.
                - n (int): deprecated, use at_most instead

        Returns:
            An ActorsList containing the selected agents.

        Raises:
            TypeError: If selection criteria is not a valid type.
        """
        if isinstance(agent_type, (str, type)):
            kwargs["agent_type"] = self._get_breed_type(agent_type)

        def check_attr(agent, attr, value=True):
            return getattr(agent, attr) == value

        if isinstance(selection, str):
            filter_func = partial(check_attr, attr=selection, value=True)
            agents_set = self._agents.select(filter_func=filter_func, **kwargs)
        elif any([callable(selection), selection is None]):
            agents_set = self._agents.select(filter_func=selection, **kwargs)
        elif isinstance(selection, dict):
            agents_set = self._agents
            for attr, value in selection.items():
                filter_func = partial(check_attr, attr=attr, value=value)
                agents_set = agents_set.select(filter_func=filter_func, **kwargs)
        else:
            raise TypeError(f"{selection} is not valid selection criteria.")
        return ActorsList(model=self.model, objs=agents_set)


class _ModelAgentsContainer(_AgentsContainer):
    """Specialized container for agents in the main model with GeoDataFrame support.

    This container extends the base agent container with additional functionality
    for creating agents from geospatial data sources. It provides methods to
    instantiate agents from GeoDataFrames while handling coordinate reference
    system (CRS) transformations and attribute mapping.

    The container ensures that all geospatial data is properly aligned with the
    model's coordinate system before creating agents, maintaining spatial consistency
    across the entire model.
    """

    def _check_crs(self, gdf: gpd.GeoDataFrame) -> bool:
        """Check and align the GeoDataFrame's CRS with the model's CRS.

        This method ensures that the input GeoDataFrame uses the same coordinate
        reference system as the model. If the GeoDataFrame has a different CRS,
        it will be transformed. If it has no CRS, the model's CRS will be assigned.

        Parameters:
            gdf: The GeoDataFrame to check and potentially transform.

        Returns:
            True if the CRS alignment was successful, False otherwise.

        Note:
            This method modifies the GeoDataFrame in-place.
        """
        if gdf.crs:
            gdf.to_crs(self.crs, inplace=True)
        else:
            gdf.set_crs(self.crs, inplace=True)
        return self.crs == gdf.crs

    def new_from_gdf(
        self,
        gdf: gpd.GeoDataFrame,
        agent_cls: type[ActorProtocol] = Actor,
        attrs: IncludeFlag = False,
        **kwargs,
    ) -> ActorsList[ActorProtocol]:
        # TODO: 这个方法需要适配到最新的 Mesa 版本
        """Create actors from a `geopandas.GeoDataFrame` object.

        This method creates actors from a GeoDataFrame, automatically assigning
        unique IDs to each actor. The geometries from the GeoDataFrame are used
        to initialize the actors' spatial properties, and selected attributes
        can be transferred to the created actors.

        Parameters:
            gdf:
                The `geopandas.GeoDataFrame` object to convert.
            agent_cls:
                Agent class to create. Defaults to `Actor`.
            attrs:
                Specifies which attributes from the GeoDataFrame to include in
                the created actors. Can be a boolean, list of column names, or
                exclusion pattern. Defaults to False (no attributes transferred).
            **kwargs:
                Additional keyword arguments to pass to the actor constructor.

        Returns:
            An `ActorsList` with all new created actors stored.

        Note:
            Each created actor will have a unique ID automatically assigned by
            the Mesa framework. The geometry from the GeoDataFrame will be
            converted to match the model's coordinate reference system (CRS).
        """
        # 检查坐标参考系是否一致
        self._check_crs(gdf)
        # 看一下哪些属性是需要加入到主体的
        geo_col = gdf.geometry.name
        set_attributes = clean_attrs(gdf.columns, attrs, exclude=geo_col)
        if not isinstance(set_attributes, dict):
            set_attributes = {col: col for col in set_attributes}
        # 创建主体
        agents = []
        for _, row in gdf.iterrows():
            geometry = row[geo_col]
            new_agent = self._new_one(geometry=geometry, agent_cls=agent_cls, **kwargs)
            new_agent.crs = self.crs

            for col, name in set_attributes.items():
                setattr(new_agent, name, row[col])
            agents.append(new_agent)
        # 添加主体到模型容器里
        return ActorsList(model=self.model, objs=agents)


class _CellAgentsContainer(_AgentsContainer):
    """Container for agents located at specific spatial cells.

    This specialized container manages agents that are positioned at a particular
    cell in the model's spatial grid. It extends the base container functionality
    with spatial awareness, ensuring that agents are properly linked to their
    location when added or removed.

    The container maintains the spatial relationship between agents and cells,
    automatically updating agent positions when they are added to or removed from
    the cell. It supports capacity limits to control the maximum number of agents
    that can occupy a single cell.

    Attributes:
        model: The ABSESpy model this container belongs to.
        _cell: The specific cell this container represents.
        _agents: The agent set containing all agents at this cell.
    """

    def __init__(
        self,
        model: MainModelProtocol,
        cell: PatchCell,
        max_len: int | float = float("inf"),
    ) -> None:
        """Initialize a cell agents container.

        Parameters:
            model: The ABSESpy model this container belongs to.
            cell: The specific cell this container manages agents for.
            max_len: Maximum number of agents allowed in this cell.
                Defaults to infinity (no limit).
        """
        super().__init__(model, max_len)
        self._agents = AgentSet([], random=model.random)
        self._cell = cell

    def _add_one(self, agent: ActorProtocol) -> None:
        """Internal method to add one agent to this cell's container.

        This method ensures that agents are properly located before being added.
        If an agent is already on earth at a different location, it must be moved
        or taken off earth first.

        Parameters:
            agent: The agent to add to this cell.

        Raises:
            ABSESpyError: If the agent is already located at a different cell.
                Use `actor.move.to()` to relocate or `actor.move.off()` to remove
                the agent from its current location first.
        """
        if agent.on_earth and agent not in self:
            e1 = f"{agent} is on {agent.at} thus cannot be added."
            e2 = "You may use 'actor.move.to()' to change its location."
            e3 = "Or you may use 'actor.move.off()' before adding it."
            raise ABSESpyError(e1 + e2 + e3)
        self._agents.add(agent)
        agent.at = self._cell
        self._agents.add(agent)

    def remove(self, agent: Optional[ActorProtocol] = None) -> None:
        """Remove the given agent from the cell.

        This method removes agents from the cell's container, breaking the spatial
        relationship between the agent and the cell. It can remove a specific agent
        or clear all agents from the cell if no agent is specified.

        It is generally recommended to use `actor.move.off()` instead, which provides
        a higher-level interface for agent movement and properly manages all related
        state updates.

        Parameters:
            agent:
                The agent (actor) to remove. If None, all agents are removed from
                the cell.

        Raises:
            ABSESpyError:
                If the specified agent is not currently located on this cell.
        """
        if agent is None:
            self._agents.clear()
            return
        assert isinstance(agent, ActorProtocol), f"{agent} is not an ActorProtocol."
        if agent.at is not self._cell:
            raise ABSESpyError(f"{agent} is not on this cell.")
        self._agents.remove(agent)
        del agent.at
