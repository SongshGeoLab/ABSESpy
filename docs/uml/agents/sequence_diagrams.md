# ABSESpy Agents Module Sequence Diagrams

This document contains sequence diagrams for the agents module, showing the interactions between Actor, ActorsList, and various container classes during agent operations.

## Agent Creation Sequence

```mermaid
sequenceDiagram
    participant User
    participant MainModel
    participant _ModelAgentsContainer
    participant Actor
    participant PatchCell
    participant Logger

    User->>MainModel: model.agents.new(Farmer, num=5)

    MainModel->>_ModelAgentsContainer: new(Farmer, num=5, **kwargs)

    _ModelAgentsContainer->>_ModelAgentsContainer: validate_agent_class(Farmer)
    _ModelAgentsContainer->>_ModelAgentsContainer: generate_agent_ids(5)

    loop For each agent (5 times)
        _ModelAgentsContainer->>Actor: Farmer(model, **kwargs)
        Actor->>Actor: __init__(model, **kwargs)
        Actor->>Actor: set_unique_id(agent_id)
        Actor->>Actor: initialize_attributes()
        Actor->>Logger: log_agent_creation()

        _ModelAgentsContainer->>_ModelAgentsContainer: register_agent(actor)
        _ModelAgentsContainer->>Actor: set_model_reference(model)
    end

    _ModelAgentsContainer->>_ModelAgentsContainer: create_ActorsList(agents)
    _ModelAgentsContainer-->>MainModel: ActorsList[Farmer]
    MainModel-->>User: ActorsList[Farmer]
```

## Agent Selection Sequence

```mermaid
sequenceDiagram
    participant User
    participant MainModel
    participant _ModelAgentsContainer
    participant ActorsList
    participant Actor
    participant Logger

    User->>MainModel: model.agents.select(lambda a: a.energy > 50)

    MainModel->>_ModelAgentsContainer: select(selection_func, agent_type=None)

    _ModelAgentsContainer->>_ModelAgentsContainer: get_all_agents()
    _ModelAgentsContainer->>_ModelAgentsContainer: filter_by_type(agent_type)

    loop For each agent
        _ModelAgentsContainer->>Actor: check_selection_criteria(agent)
        Actor-->>_ModelAgentsContainer: boolean result
    end

    _ModelAgentsContainer->>_ModelAgentsContainer: create_filtered_list(matching_agents)
    _ModelAgentsContainer->>ActorsList: ActorsList(filtered_agents)
    ActorsList->>ActorsList: __init__(agents, model)

    _ModelAgentsContainer-->>MainModel: ActorsList
    MainModel-->>User: ActorsList
```

## Batch Operations Sequence

```mermaid
sequenceDiagram
    participant User
    participant ActorsList
    participant Actor
    participant Logger
    participant ListRandom

    User->>ActorsList: actors.shuffle_do("work")

    ActorsList->>ActorsList: validate_method_exists("work")
    ActorsList->>ListRandom: shuffle(agents)
    ListRandom->>ListRandom: random.shuffle(agents)
    ListRandom-->>ActorsList: shuffled_agents

    loop For each agent in shuffled order
        ActorsList->>Actor: work()
        Actor->>Actor: execute_work_method()
        Actor->>Logger: log_action("work")
        Actor-->>ActorsList: method_completed
    end

    ActorsList->>Logger: log_batch_operation_complete()
    ActorsList-->>User: operation completed
```

## Agent Movement Sequence

```mermaid
sequenceDiagram
    participant Actor
    participant PatchCell
    participant _CellAgentsContainer
    participant PatchModule
    participant Logger

    Actor->>Actor: move(target_position)

    Actor->>Actor: validate_target_position(target_position)
    Actor->>PatchModule: get_cell(target_position)
    PatchModule-->>Actor: target_cell

    alt Target cell exists
        Actor->>PatchCell: add_agent(actor)
        PatchCell->>_CellAgentsContainer: add_agent(actor)
        _CellAgentsContainer->>_CellAgentsContainer: register_agent(actor)

        Actor->>Actor: remove_from_current_cell()
        Actor->>PatchCell: remove_agent(actor)
        PatchCell->>_CellAgentsContainer: remove_agent(actor)

        Actor->>Actor: update_position(target_position)
        Actor->>Logger: log_movement()
    else Target cell not found
        Actor->>Logger: log_movement_error()
        Actor-->>Actor: movement_failed
    end
```

