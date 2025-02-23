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

from collections import deque
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    runtime_checkable,
)

from omegaconf import DictConfig


class State(IntEnum):
    """状态枚举，使用整数值确保可以比较"""

    NEW = 0
    INIT = 1
    READY = 2
    COMPLETE = 3


class Experiment(Protocol):
    """实验协议"""

    name: str


@runtime_checkable
class TimeDriver(Protocol):
    """时间驱动协议"""

    @property
    def current(self) -> datetime: ...
    def step(self, steps: int = 1) -> None: ...
    def reset(self) -> None: ...


@runtime_checkable
class Variable(Protocol):
    """变量协议"""

    _max_length: int = 1
    _history: deque[Any]

    @property
    def obj(self) -> ModelElement: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> Any: ...

    def update(self, value: Any) -> None: ...


@runtime_checkable
class DynamicVariable(Variable, Protocol):
    """动态变量协议"""


@runtime_checkable
class Observer(Protocol):
    """观察者协议"""

    def update(self, subject: Observable) -> None: ...


@runtime_checkable
class Observable(Protocol):
    """可被观察的组件协议"""

    @property
    def observers(self) -> Set[Observer]: ...
    @property
    def variables(self) -> Dict[str, Variable]: ...

    def attach(self, observer: Observer) -> None: ...
    def detach(self, observer: Observer) -> None: ...
    def notify(self) -> None: ...


class ModelElement(Observable, Protocol):
    """
    Model element protocol.

    Each model element is a component of the model.
    It should have:
    - a name
    - belong to a model
    - parameters
    """

    @property
    def name(self) -> str: ...
    @property
    def model(self) -> MainModelProtocol: ...
    @property
    def params(self) -> DictConfig: ...


@runtime_checkable
class MainModelProtocol(ModelElement, Protocol):
    """主模型协议"""

    parameters: DictConfig | None | Dict = None
    run_id: int | None = None
    seed: int | None = None
    rng: RNGLike | SeedLike | None = None
    experiment: Experiment | None = None

    def add_name(self, name: str, check: Optional[HowCheckName] = None) -> None: ...

    @property
    def settings(self) -> DictConfig: ...
    @property
    def outpath(self) -> Path: ...
    @property
    def exp(self) -> Experiment: ...
    @property
    def version(self) -> str: ...
    @property
    def datasets(self) -> DictConfig: ...
    @property
    def human(self) -> BaseHuman: ...
    @property
    def nature(self) -> BaseNature: ...


@runtime_checkable
class ModuleProtocol(ModelElement, Protocol):
    """
    Model component protocol.
    """

    @property
    def state(self) -> State: ...
    @property
    def opening(self) -> bool: ...
    @property
    def outpath(self) -> Optional[Path]: ...

    def set_state(self, state: State) -> None: ...
    def reset(self, opening: bool = True) -> None: ...
    def initialize(self) -> None: ...
    def setup(self) -> None: ...
    def step(self) -> None: ...
    def end(self) -> None: ...


@runtime_checkable
class SubSystemProtocol(ModuleProtocol, Protocol):
    """子系统（Nature/Human）协议"""

    @property
    def modules(self) -> Dict[str, ModuleProtocol]: ...

    def create_module(self, name: str, *args: Any, **kwargs: Any) -> ModuleProtocol: ...
    def register(self, component: ModuleProtocol) -> None: ...
    def unregister(self, component: ModuleProtocol) -> None: ...


@runtime_checkable
class AgentProtocol(Observer, ModelElement, Protocol):
    """代理协议，既是观察者也是被观察者

    注意继承顺序：
    1. Observer 和 ModelElement 先继承，因为它们是具体的协议
    2. Protocol 放在最后，因为它是基础协议类
    """

    unique_id: AgentID
    pos: Optional[Position]

    def initialize(self) -> None: ...
    def step(self) -> None: ...


# Type definitions
ComponentType = TypeVar("ComponentType", bound=ModuleProtocol)
ModelType = TypeVar("ModelType", bound=MainModelProtocol)
AgentID = Union[str, int]
Position = Tuple[float, float]
GeometryType = Literal["Point", "Shape"]
AgentType = TypeVar("AgentType", bound="AgentProtocol")
HowCheckName: TypeAlias = Literal["unique", "exists"]

# 容器相关类型
if TYPE_CHECKING:
    from mesa.model import RNGLike, SeedLike

    from abses.agents.actor import Actor
    from abses.agents.sequences import ActorsList
    from abses.human.human import BaseHuman
    from abses.space.nature import BaseNature

    # 将所有类型定义移到这里
    ActorTypes: TypeAlias = Union[Type[Actor], Iterable[Type[Actor]]]
    Actors: TypeAlias = Union[Actor, ActorsList, Iterable[Actor]]
    UniqueID: TypeAlias = Union[str, int]
    UniqueIDs: TypeAlias = List[Optional[UniqueID]]
    N = TypeVar("N", bound=BaseNature)
    H = TypeVar("H", bound=BaseHuman)

    SubSystemType: TypeAlias = Literal["model", "nature", "human"]
    SubSystem: TypeAlias = Union[
        SubSystemType,
        Tuple[SubSystemType, SubSystemType],
        Tuple[SubSystemType, SubSystemType, SubSystemType],
    ]
