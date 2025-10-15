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
    Generic,
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
from abses.core.type_aliases import (
    AgentID,
    HowCheckName,
    Position,
    SubSystemName,
    UniqueID,
)

# Type variable for generic variable values
T = TypeVar("T")

if TYPE_CHECKING:
    from pathlib import Path

    import networkx as nx
    import pyproj
    from mesa.agent import AgentSet
    from mesa.model import RNGLike, SeedLike
    from omegaconf import DictConfig
    from pendulum import DateTime
    from pendulum.duration import Duration


class ExperimentProtocol(Protocol):
    """实验协议"""

    name: str


class TimeDriverProtocol(Protocol):
    """Time driver protocol.

    Defines the interface for time management in models.
    """

    dt: DateTime
    duration: Duration
    end_at: DateTime | None | int
    start_dt: DateTime | None
    tick: int

    def go(self, steps: int = 1) -> None: ...
    def to(self, dt: DateTime | str) -> None: ...


@runtime_checkable
class VariableProtocol(Protocol):
    """Variable protocol.

    Defines the interface for model variables that can be tracked and observed.

    Attributes:
        _max_length: Maximum length of variable history to store.
        obj: The model element that owns this variable.
        name: Name of the variable.
    """

    _max_length: int = 1

    @property
    def obj(self) -> ModelElement:
        """Get the model element that owns this variable.

        Returns:
            The owning model element.
        """
        ...

    @property
    def name(self) -> str:
        """Get the name of the variable.

        Returns:
            Variable name.
        """
        ...


class DynamicVariableProtocol(VariableProtocol, Protocol, Generic[T]):
    """Dynamic variable protocol with generic type support.

    Extends VariableProtocol with caching and computation capabilities.
    The generic type T represents the type of value this variable holds.

    Example:
        ```python
        # A dynamic variable that returns int values
        var: DynamicVariableProtocol[int] = ...
        value: int = var.now()
        ```
    """

    attrs: Dict[str, Any]

    @property
    def cache(self) -> T:
        """Get cached value.

        Returns:
            The cached value of type T.
        """
        ...

    @property
    def now(self) -> T:
        """Compute and return current value.

        Returns:
            The current computed value of type T.
        """
        ...


class Observer(Protocol):
    """Observer protocol.

    Defines the interface for objects that observe changes in observables.
    """

    def update(self, subject: Observable) -> None:
        """Called when the observed subject changes.

        Args:
            subject: The observable that changed.
        """
        ...


class Observable(Protocol):
    """Observable protocol.

    Defines the interface for objects that can be observed for changes.
    """

    @property
    def observers(self) -> Set[Observer]: ...
    @property
    def variables(self) -> Dict[str, VariableProtocol]: ...

    def attach(self, observer: Observer) -> None: ...
    def detach(self, observer: Observer) -> None: ...
    def notify(self) -> None: ...


class StateManagerProtocol(Protocol):
    """State manager protocol.

    Defines the interface for managing component lifecycle states.
    """

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


class MainModelProtocol(ModelElement, Protocol):
    """Main model protocol.

    Defines the complete interface for ABSESpy main models.
    """

    parameters: DictConfig | None | Dict = None
    run_id: int | None = None
    _seed: int | None = None
    rng: RNGLike | SeedLike | None = None
    experiment: ExperimentProtocol | None = None
    steps: int = 0
    running: bool = True
    datacollector: Any  # ABSESpyDataCollector, kept as Any for flexibility
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


class ModuleProtocol(ModelElement, Protocol):
    """Model module protocol.

    Defines the interface for model modules with lifecycle management.
    """

    @property
    def state(self) -> State: ...
    @property
    def opening(self) -> bool: ...
    @property
    def outpath(self) -> Optional[Path]: ...


class SubSystemProtocol(ModuleProtocol, Protocol):
    """Subsystem protocol (Nature/Human).

    Defines the interface for subsystems that manage collections of modules.
    """

    def __init__(
        self, model: MainModelProtocol, name: Optional[str] = None
    ) -> None: ...

    @property
    def modules(self) -> Dict[str, ModuleProtocol]: ...

    def create_module(self, name: str, *args: Any, **kwargs: Any) -> ModuleProtocol: ...
    def register(self, component: ModuleProtocol) -> None: ...
    def unregister(self, component: ModuleProtocol) -> None: ...
    def get_raster(
        self, *args: Any, **kwargs: Any
    ) -> Any: ...  # Returns raster data, kept flexible
    def get_graph(
        self, *args: Any, **kwargs: Any
    ) -> Any: ...  # Returns graph, kept flexible


class MovementProtocol(Protocol):
    """Movement protocol.

    Defines the interface for actor movement operations.
    """

    def to(self, cell: PatchCellProtocol) -> None:
        """Move to a specific cell.

        Args:
            cell: Target cell to move to.
        """
        ...

    def off(self) -> None:
        """Remove from current cell (go off-grid)."""
        ...

    def by(self, cell: PatchCellProtocol) -> None:
        """Move by a cell offset.

        Args:
            cell: Cell offset for relative movement.
        """
        ...

    def random(self) -> None:
        """Move to a random neighboring cell."""
        ...


# Deprecated alias for backward compatibility
_MovementsProtocol = MovementProtocol


