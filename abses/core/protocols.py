#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    runtime_checkable,
)

import numpy as np

from abses.core.primitives import DEFAULT_RUN_ORDER, State

if TYPE_CHECKING:
    from pathlib import Path

    import networkx as nx
    import pyproj
    from mesa.agent import AgentSet
    from mesa.model import RNGLike, SeedLike
    from omegaconf import DictConfig
    from pendulum import DateTime
    from pendulum.duration import Duration

    from abses.core.types import (
        AgentID,
        HowCheckName,
        Position,
        SubSystemName,
        UniqueID,
    )


class ExperimentProtocol(Protocol):
    """实验协议"""

    name: str


@runtime_checkable
class TimeDriverProtocol(Protocol):
    """时间驱动协议"""

    dt: DateTime
    duration: Duration
    end_at: DateTime | None | int
    start_dt: DateTime | None
    tick: int

    def go(self, steps: int = 1) -> None: ...
    def to(self, dt: DateTime | str) -> None: ...


@runtime_checkable
class VariableProtocol(Protocol):
    """变量协议"""

    _max_length: int = 1

    @property
    def obj(self) -> ModelElement: ...
    @property
    def name(self) -> str: ...


@runtime_checkable
class DynamicVariableProtocol(VariableProtocol, Protocol):
    """动态变量协议"""

    attrs: Dict[str, Any]

    @property
    def cache(self) -> Any: ...
    @property
    def now(self) -> Any: ...


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
    def variables(self) -> Dict[str, VariableProtocol]: ...

    def attach(self, observer: Observer) -> None: ...
    def detach(self, observer: Observer) -> None: ...
    def notify(self) -> None: ...


@runtime_checkable
class StateManagerProtocol(Protocol):
    """状态管理器协议"""

    def set_state(self, state: State) -> None: ...
    def reset(self, opening: bool = True) -> None: ...
    def initialize(self) -> None: ...
    def setup(self) -> None: ...
    def step(self) -> None: ...
    def end(self) -> None: ...


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
    @property
    def tick(self) -> int: ...


@runtime_checkable
class MainModelProtocol(ModelElement, Protocol):
    """主模型协议"""

    parameters: DictConfig | None | Dict = None
    run_id: int | None = None
    _seed: int | None = None
    rng: RNGLike | SeedLike | None = None
    experiment: ExperimentProtocol | None = None
    steps: int = 0
    running: bool = True
    datacollector: Any
    random: np.random.Generator

    def __new__(cls, *args: Any, **kwargs: Any) -> MainModelProtocol: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    def add_name(self, name: str, check: Optional[HowCheckName] = None) -> None: ...
    def run_model(
        self,
        steps: Optional[int] = None,
        order: Tuple[SubSystemName, ...] = DEFAULT_RUN_ORDER,
    ) -> None: ...

    @property
    def settings(self) -> DictConfig: ...
    @property
    def outpath(self) -> Path: ...
    @property
    def exp(self) -> ExperimentProtocol: ...
    @property
    def version(self) -> str: ...
    @property
    def datasets(self) -> DictConfig: ...
    @property
    def human(self) -> HumanSystemProtocol: ...
    @property
    def nature(self) -> NatureSystemProtocol: ...
    @property
    def agent_types(self) -> List[type[ActorProtocol]]: ...
    @property
    def agent_by_type(self) -> Dict[type[ActorProtocol], AgentSet]: ...
    @property
    def agents(self) -> AgentsContainerProtocol: ...
    @property
    def actors(self) -> ActorsListProtocol: ...
    @property
    def time(self) -> TimeDriverProtocol: ...
    @property
    def params(self) -> DictConfig: ...
    @property
    def agents_by_type(self) -> dict[type, ActorsListProtocol]: ...

    def deregister_agent(self, agent: "ActorProtocol") -> None:
        """Deregister an agent from the model."""
        ...


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


