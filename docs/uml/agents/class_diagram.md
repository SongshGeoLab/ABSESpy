# ABSESpy Agents Module Class Diagram

This document contains the detailed class diagram for the agents module, showing the relationships between Actor, ActorsList, and various container classes.

## Agents Module Class Diagram

```mermaid
classDiagram
    %% Base Actor Classes
    class Actor {
        +unique_id: int
        +model: MainModel
        +pos: Optional[Position]
        +on_earth: bool
        +alive: bool
        +geometry: Optional[BaseGeometry]
        +__init__(model: MainModel, observer: bool, **kwargs) void
        +die() void
        +move(target: Position) void
        +step() void
        +distance_to(target: Position) float
        +neighbors(radius: float) List[Actor]
    }

    class ActorProtocol {
        <<interface>>
        +unique_id: int
        +model: MainModelProtocol
        +pos: Optional[Position]
        +on_earth: bool
        +die() void
        +move(target: Position) void
        +step() void
    }

    %% Actor Collections
    class ActorsList {
        +agents: List[Actor]
        +random: ListRandom
        +model: MainModel
        +item(how: HOW_TO_SELECT, index: int) Optional[Actor]
        +array(attr: str) np.ndarray
        +select(selection: Callable) ActorsList
        +shuffle_do(method: str) void
        +apply(func: Callable) void
        +filter(condition: Callable) ActorsList
        +sample(n: int) ActorsList
        +random_choice() Actor
    }

    class ActorsListProtocol {
        <<interface>>
        +item(how: HOW_TO_SELECT, index: int) Optional[Actor]
        +array(attr: str) np.ndarray
        +select(selection: Callable) ActorsList
        +shuffle_do(method: str) void
        +apply(func: Callable) void
    }

    %% Agent Containers
    class _AgentsContainer {
        +agents: Dict[int, Actor]
        +model: MainModel
        +new(agent_class: Type[Actor], num: int, **kwargs) ActorsList
        +select(selection: Callable, agent_type: Type[Actor]) ActorsList
        +__getitem__(breeds: Breeds) ActorsList
        +deregister_agent(agent: Actor) void
        +register_agent(agent: Actor) void
        +get_agent(agent_id: int) Optional[Actor]
    }

    class _ModelAgentsContainer {
        +model: MainModel
        +agents: Dict[int, Actor]
        +new(agent_class: Type[Actor], num: int, **kwargs) ActorsList
        +select(selection: Callable, agent_type: Type[Actor]) ActorsList
        +__getitem__(breeds: Breeds) ActorsList
        +deregister_agent(agent: Actor) void
        +register_agent(agent: Actor) void
        +get_agent(agent_id: int) Optional[Actor]
        +__len__() int
        +__iter__() Iterator[Actor]
    }

    class _CellAgentsContainer {
        +cell: PatchCell
        +agents: List[Actor]
        +add_agent(agent: Actor) void
        +remove_agent(agent: Actor) void
        +select(selection: Callable) ActorsList
        +get_agent(agent_id: int) Optional[Actor]
        +__len__() int
        +__iter__() Iterator[Actor]
    }

    %% Random Operations
    class ListRandom {
        +generator: np.random.Generator
        +choice(actors: List[Actor]) Actor
        +sample(actors: List[Actor], n: int) List[Actor]
        +shuffle(actors: List[Actor]) List[Actor]
        +new(agent_class: Type[Actor], num: int) ActorsList
    }

    %% Selection Strategies
    class HOW_TO_SELECT {
        <<enumeration>>
        +ITEM
        +RANDOM
        +FIRST
        +LAST
    }

    %% Decorators
    class alive_required {
        <<decorator>>
        +__call__(method: Callable) Callable
    }

    class with_axes {
        <<decorator>>
        +__call__(method: Callable) Callable
    }

    %% Relationships
    Actor ..|> ActorProtocol : implements
    ActorsList ..|> ActorsListProtocol : implements

    _ModelAgentsContainer --|> _AgentsContainer : extends
    _CellAgentsContainer --|> _AgentsContainer : extends

    ActorsList ||--o{ Actor : contains
    ActorsList ||--|| ListRandom : uses

    _ModelAgentsContainer ||--o{ Actor : manages
    _CellAgentsContainer ||--o{ Actor : manages

    Actor ||--|| MainModel : belongs to
    Actor ||--o| PatchCell : located on

    ActorsList ||--|| _AgentsContainer : created by

    alive_required ..> Actor : decorates
    with_axes ..> Actor : decorates
```

## Key Components

### Actor Class
- **Purpose**: Base class for all agents in ABSESpy
- **Key Features**:
  - Spatial positioning (`pos`, `on_earth`)
  - Lifecycle management (`alive`, `die()`)
  - Movement capabilities (`move()`)
  - Model integration (`model` reference)

### ActorsList Class
- **Purpose**: Collection of actors with batch operations
- **Key Features**:
  - Chainable operations (`select()`, `filter()`)
  - Random operations (`random_choice()`, `sample()`)
  - Batch execution (`shuffle_do()`, `apply()`)
  - Data extraction (`array()`)

### Container Classes
- **_ModelAgentsContainer**: Manages all agents in the model
- **_CellAgentsContainer**: Manages agents on a specific cell
- **_AgentsContainer**: Base class for agent management

### Design Patterns
- **Container Pattern**: Various containers manage actor collections
- **Strategy Pattern**: Different selection strategies (item, random, first, last)
- **Decorator Pattern**: `@alive_required`, `@with_axes` decorators
- **Factory Pattern**: Agent creation through containers

## Usage Examples

```python
# Create agents
farmers = model.agents.new(Farmer, num=10)

# Chain operations
active_farmers = (farmers
                  .select(lambda a: a.energy > 0)
                  .select(lambda a: a.pos is not None))

# Batch operations
farmers.shuffle_do("work")
farmers.apply(lambda a: a.collect_resources())

# Random selection
random_farmer = farmers.random_choice()
sample_farmers = farmers.sample(5)
```