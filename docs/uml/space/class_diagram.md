# ABSESpy Space Module Class Diagram

This document contains the detailed class diagram for the space module, showing the relationships between spatial components, raster layers, and cells.

## Space Module Class Diagram

```mermaid
classDiagram
    %% Core Spatial Components
    class BaseNature {
        +major_layer: Optional[PatchModule]
        +total_bounds: Tuple[float, float, float, float]
        +crs: str
        +layers: Dict[str, PatchModule]
        +modules: ModuleFactory
        +create_module(name: str, **kwargs) PatchModule
        +get_layer(name: str) PatchModule
        +apply_raster(raster: xr.DataArray, name: str) void
        +setup() void
        +step() void
    }

    class PatchModule {
        +name: str
        +cells: List[PatchCell]
        +raster: xr.DataArray
        +crs: str
        +bounds: Tuple[float, float, float, float]
        +shape: Tuple[int, int]
        +transform: Affine
        +create_cells() List[PatchCell]
        +apply_raster(raster: xr.DataArray) void
        +get_cell(pos: Position) Optional[PatchCell]
        +neighbors(pos: Position, radius: int) List[PatchCell]
    }

    class PatchCell {
        +pos: Position
        +geometry: BaseGeometry
        +agents: _CellAgentsContainer
        +raster_attributes: Dict[str, Any]
        +fertility: float
        +elevation: float
        +land_use: str
        +add_agent(agent: Actor) void
        +remove_agent(agent: Actor) void
        +get_agents() List[Actor]
        +neighbors(radius: int) List[PatchCell]
    }

    %% Raster Attributes
    class raster_attribute {
        <<decorator>>
        +__call__(method: Callable) Callable
    }

    class RasterAttribute {
        +name: str
        +raster: xr.DataArray
        +get_value(pos: Position) Any
        +set_value(pos: Position, value: Any) void
        +apply_to_cells() void
    }

    %% Spatial Operations
    class SpatialOperations {
        +distance(pos1: Position, pos2: Position) float
        +neighbors(pos: Position, radius: int) List[Position]
        +within_bounds(pos: Position, bounds: Tuple) bool
        +transform_coordinates(pos: Position, from_crs: str, to_crs: str) Position
    }

    %% Coordinate Systems
    class CoordinateSystem {
        +crs: str
        +transform: Affine
        +bounds: Tuple[float, float, float, float]
        +to_geographic(pos: Position) Position
        +to_projected(pos: Position) Position
    }

    %% Data Structures
    class xr.DataArray {
        +values: np.ndarray
        +coords: Dict[str, Any]
        +dims: Tuple[str, ...]
        +attrs: Dict[str, Any]
        +sel(**kwargs) DataArray
        +isel(**kwargs) DataArray
        +where(condition: DataArray) DataArray
    }

    class BaseGeometry {
        +bounds: Tuple[float, float, float, float]
        +area: float
        +centroid: Point
        +contains(other: BaseGeometry) bool
        +intersects(other: BaseGeometry) bool
        +buffer(distance: float) BaseGeometry
    }

    class Point {
        +x: float
        +y: float
        +coords: Tuple[float, float]
        +distance(other: Point) float
    }

    %% Relationships
    BaseNature ||--o{ PatchModule : manages
    PatchModule ||--o{ PatchCell : contains
    PatchCell ||--|| _CellAgentsContainer : contains
    PatchCell ||--|| BaseGeometry : has geometry

    PatchModule ||--|| xr.DataArray : uses raster data
    PatchModule ||--|| CoordinateSystem : uses coordinate system

    PatchCell ||--o{ Actor : hosts
    PatchCell ||--o{ RasterAttribute : has attributes

    raster_attribute ..> PatchCell : decorates methods
    RasterAttribute ||--|| xr.DataArray : uses raster data

    SpatialOperations ..> PatchModule : operates on
    SpatialOperations ..> PatchCell : operates on

    BaseGeometry <|-- Point : extends
    PatchCell ||--|| Point : has centroid
```

## Key Components

### BaseNature Class
- **Purpose**: Main spatial subsystem managing all raster layers
- **Key Features**:
  - Module management (`create_module()`, `get_layer()`)
  - Raster application (`apply_raster()`)
  - Coordinate system management (`crs`)
  - Bounds management (`total_bounds`)

### PatchModule Class
- **Purpose**: Individual raster layer containing cells
- **Key Features**:
  - Cell management (`create_cells()`, `get_cell()`)
  - Raster data handling (`raster`, `apply_raster()`)
  - Spatial queries (`neighbors()`)
  - Coordinate transformations

### PatchCell Class
- **Purpose**: Individual spatial unit that can host agents
- **Key Features**:
  - Agent hosting (`agents`, `add_agent()`, `remove_agent()`)
  - Raster attributes (`fertility`, `elevation`, `land_use`)
  - Spatial properties (`pos`, `geometry`)
  - Neighbor queries (`neighbors()`)

### Raster Attributes
- **Purpose**: Dynamic attributes linked to raster data
- **Key Features**:
  - Automatic value extraction from raster
  - Cell-level attribute access
  - Decorator-based implementation (`@raster_attribute`)

## Design Patterns

- **Module Pattern**: BaseNature manages multiple PatchModule instances
- **Cell Pattern**: PatchCell represents individual spatial units
- **Raster Pattern**: Integration with xarray for geospatial data
- **Decorator Pattern**: `@raster_attribute` for dynamic attributes
- **Factory Pattern**: ModuleFactory creates PatchModule instances

## Usage Examples

```python
# Create spatial module
nature = model.nature
dem_module = nature.create_module("dem", shape=(100, 100))

# Apply raster data
dem_raster = xr.open_dataarray("elevation.tif")
dem_module.apply_raster(dem_raster)

# Access cells
cell = dem_module.get_cell((50, 50))
neighbors = cell.neighbors(radius=1)

# Raster attributes
@raster_attribute
def elevation(self) -> float:
    return self.raster.sel(x=self.pos[0], y=self.pos[1]).values

# Agent placement
agent = model.agents.new(Farmer, num=1).item()
cell.add_agent(agent)
```