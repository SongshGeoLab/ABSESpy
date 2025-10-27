# ABSESpy Human Module Class Diagram

This document contains the detailed class diagram for the human module, showing the relationships between human system components.

## Human Module Class Diagram

```mermaid
classDiagram
    %% Core Human Components
    class BaseHuman {
        +agents: _ModelAgentsContainer
        +collections: Dict[str, Any]
        +_refers: Dict[str, Dict[str, Any]]
        +define(name: str, **kwargs) void
        +get_collection(name: str) Any
        +setup() void
        +step() void
        +update_human_state() void
    }

    class HumanModule {
        +name: str
        +model: MainModel
        +agents: _ModelAgentsContainer
        +collections: Dict[str, Any]
        +define(name: str, **kwargs) void
        +get_collection(name: str) Any
        +setup() void
        +step() void
    }

    class HumanSystemProtocol {
        <<interface>>
        +agents: _ModelAgentsContainer
        +collections: Dict[str, Any]
        +define(name: str, **kwargs) void
        +get_collection(name: str) Any
        +setup() void
        +step() void
    }

    %% Human Decision Making
    class DecisionMaker {
        +decision_rules: Dict[str, Callable]
        +make_decision(context: Dict) Any
        +evaluate_options(options: List) Any
        +apply_decision(decision: Any) void
    }

    class HumanBehavior {
        +behavior_patterns: Dict[str, Callable]
        +execute_behavior(pattern: str) void
        +update_behavior_state() void
        +learn_from_experience() void
    }

    %% Human Links and Networks
    class _LinkContainer {
        +links: Dict[str, Any]
        +add_link(source: Actor, target: Actor) void
        +remove_link(link_id: str) void
        +get_links(actor: Actor) List[Link]
        +update_network() void
    }

    class _LinkNodeActor {
        +links: List[Link]
        +add_link(target: Actor) void
        +remove_link(target: Actor) void
        +get_neighbors() List[Actor]
        +update_network_position() void
    }

    class Link {
        +source: Actor
        +target: Actor
        +strength: float
        +type: str
        +update_strength() void
        +is_active() bool
    }

    %% Human Collections
    class HumanCollection {
        +name: str
        +members: List[Actor]
        +rules: Dict[str, Any]
        +add_member(actor: Actor) void
        +remove_member(actor: Actor) void
        +apply_collection_rules() void
        +update_collection_state() void
    }

    class SocialNetwork {
        +nodes: Dict[int, Actor]
        +edges: List[Link]
        +add_node(actor: Actor) void
        +add_edge(source: Actor, target: Actor) void
        +remove_node(actor: Actor) void
        +remove_edge(link: Link) void
        +get_network_metrics() Dict[str, float]
    }

    %% Relationships
    BaseHuman ..|> HumanSystemProtocol : implements
    HumanModule --|> BaseHuman : extends

    BaseHuman ||--|| _ModelAgentsContainer : manages
    BaseHuman ||--o{ HumanCollection : contains

    HumanCollection ||--o{ Actor : manages
    HumanCollection ||--|| DecisionMaker : uses

    _LinkContainer ||--o{ Link : manages
    _LinkNodeActor ||--o{ Link : participates in
    Link ||--|| Actor : connects

    SocialNetwork ||--o{ Actor : contains nodes
    SocialNetwork ||--o{ Link : contains edges

    HumanBehavior ||--|| DecisionMaker : uses
    HumanBehavior ||--|| _LinkNodeActor : influences
```

## Key Components

### BaseHuman Class
- **Purpose**: Base class for human system management
- **Key Features**:
  - Agent management through _ModelAgentsContainer
  - Collection management for human groups
  - Reference management for human relationships
  - Setup and step methods for simulation lifecycle

### HumanModule Class
- **Purpose**: Specific implementation of human system
- **Key Features**:
  - Extends BaseHuman with specific functionality
  - Manages human-specific collections
  - Implements human decision-making processes
  - Handles human behavior patterns

### Decision Making Components
- **DecisionMaker**: Manages decision rules and evaluation
- **HumanBehavior**: Implements behavior patterns and learning
- **Decision Rules**: Configurable decision-making logic

### Human Networks
- **_LinkContainer**: Manages links between human actors
- **_LinkNodeActor**: Represents actors in social networks
- **Link**: Represents relationships between actors
- **SocialNetwork**: Manages network structure and metrics

### Human Collections
- **HumanCollection**: Manages groups of human actors
- **Collection Rules**: Define group behavior and interactions
- **Member Management**: Add/remove members from collections

## Design Patterns

- **Module Pattern**: BaseHuman manages human system components
- **Collection Pattern**: HumanCollection manages actor groups
- **Network Pattern**: Social networks manage actor relationships
- **Decision Pattern**: DecisionMaker handles human decision-making
- **Behavior Pattern**: HumanBehavior implements behavior patterns

## Usage Examples

```python
# Create human system
human = model.human

# Define human collections
human.define("farmers", agent_type=Farmer, num=50)
human.define("hunters", agent_type=Hunter, num=20)

# Get collections
farmers = human.get_collection("farmers")
hunters = human.get_collection("hunters")

# Human decision making
decision_maker = DecisionMaker()
decision = decision_maker.make_decision(context)

# Social networks
network = SocialNetwork()
network.add_node(farmer)
network.add_edge(farmer, hunter)

# Human behavior
behavior = HumanBehavior()
behavior.execute_behavior("cooperative")
```