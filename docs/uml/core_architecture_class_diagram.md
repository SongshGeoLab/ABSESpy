# ABSESpy Core Architecture Class Diagram

This document contains the core architecture class diagram for ABSESpy, showing the main components and their relationships.

## Core Architecture Class Diagram

```mermaid
classDiagram
    %% Core Model Components
    class MainModel {
        +parameters: DictConfig
        +agents: _ModelAgentsContainer
        +nature: BaseNature
        +human: BaseHuman
        +time: TimeDriver
        +datacollector: ABSESpyDataCollector
        +run_id: Optional[int]
        +seed: Optional[int]
        +rng: np.random.Generator
        +experiment: Optional[ExperimentProtocol]
        +setup() void
        +step() void
        +run_model() void
    }

    class BaseNature {
        +major_layer: Optional[PatchModule]
        +total_bounds: Tuple[float, float, float, float]
        +crs: str
        +layers: Dict[str, PatchModule]
        +modules: ModuleFactory
        +create_module(name: str, **kwargs) PatchModule
        +get_layer(name: str) PatchModule
        +apply_raster(raster: xr.DataArray, name: str) void
    }

    class BaseHuman {
        +agents: _ModelAgentsContainer
        +collections: Dict[str, Any]
        +define(name: str, **kwargs) void
        +get_collection(name: str) Any
        +setup() void
        +step() void
    }

    class Actor {
        +unique_id: int
        +model: MainModel
        +pos: Optional[Position]
        +on_earth: bool
        +alive: bool
        +die() void
        +move(target: Position) void
        +step() void
    }

    class PatchCell {
        +agents: _CellAgentsContainer
        +pos: Position
        +geometry: BaseGeometry
        +fertility: float
        +raster_attributes: Dict[str, Any]
        +add_agent(agent: Actor) void
        +remove_agent(agent: Actor) void
    }

    class PatchModule {
        +name: str
        +cells: List[PatchCell]
        +raster: xr.DataArray
        +crs: str
        +bounds: Tuple[float, float, float, float]
        +create_cells() List[PatchCell]
        +apply_raster(raster: xr.DataArray) void
    }

    %% Agent Management
    class _ModelAgentsContainer {
        +model: MainModel
        +agents: Dict[int, Actor]
        +new(agent_class: Type[Actor], num: int) ActorsList
        +select(selection: Callable, agent_type: Type[Actor]) ActorsList
        +__getitem__(breeds: Breeds) ActorsList
        +deregister_agent(agent: Actor) void
    }

    class _CellAgentsContainer {
        +cell: PatchCell
        +agents: List[Actor]
        +add_agent(agent: Actor) void
        +remove_agent(agent: Actor) void
        +select(selection: Callable) ActorsList
    }

    class ActorsList {
        +agents: List[Actor]
        +random: ListRandom
        +item(how: HOW_TO_SELECT, index: int) Optional[Actor]
        +array(attr: str) np.ndarray
        +select(selection: Callable) ActorsList
        +shuffle_do(method: str) void
        +apply(func: Callable) void
    }

    %% Time and Data Management
    class TimeDriver {
        +tick: int
        +current_time: DateTime
        +end_time: DateTime
        +go() void
        +step() void
        +is_finished() bool
    }

    class ABSESpyDataCollector {
        +model_reporters: Dict[str, Callable]
        +agent_reporters: Dict[str, Callable]
        +collect(model: MainModel) void
        +get_model_vars_dataframe() pd.DataFrame
        +get_agent_vars_dataframe() pd.DataFrame
    }

    %% Relationships
    MainModel ||--|| BaseNature : contains
    MainModel ||--|| BaseHuman : contains
    MainModel ||--|| TimeDriver : contains
    MainModel ||--|| ABSESpyDataCollector : contains
    MainModel ||--|| _ModelAgentsContainer : contains

    BaseNature ||--o{ PatchModule : manages
    PatchModule ||--o{ PatchCell : contains
    PatchCell ||--o{ Actor : hosts
    PatchCell ||--|| _CellAgentsContainer : contains

    _ModelAgentsContainer ||--o{ Actor : manages
    _CellAgentsContainer ||--o{ Actor : manages
    ActorsList ||--o{ Actor : contains

    Actor ||--|| MainModel : belongs to
    Actor ||--o| PatchCell : located on

    BaseHuman ||--|| _ModelAgentsContainer : uses
```

## Key Relationships

1. **MainModel** is the central component that orchestrates all subsystems
2. **BaseNature** manages spatial components through PatchModule instances
3. **BaseHuman** manages human-related agents and collections
4. **Actor** represents individual agents that can be placed on PatchCell instances
5. **PatchCell** represents spatial units that can host multiple actors
6. **ActorsList** provides batch operations on actor collections
7. **TimeDriver** manages model time progression
8. **ABSESpyDataCollector** collects and stores model data

## Design Patterns

- **Observer Pattern**: Actors observe model state changes
- **Factory Pattern**: ModuleFactory creates PatchModule instances
- **Container Pattern**: Various container classes manage collections
- **Strategy Pattern**: Different selection strategies for ActorsList