@runtime_checkable
class ActorProtocol(Observer, ModelElement, Protocol):
    """Actor protocol.

    Defines the complete interface for actors (agents) in ABSESpy models.
    Actors are both observers and model elements with spatial awareness and lifecycle management.

    Attributes:
        unique_id: Unique identifier for this actor.
        pos: Current position (longitude, latitude).
        alive: Whether the actor is alive.
        model: Reference to the parent model.
        indices: Grid indices if on a patch.
        move: Movement operations interface.
        layer: The module/layer this actor belongs to.
        on_earth: Whether positioned on the spatial grid.
        at: The patch cell at current position.
        crs: Coordinate reference system.

    Lifecycle Methods:
        initialize(): Called once at creation.
        setup(): Called before simulation starts.
        step(): Called each simulation step.
        end(): Called when simulation ends.

    Example:
        ```python
        class Farmer(Actor):
            def setup(self):
                self.wealth = 100

            def step(self):
                if self.on_earth:
                    # Harvest from current cell
                    self.wealth += self.at.yield_value
        ```
    """

    unique_id: AgentID
    pos: Optional[Position]
    alive: bool
    model: MainModelProtocol
    indices: Optional[Position]

    def __init__(self, model: MainModelProtocol, **kwargs: Any) -> None: ...

    @property
    def move(self) -> MovementProtocol: ...
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
    """Actors list protocol.

    Defines the interface for collections of actors with selection and manipulation capabilities.

    Attributes:
        model: The ABSESpy model instance.
        random: Random operations on the actors list.
        plot: Visualization interface for actors.

    Example:
        ```python
        # Select actors with specific attribute
        active_actors = model.actors.select("active")

        # Get array of actor attributes
        ages = actors.array("age")

        # Random operations
        sample = actors.random.choice(n=10)
        ```
    """

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
    """Agents container protocol.

    Defines the interface for managing all agents in the model with type-based organization.

    Attributes:
        model: The ABSESpy model instance.
        is_full: Whether the container has reached capacity.
        agents_by_type: Dictionary mapping agent types to their lists.

    Example:
        ```python
        # Add new agent
        agent = Actor(model)
        model.agents.add(agent)

        # Get by type
        farmers = model.agents.get_by_type(Farmer)

        # Select with criteria
        active = model.agents.select("active", at_most=10)
        ```
    """

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


class PatchCellProtocol(Protocol):
    """PatchCell protocol.

    Defines the interface for patch cells in the spatial grid.

    Attributes:
        indices: Grid indices (row, col) of the cell.
        pos: Optional position tuple.
        layer: The raster layer this cell belongs to.
        agents: Container for agents at this cell.
        coordinate: Geographic coordinates of the cell.
        crs: Coordinate reference system.
    """

    indices: Optional[Position]
    pos: Optional[Position]
    max_agents: Optional[int]

    @property
    def layer(self) -> Optional[ModuleProtocol]:
        """Get the raster layer this cell belongs to.

        Returns:
            The layer module.
        """
        ...

    @property
    def agents(self) -> AgentsContainerProtocol:
        """Get the agents container at this cell.

        Returns:
            Container of agents at this location.
        """
        ...

    @property
    def coordinate(self) -> Tuple[float, float]:
        """Get the geographic coordinates of this cell.

        Returns:
            (longitude, latitude) or (x, y) coordinates.
        """
        ...

    @property
    def geo_type(self) -> str:
        """Get the geometry type.

        Returns:
            Geometry type name.
        """
        ...

    @property
    def crs(self) -> Any:
        """Get the coordinate reference system.

        Returns:
            CRS object.
        """
        ...

    def neighboring(
        self,
        moore: bool = False,
        radius: int = 1,
        include_center: bool = False,
        annular: bool = False,
    ) -> ActorsListProtocol:
        """Get neighboring cells.

        Args:
            moore: Whether to include Moore neighborhood.
            radius: Radius of the neighborhood.
            include_center: Whether to include center cell.
            annular: Whether to use annular neighborhood.

        Returns:
            List of neighboring cells.
        """
        ...


class LinkNodeProtocol(Protocol):
    """LinkNode protocol.

    Defines the interface for linkable nodes (Actors and PatchCells).

    Attributes:
        unique_id: Unique identifier for the node.
        breed: Type/breed of the node.
    """

    unique_id: UniqueID

    @property
    def breed(self) -> str:
        """Get the breed/type of this node.

        Returns:
            Breed name.
        """
        ...

    def get(
        self,
        attr: str,
        target: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """Get attribute value from this node or a target.

        Args:
            attr: Attribute name to get.
            target: Optional target name to redirect to.
            default: Default value if attribute not found.

        Returns:
            Attribute value.
        """
        ...


class LinkContainerProtocol(Protocol):
    """Link container protocol.

    Defines the interface for managing links between nodes.
    """

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


class HumanSystemProtocol(SubSystemProtocol, LinkContainerProtocol, Protocol):
    """Human subsystem protocol.

    Combines subsystem functionality with link management for social networks.
    """

    ...


class NatureSystemProtocol(SubSystemProtocol, Protocol):
    """Nature subsystem protocol.

    Defines the interface for the nature/spatial subsystem with CRS support.
    """

    @property
    def crs(self) -> pyproj.CRS: ...

    ...
