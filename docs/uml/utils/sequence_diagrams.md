# Utils Module Sequence Diagrams

This document contains sequence diagrams for the Utils module, showing the key flows for data collection and random operations.

## Data Collection Flow

This diagram shows how data is collected during simulation steps.

```mermaid
sequenceDiagram
    participant Model as MainModel
    participant DC as ABSESpyDataCollector
    participant Agent as Actor
    participant Nature as BaseNature
    participant Human as BaseHuman

    Note over Model: Step execution begins
    Model->>DC: collect()

    Note over DC: Collect model-level data
    DC->>Model: get_model_vars()
    Model-->>DC: model_data

    Note over DC: Collect agent data
    DC->>Model: get_agent_vars()
    Model->>Agent: get_agent_data()
    Agent-->>Model: agent_data
    Model-->>DC: agent_data

    Note over DC: Collect nature data
    DC->>Nature: get_nature_vars()
    Nature-->>DC: nature_data

    Note over DC: Collect human data
    DC->>Human: get_human_vars()
    Human-->>DC: human_data

    Note over DC: Store collected data
    DC->>DC: store_data()

    Note over Model: Step execution continues
```

## Random Operations Flow

This diagram shows how random operations are performed on agent lists.

```mermaid
sequenceDiagram
    participant AgentList as ActorsList
    participant Random as ListRandom
    participant Agent as Actor
    participant Model as MainModel

    Note over AgentList: Random operation requested
    AgentList->>Random: random.choice()

    Note over Random: Generate random selection
    Random->>Random: generate_random_index()
    Random->>AgentList: get_item(index)
    AgentList-->>Random: selected_agent

    Random-->>AgentList: selected_agent

    Note over AgentList: Apply operation to selected agent
    AgentList->>Agent: apply_operation()
    Agent-->>AgentList: result

    Note over AgentList: Return result
    AgentList-->>Model: operation_result
```

## Variable Management Flow

This diagram shows how dynamic variables are managed and updated.

```mermaid
sequenceDiagram
    participant Model as MainModel
    participant Var as BaseDynamicVariable
    participant DC as ABSESpyDataCollector

    Note over Model: Variable update requested
    Model->>Var: update()

    Note over Var: Calculate new value
    Var->>Var: calculate_value()
    Var->>Var: validate_value()

    Note over Var: Store updated value
    Var->>Var: store_value()

    Note over Var: Notify data collector
    Var->>DC: notify_change()
    DC->>DC: update_collection()

    Note over Var: Return updated value
    Var-->>Model: updated_value
```

## Data Export Flow

This diagram shows how collected data is exported to different formats.

```mermaid
sequenceDiagram
    participant DC as ABSESpyDataCollector
    participant Model as MainModel
    participant File as FileSystem

    Note over DC: Export requested
    DC->>DC: prepare_export()

    Note over DC: Convert to DataFrame
    DC->>DC: to_dataframe()
    DC->>DC: format_data()

    Note over DC: Export to file
    DC->>File: write_csv()
    File-->>DC: success

    Note over DC: Return export info
    DC-->>Model: export_complete
```

## Error Handling Flow

This diagram shows how errors are handled in utility operations.

```mermaid
sequenceDiagram
    participant Model as MainModel
    participant Utils as UtilsModule
    participant Logger as Logger

    Note over Model: Operation with potential error
    Model->>Utils: perform_operation()

    alt Operation succeeds
        Utils-->>Model: success_result
    else Operation fails
        Utils->>Logger: log_error()
        Logger->>Logger: format_error_message()
        Utils->>Utils: handle_error()
        Utils-->>Model: error_result
    end

    Note over Model: Continue with error handling
    Model->>Model: handle_result()
```