@runtime_checkable
class SubSystemProtocol(ModuleProtocol, Protocol):
    """子系统（Nature/Human）协议"""

    def __init__(
        self, model: MainModelProtocol, name: Optional[str] = None
    ) -> None: ...

    @property
    def modules(self) -> Dict[str, ModuleProtocol]: ...

    def create_module(self, name: str, *args: Any, **kwargs: Any) -> Any: ...
    def register(self, component: ModuleProtocol) -> None: ...
    def unregister(self, component: ModuleProtocol) -> None: ...
    def get_raster(self, *args: Any, **kwargs: Any) -> Any: ...
    def get_graph(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class _MovementsProtocol(Protocol):
    """移动协议"""

    def to(self, cell: PatchCellProtocol) -> None: ...
    def off(self) -> None: ...
    def by(self, cell: PatchCellProtocol) -> None: ...
    def random(self) -> None: ...


@runtime_checkable
class ActorProtocol(Observer, ModelElement, Protocol):
    """代理协议，既是观察者也是被观察者

    注意继承顺序：
    1. Observer 和 ModelElement 先继承，因为它们是具体的协议
    2. Protocol 放在最后，因为它是基础协议类
    """

    unique_id: AgentID
    pos: Optional[Position]
    alive: bool
    model: MainModelProtocol
    indices: Optional[Position]

    def __init__(self, model: MainModelProtocol, **kwargs: Any) -> None: ...

    @property
    def move(self) -> _MovementsProtocol: ...
    @property
    def layer(self) -> Optional[ModuleProtocol]: ...
    @property
    def on_earth(self) -> bool: ...
    @property
    def at(self) -> PatchCellProtocol | None: ...
    @property
    def crs(self) -> pyproj.CRS: ...
    def die(self) -> None: ...
    def moving(self) -> bool: ...
    def update(self, subject: Observable) -> None: ...
    def step(self) -> None: ...
    def initialize(self) -> None: ...
    def setup(self) -> None: ...
    def end(self) -> None: ...


AgentType = TypeVar("AgentType", bound="ActorProtocol")


class ActorsListProtocol(Protocol):
    """代理列表协议"""

    model: MainModelProtocol

    def __iter__(self) -> Iterator[ActorProtocol]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> ActorProtocol: ...
    def append(self, actor: ActorProtocol) -> None: ...
    def remove(self, actor: ActorProtocol) -> None: ...
    def select(self, how: str = "all", **kwargs: Any) -> ActorsListProtocol: ...
    def array(self, attr: str) -> np.ndarray: ...
    def item(self, index: int) -> ActorProtocol: ...

    @property
    def random(self) -> Any: ...
    @property
    def plot(self) -> Any: ...


class AgentsContainerProtocol(Protocol):
    """代理容器协议"""

    model: MainModelProtocol

    def __iter__(self) -> Iterator[ActorProtocol]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> ActorProtocol: ...

    def add(self, agent: ActorProtocol) -> None: ...
    def remove(self, agent: ActorProtocol) -> None: ...
    def get_by_id(self, agent_id: AgentID) -> Optional[ActorProtocol]: ...
    def get_by_type(self, agent_type: type) -> ActorsListProtocol: ...
    def get_all(self) -> ActorsListProtocol: ...
    def select(self, *args: Any, **kwargs: Any) -> ActorsListProtocol: ...
    @property
    def is_full(self) -> bool: ...

    @property
    def agents_by_type(self) -> dict[type, ActorsListProtocol]: ...


@runtime_checkable
class PatchCellProtocol(Protocol):
    """PatchCell协议"""

    ...


@runtime_checkable
class LinkNodeProtocol(Protocol):
    """LinkNode协议"""

    ...


@runtime_checkable
class LinkContainerProtocol(Protocol):
    """LinkContainer协议"""

    links: Tuple[str, ...]

    def _cache_node(self, node: LinkNodeProtocol) -> UniqueID: ...
    def _get_node(self, node_id: UniqueID) -> LinkNodeProtocol: ...
    def _register_link(
        self, link_name: str, source: LinkNodeProtocol, target: LinkNodeProtocol
    ) -> None: ...
    def has_link(
        self, link_name: str, source: LinkNodeProtocol, target: LinkNodeProtocol
    ) -> Tuple[bool, bool]: ...
    def add_a_link(
        self,
        link_name: str,
        source: LinkNodeProtocol,
        target: LinkNodeProtocol,
        mutual: bool = False,
    ) -> None: ...
    def remove_a_link(
        self,
        link_name: str,
        source: LinkNodeProtocol,
        target: LinkNodeProtocol,
        mutual: bool = False,
    ) -> None: ...
    def linked(
        self,
        node: LinkNodeProtocol,
        link_name: Optional[str | list[str]] = None,
        direction: Optional[str] = None,
        default: Any = ...,
    ) -> Set[LinkNodeProtocol]: ...
    def owns_links(
        self, node: LinkNodeProtocol, direction: Optional[str] = None
    ) -> Tuple[str, ...]: ...
    def get_graph(
        self, link_name: str, directions: bool = False
    ) -> "nx.Graph | nx.DiGraph": ...
    def clean_links_of(
        self,
        node: LinkNodeProtocol,
        link_name: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> None: ...

    ...


@runtime_checkable
class HumanSystemProtocol(SubSystemProtocol, LinkContainerProtocol, Protocol):
    """添加 @runtime_checkable 使得可以在运行时检查"""

    ...


@runtime_checkable
class NatureSystemProtocol(SubSystemProtocol, Protocol):
    """添加 @runtime_checkable 使得可以在运行时检查"""

    @property
    def crs(self) -> pyproj.CRS: ...

    ...
