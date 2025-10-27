# ABSESpy Utils Module Class Diagram

This document contains the detailed class diagram for the utils module, showing the relationships between utility components.

## Utils Module Class Diagram

```mermaid
classDiagram
    %% Data Collection
    class ABSESpyDataCollector {
        +model_reporters: Dict[str, Callable]
        +agent_reporters: Dict[str, Callable]
        +model_vars: List[Dict]
        +agent_vars: List[Dict]
        +collect(model: MainModel) void
        +get_model_vars_dataframe() pd.DataFrame
        +get_agent_vars_dataframe() pd.DataFrame
        +add_model_reporter(name: str, func: Callable) void
        +add_agent_reporter(name: str, func: Callable) void
    }

    %% Time Management
    class TimeDriver {
        +tick: int
        +current_time: DateTime
        +end_time: DateTime
        +time_step: Duration
        +go() void
        +step() void
        +is_finished() bool
        +setup_time_parameters() void
        +update_current_time() void
    }

    %% Random Operations
    class ListRandom {
        +generator: np.random.Generator
        +choice(actors: List[Actor]) Actor
        +sample(actors: List[Actor], n: int) List[Actor]
        +shuffle(actors: List[Actor]) List[Actor]
        +new(agent_class: Type[Actor], num: int) ActorsList
        +set_generator(generator: np.random.Generator) void
    }

    %% Configuration Management
    class ConfigManager {
        +config: DictConfig
        +default_config: DictConfig
        +merge_parameters(*configs) DictConfig
        +validate_config(config: DictConfig) bool
        +load_config(file_path: str) DictConfig
        +save_config(config: DictConfig, file_path: str) void
    }

    %% Logging System
    class Logger {
        +logger: loguru.Logger
        +setup_logger_info() void
        +setup_model_logger(model: MainModel) void
        +log_session() void
        +log_step_start() void
        +log_step_end() void
        +log_error(error: Exception) void
    }

    %% Data Loading
    class DataLoader {
        +load_raster(file_path: str) xr.DataArray
        +load_vector(file_path: str) gpd.GeoDataFrame
        +load_csv(file_path: str) pd.DataFrame
        +load_netcdf(file_path: str) xr.Dataset
        +validate_data(data: Any) bool
    }

    %% Spatial Utilities
    class SpatialUtils {
        +distance(pos1: Position, pos2: Position) float
        +neighbors(pos: Position, radius: int) List[Position]
        +within_bounds(pos: Position, bounds: Tuple) bool
        +transform_coordinates(pos: Position, from_crs: str, to_crs: str) Position
        +buffer_geometry(geometry: BaseGeometry, distance: float) BaseGeometry
    }

    %% Function Utilities
    class FuncUtils {
        +get_buffer(data: Any, buffer_size: int) Any
        +set_null_values(data: Any, null_value: Any) Any
        +clean_attrs(obj: Any, attrs: List[str]) Any
        +get_only_item(collection: Collection) Any
        +merge_parameters(*params) DictConfig
    }

    %% Error Handling
    class ErrorHandler {
        +handle_error(error: Exception) void
        +classify_error(error: Exception) str
        +log_error(error: Exception) void
        +recover_from_error(error: Exception) bool
        +stop_model_on_fatal_error(error: Exception) void
    }

    %% Type Definitions
    class TypeAliases {
        <<enumeration>>
        +AgentID
        +Position
        +UniqueID
        +SubSystemName
        +HowCheckName
        +GeoType
        +TargetName
    }

    %% Relationships
    ABSESpyDataCollector ||--|| MainModel : collects from
    ABSESpyDataCollector ||--o{ Callable : uses reporters

    TimeDriver ||--|| MainModel : manages time for
    TimeDriver ||--|| DateTime : uses

    ListRandom ||--|| np.random.Generator : uses
    ListRandom ||--o{ Actor : operates on

    ConfigManager ||--|| DictConfig : manages
    ConfigManager ||--|| DictConfig : uses defaults

    Logger ||--|| loguru.Logger : uses
    Logger ||--|| MainModel : logs for

    DataLoader ||--|| xr.DataArray : loads
    DataLoader ||--|| gpd.GeoDataFrame : loads
    DataLoader ||--|| pd.DataFrame : loads

    SpatialUtils ||--|| Position : operates on
    SpatialUtils ||--|| BaseGeometry : operates on

    FuncUtils ||--|| Any : operates on
    FuncUtils ||--|| DictConfig : merges

    ErrorHandler ||--|| Exception : handles
    ErrorHandler ||--|| Logger : uses
```

