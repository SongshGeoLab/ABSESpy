# ABSESpy Core Module Sequence Diagrams

This document contains sequence diagrams for the core module, showing the interactions between MainModel, BaseNature, BaseHuman, TimeDriver, and DataCollector during key operations.

## Model Initialization Sequence

```mermaid
sequenceDiagram
    participant User
    participant MainModel
    participant BaseNature
    participant BaseHuman
    participant TimeDriver
    participant DataCollector
    participant Logger

    User->>MainModel: MainModel(parameters, **kwargs)

    MainModel->>MainModel: __init__(parameters, human_class, nature_class, **kwargs)
    MainModel->>MainModel: merge_parameters(parameters, **kwargs)
    MainModel->>Logger: setup_model_logger()

    MainModel->>BaseNature: BaseNature(model, name="nature")
    BaseNature->>BaseNature: GeoSpace.__init__(crs=DEFAULT_CRS)
    BaseNature->>BaseNature: BaseSubSystem.__init__(model, name)

    MainModel->>BaseHuman: BaseHuman(model, name="human")
    BaseHuman->>BaseHuman: BaseModule.__init__(model, name)
    BaseHuman->>BaseHuman: define(name, **kwargs)

    MainModel->>TimeDriver: TimeDriver(model)
    TimeDriver->>TimeDriver: __init__(model)
    TimeDriver->>TimeDriver: setup_time_parameters()

    MainModel->>DataCollector: ABSESpyDataCollector(model)
    DataCollector->>DataCollector: __init__(model)

    MainModel->>MainModel: setup()
    MainModel->>BaseNature: setup()
    MainModel->>BaseHuman: setup()

    MainModel-->>User: model instance ready
```

## Model Step Execution Sequence

```mermaid
sequenceDiagram
    participant MainModel
    participant TimeDriver
    participant BaseNature
    participant BaseHuman
    participant DataCollector
    participant Logger

    MainModel->>MainModel: step()

    MainModel->>Logger: log_step_start()

    MainModel->>TimeDriver: go()
    TimeDriver->>TimeDriver: step()
    TimeDriver->>TimeDriver: update_current_time()

    MainModel->>BaseNature: step()
    BaseNature->>BaseNature: update_spatial_state()

    MainModel->>BaseHuman: step()
    BaseHuman->>BaseHuman: update_human_state()

    MainModel->>DataCollector: collect(model)
    DataCollector->>DataCollector: collect_model_vars()
    DataCollector->>DataCollector: collect_agent_vars()

    MainModel->>Logger: log_step_end()

    MainModel->>TimeDriver: is_finished()
    TimeDriver-->>MainModel: boolean result
```

## Data Collection Sequence

```mermaid
sequenceDiagram
    participant MainModel
    participant DataCollector
    participant BaseNature
    participant BaseHuman
    participant ActorsList
    participant Logger

    MainModel->>DataCollector: collect(model)

    DataCollector->>DataCollector: collect_model_vars()

    loop For each model reporter
        DataCollector->>MainModel: call reporter function
        MainModel-->>DataCollector: return value
    end

    DataCollector->>DataCollector: collect_agent_vars()

    DataCollector->>BaseNature: get_agents()
    BaseNature-->>DataCollector: ActorsList

    DataCollector->>BaseHuman: get_agents()
    BaseHuman-->>DataCollector: ActorsList

    loop For each agent reporter
        DataCollector->>ActorsList: apply reporter function
        ActorsList-->>DataCollector: return values
    end

    DataCollector->>DataCollector: store_data()
    DataCollector->>Logger: log_collection_stats()
```

## Model Run Sequence

```mermaid
sequenceDiagram
    participant User
    participant MainModel
    participant TimeDriver
    participant BaseNature
    participant BaseHuman
    participant DataCollector
    participant Logger

    User->>MainModel: run_model()

    MainModel->>Logger: log_run_start()

    MainModel->>MainModel: setup()
    MainModel->>BaseNature: setup()
    MainModel->>BaseHuman: setup()

    loop While not finished
        MainModel->>MainModel: step()

        MainModel->>TimeDriver: go()
        TimeDriver->>TimeDriver: step()

        MainModel->>BaseNature: step()
        BaseNature->>BaseNature: update_spatial_state()

        MainModel->>BaseHuman: step()
        BaseHuman->>BaseHuman: update_human_state()

        MainModel->>DataCollector: collect(model)
        DataCollector->>DataCollector: collect_data()

        MainModel->>TimeDriver: is_finished()
        TimeDriver-->>MainModel: boolean result
    end

    MainModel->>Logger: log_run_end()
    MainModel->>DataCollector: get_model_vars_dataframe()
    DataCollector-->>MainModel: DataFrame

    MainModel-->>User: run completed
```

## Error Handling Sequence

```mermaid
sequenceDiagram
    participant MainModel
    participant BaseNature
    participant BaseHuman
    participant Logger
    participant ErrorHandler

    MainModel->>MainModel: step()

    MainModel->>BaseNature: step()
    BaseNature-->>MainModel: Exception

    MainModel->>ErrorHandler: handle_error(exception)
    ErrorHandler->>Logger: log_error(exception)
    ErrorHandler->>ErrorHandler: determine_recovery_strategy()

    alt Recoverable error
        ErrorHandler->>MainModel: retry_step()
        MainModel->>BaseNature: step()
        BaseNature-->>MainModel: success
    else Fatal error
        ErrorHandler->>MainModel: stop_model()
        MainModel->>Logger: log_fatal_error()
        MainModel-->>User: Model stopped
    end
```

## Key Interactions

### Model Initialization
1. **Parameter Merging**: User parameters are merged with defaults
2. **Subsystem Creation**: BaseNature, BaseHuman, TimeDriver, DataCollector are created
3. **Setup Phase**: All subsystems are initialized in proper order
4. **Logging Setup**: Model-specific logging is configured

### Step Execution
1. **Time Progression**: TimeDriver advances model time
2. **Spatial Updates**: BaseNature updates spatial state
3. **Human Updates**: BaseHuman updates human-related state
4. **Data Collection**: DataCollector gathers model and agent data
5. **Logging**: Step progress is logged

### Data Collection
1. **Model Variables**: Collect model-level data using reporters
2. **Agent Variables**: Collect agent-level data from all subsystems
3. **Storage**: Data is stored for later analysis
4. **Statistics**: Collection statistics are logged

### Error Handling
1. **Exception Capture**: Errors are caught during step execution
2. **Error Classification**: Errors are classified as recoverable or fatal
3. **Recovery Strategy**: Appropriate recovery action is taken
4. **Logging**: All errors are logged with context
