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
    Deque,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Set,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from pathlib import Path

    from mesa.agent import AgentSet
    from mesa.model import RNGLike, SeedLike
    from omegaconf import DictConfig
    from pendulum import DateTime
    from pendulum.duration import Duration

    from abses.core.primitives import State
    from abses.core.types import (
        AgentID,
        HowCheckName,
        Position,
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

    def go(self, steps: int = 1) -> None: ...
    def to(self, dt: DateTime | str) -> None: ...


@runtime_checkable
class Variable(Protocol):
    """变量协议"""

    _max_length: int = 1
    _history: Deque[Any]

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
    seed: int | None = None
    rng: RNGLike | SeedLike | None = None
    experiment: ExperimentProtocol | None = None
    steps: int = 0
    running: bool = True

    def add_name(self, name: str, check: Optional[HowCheckName] = None) -> None: ...

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
    def agent_types(self) -> List[AgentType]: ...
    @property
    def agent_by_type(self) -> Dict[AgentType, AgentSet]: ...


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

    def create_module(self, name: str, *args: Any, **kwargs: Any) -> ModuleProtocol: ...
    def register(self, component: ModuleProtocol) -> None: ...
    def unregister(self, component: ModuleProtocol) -> None: ...


@runtime_checkable
class ActorProtocol(Observer, ModelElement, Protocol):
    """代理协议，既是观察者也是被观察者

    注意继承顺序：
    1. Observer 和 ModelElement 先继承，因为它们是具体的协议
    2. Protocol 放在最后，因为它是基础协议类
    """

    unique_id: AgentID
    pos: Optional[Position]

    def initialize(self) -> None: ...
    def step(self) -> None: ...


AgentType = TypeVar("AgentType", bound="ActorProtocol")


class ActorsListProtocol(Protocol):
    """ActorsList协议"""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> ActorProtocol: ...
    def __iter__(self) -> Iterator[ActorProtocol]: ...

    def select(self, **kwargs: Any) -> ActorsListProtocol: ...


class AgentsContainerProtocol(Protocol):
    """AgentsContainer协议"""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> ActorProtocol: ...
    def __iter__(self) -> Iterator[ActorProtocol]: ...


@runtime_checkable
class HumanSystemProtocol(SubSystemProtocol, Protocol):
    """添加 @runtime_checkable 使得可以在运行时检查"""

    ...


@runtime_checkable
class NatureSystemProtocol(SubSystemProtocol, Protocol):
    """添加 @runtime_checkable 使得可以在运行时检查"""

    ...


@runtime_checkable
class PatchCellProtocol(Protocol):
    """PatchCell协议"""

    ...