## Key Components

### Data Collection
- **ABSESpyDataCollector**: Collects model and agent data during simulation
- **Model Reporters**: Functions that collect model-level data
- **Agent Reporters**: Functions that collect agent-level data
- **Data Storage**: Stores collected data for analysis

### Time Management
- **TimeDriver**: Manages model time progression
- **Time Steps**: Controls simulation time advancement
- **Time Validation**: Ensures time progression is valid
- **Time Queries**: Provides time-related information

### Random Operations
- **ListRandom**: Provides random operations on actor lists
- **Random Selection**: Random choice and sampling operations
- **Random Shuffling**: Random ordering of actors
- **Random Generation**: Random number generation for agents

### Configuration Management
- **ConfigManager**: Manages model configuration
- **Parameter Merging**: Combines multiple configuration sources
- **Config Validation**: Validates configuration parameters
- **Config Persistence**: Loads and saves configuration

### Logging System
- **Logger**: Provides logging functionality
- **Model Logging**: Model-specific logging setup
- **Session Logging**: Session-level logging
- **Error Logging**: Error and exception logging

### Data Loading
- **DataLoader**: Loads various data formats
- **Raster Loading**: Loads raster data (GeoTIFF, NetCDF)
- **Vector Loading**: Loads vector data (Shapefile, GeoJSON)
- **Tabular Loading**: Loads tabular data (CSV, Excel)

### Spatial Utilities
- **SpatialUtils**: Provides spatial operations
- **Distance Calculations**: Calculates distances between positions
- **Neighbor Finding**: Finds neighboring positions
- **Coordinate Transformations**: Transforms coordinates between CRS

### Function Utilities
- **FuncUtils**: Provides general utility functions
- **Data Processing**: Processes data with buffers and null values
- **Attribute Cleaning**: Cleans object attributes
- **Parameter Merging**: Merges parameters from multiple sources

### Error Handling
- **ErrorHandler**: Handles errors and exceptions
- **Error Classification**: Classifies errors by type
- **Error Recovery**: Attempts to recover from errors
- **Fatal Error Handling**: Handles fatal errors appropriately

## Design Patterns

- **Utility Pattern**: Utils provide common functionality
- **Manager Pattern**: Managers handle specific aspects (time, config, logging)
- **Loader Pattern**: Loaders handle data loading operations
- **Handler Pattern**: Handlers manage specific operations (errors, data)
- **Collector Pattern**: Collectors gather and store data

## Usage Examples

```python
# Data collection
collector = ABSESpyDataCollector(model)
collector.add_model_reporter("population", lambda m: len(m.agents))
collector.collect(model)
df = collector.get_model_vars_dataframe()

# Time management
time_driver = TimeDriver(model)
time_driver.go()  # Advance time
is_finished = time_driver.is_finished()

# Random operations
random_ops = ListRandom()
random_actor = random_ops.choice(actors)
sample_actors = random_ops.sample(actors, 10)

# Configuration
config_manager = ConfigManager()
config = config_manager.merge_parameters(user_config, default_config)

# Logging
logger = Logger()
logger.setup_model_logger(model)
logger.log_step_start()

# Data loading
loader = DataLoader()
raster = loader.load_raster("elevation.tif")
vector = loader.load_vector("boundaries.shp")

# Spatial utilities
spatial = SpatialUtils()
distance = spatial.distance(pos1, pos2)
neighbors = spatial.neighbors(pos, radius=2)

# Error handling
error_handler = ErrorHandler()
try:
    model.step()
except Exception as e:
    error_handler.handle_error(e)
```