## Agent Death Sequence

```mermaid
sequenceDiagram
    participant Actor
    participant MainModel
    participant _ModelAgentsContainer
    participant PatchCell
    participant _CellAgentsContainer
    participant Logger

    Actor->>Actor: die()

    Actor->>Actor: set_alive_status(False)
    Actor->>Logger: log_death()

    Actor->>MainModel: deregister_agent(actor)
    MainModel->>_ModelAgentsContainer: deregister_agent(actor)
    _ModelAgentsContainer->>_ModelAgentsContainer: remove_from_agents_dict(actor)

    alt Actor is on a cell
        Actor->>PatchCell: remove_agent(actor)
        PatchCell->>_CellAgentsContainer: remove_agent(actor)
        _CellAgentsContainer->>_CellAgentsContainer: remove_from_agents_list(actor)
    end

    Actor->>Actor: cleanup_resources()
    Actor->>Logger: log_cleanup_complete()

    _ModelAgentsContainer-->>MainModel: agent_deregistered
    MainModel-->>Actor: death_completed
```

## Chainable Operations Sequence

```mermaid
sequenceDiagram
    participant User
    participant ActorsList
    participant Actor
    participant Logger

    User->>ActorsList: actors.select(lambda a: a.energy > 0).sample(10).shuffle_do("work")

    ActorsList->>ActorsList: select(lambda a: a.energy > 0)
    ActorsList->>ActorsList: filter_by_condition()
    ActorsList-->>ActorsList: filtered_ActorsList

    ActorsList->>ActorsList: sample(10)
    ActorsList->>ActorsList: random_sample(10)
    ActorsList-->>ActorsList: sampled_ActorsList

    ActorsList->>ActorsList: shuffle_do("work")
    ActorsList->>ActorsList: validate_method_exists("work")

    loop For each agent
        ActorsList->>Actor: work()
        Actor->>Actor: execute_work_method()
        Actor-->>ActorsList: method_completed
    end

    ActorsList->>Logger: log_chain_operation_complete()
    ActorsList-->>User: chain_operation_completed
```

## Key Interactions

### Agent Creation
1. **Validation**: Agent class is validated before creation
2. **ID Generation**: Unique IDs are generated for each agent
3. **Initialization**: Each agent is properly initialized with model reference
4. **Registration**: Agents are registered in the container
5. **Collection**: Agents are returned as an ActorsList

### Agent Selection
1. **Filtering**: Agents are filtered based on selection criteria
2. **Type Filtering**: Optional agent type filtering
3. **Collection Creation**: Filtered agents are returned as ActorsList
4. **Chainable**: Selection can be chained with other operations

### Batch Operations
1. **Method Validation**: Target method is validated before execution
2. **Randomization**: Agents are shuffled for random execution order
3. **Batch Execution**: Method is called on each agent
4. **Logging**: All operations are logged for debugging

### Agent Movement
1. **Position Validation**: Target position is validated
2. **Cell Lookup**: Target cell is found in the spatial module
3. **Container Updates**: Agent is moved between cell containers
4. **Position Update**: Agent's position is updated

### Agent Death
1. **Status Update**: Agent's alive status is set to False
2. **Deregistration**: Agent is removed from model container
3. **Cell Removal**: Agent is removed from current cell
4. **Cleanup**: Agent resources are cleaned up

### Chainable Operations
1. **Method Chaining**: Operations can be chained together
2. **Lazy Evaluation**: Operations are executed in sequence
3. **Result Passing**: Results are passed between operations
4. **Final Execution**: Final operation is executed on the result
