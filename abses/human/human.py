#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Optional,
    Set,
    Type,
)

from abses.core.base import BaseModule, BaseSubSystem
from abses.core.protocols import (
    ActorsListProtocol,
    HumanSystemProtocol,
    MainModelProtocol,
)
from abses.human.links import _LinkContainer


class HumanModule(BaseModule):
    """The `Human` sub-module base class.

    Note:
        Look at [this tutorial](../tutorial/beginner/organize_model_structure.ipynb) to understand the model structure.

    Attributes:
        agents:
            The agents container of this ABSESpy model.
        collections:
            Actor collections defined.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        model: MainModelProtocol,
        **kwargs,
    ):
        BaseModule.__init__(self, model, name=name)
        self._refers: Dict[str, Dict[str, Any]] = {}
        self.define(name, **kwargs)

    @property
    def agents(self) -> ActorsListProtocol:
        """The agents container of this ABSESpy model."""
        if self.name not in self._refers:
            raise KeyError(f"{self.name} is not defined.")
        selection = self._refers[self.name]
        return self.model.agents.select(**selection)

    @property
    def collections(self) -> Set[str]:
        """Actor collections defined."""
        return set(self._refers.keys())

    @property
    def actors(self) -> ActorsListProtocol:
        """Different selections of agents"""
        return self.agents.select("on_earth")

    def define(
        self,
        refer_name: Optional[str] = None,
        **kwargs,
    ) -> ActorsListProtocol:
        """Define a query of actors and save it into collections.

        Parameters:
            name:
                defined name of this group of actors.
            selection:
                Selection query of `Actor`.

        Raises:
            KeyError:
                If the name is already defined.

        Returns:
            The list of actors who are satisfied the query condition.

        Example:
            ```
            # Create 5 actors to query
            model=MainModelProtocol()
            model.agents.new(Actor, 5)

            module = HumanModule(model=model)
            actors = module.define(name='first', selection='ids=0')
            >>> len(actors)
            >>> 1

            >>> module.actors('first') == actors
            >>> True
            ```
        """
        if refer_name is None:
            refer_name = self.name
        if refer_name in self._refers:
            raise KeyError(f"{refer_name} is already defined.")
        self._refers[refer_name] = kwargs.copy()
        selected = self.agents.select(**kwargs)
        return selected


class BaseHuman(BaseSubSystem, _LinkContainer, HumanSystemProtocol):
    """The Base Human Module."""

    def __init__(self, model: MainModelProtocol, name: str = "human"):
        BaseSubSystem.__init__(self, model, name=name)
        _LinkContainer.__init__(self, model)

    def create_module(
        self,
        name: Optional[str] = None,
        *,
        module_cls: Type[HumanModule] = HumanModule,
        **kwargs,
    ) -> BaseModule:
        if name is None:
            name = f"Group {len(self.modules)}"
        module = super().create_module(
            name=name,
            module_cls=module_cls,
            **kwargs,
        )
        return module
