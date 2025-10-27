# ABSESpy Space Module Sequence Diagrams

This document contains sequence diagrams for the space module, showing the interactions between BaseNature, PatchModule, PatchCell, and raster operations.

## Spatial Module Creation Sequence

```mermaid
sequenceDiagram
    participant User
    participant BaseNature
    participant PatchModule
    participant PatchCell
    participant xr.DataArray
    participant Logger

    User->>BaseNature: nature.create_module("dem", shape=(100, 100))

    BaseNature->>BaseNature: validate_module_name("dem")
    BaseNature->>PatchModule: PatchModule(name="dem", shape=(100, 100))

    PatchModule->>PatchModule: __init__(name, shape, **kwargs)
    PatchModule->>PatchModule: initialize_coordinate_system()
    PatchModule->>PatchModule: create_raster_array(shape)
    PatchModule->>xr.DataArray: create_empty_raster(shape)
    xr.DataArray-->>PatchModule: empty_raster

    PatchModule->>PatchModule: create_cells()

    loop For each cell position
        PatchModule->>PatchCell: PatchCell(pos, geometry)
        PatchCell->>PatchCell: __init__(pos, geometry)
        PatchCell->>PatchCell: initialize_attributes()
        PatchCell-->>PatchModule: cell_instance
    end

    PatchModule->>BaseNature: register_module(module)
    BaseNature->>BaseNature: add_to_layers("dem", module)
    BaseNature->>Logger: log_module_creation("dem")

    BaseNature-->>User: PatchModule instance
```

## Raster Application Sequence

```mermaid
sequenceDiagram
    participant User
    participant BaseNature
    participant PatchModule
    participant PatchCell
    participant xr.DataArray
    participant Logger

    User->>BaseNature: nature.apply_raster(raster_data, "elevation")

    BaseNature->>BaseNature: get_layer("elevation")
    BaseNature->>PatchModule: get_layer("elevation")
    PatchModule-->>BaseNature: elevation_module

    BaseNature->>PatchModule: apply_raster(raster_data)
    PatchModule->>PatchModule: validate_raster_compatibility(raster_data)
    PatchModule->>PatchModule: update_raster_data(raster_data)
    PatchModule->>xr.DataArray: update_values(raster_data)
    xr.DataArray-->>PatchModule: updated_raster

    PatchModule->>PatchModule: update_cell_attributes()

    loop For each cell
        PatchModule->>PatchCell: update_raster_attributes()
        PatchCell->>PatchCell: extract_values_from_raster()
        PatchCell->>PatchCell: update_attributes()
        PatchCell-->>PatchModule: attributes_updated
    end

    PatchModule->>Logger: log_raster_application("elevation")
    PatchModule-->>BaseNature: raster_applied
    BaseNature-->>User: raster application completed
```

## Cell Agent Interaction Sequence

```mermaid
sequenceDiagram
    participant Actor
    participant PatchCell
    participant _CellAgentsContainer
    participant PatchModule
    participant Logger

    Actor->>PatchCell: cell.add_agent(actor)

    PatchCell->>PatchCell: validate_agent(actor)
    PatchCell->>_CellAgentsContainer: add_agent(actor)
    _CellAgentsContainer->>_CellAgentsContainer: register_agent(actor)
    _CellAgentsContainer->>Actor: set_cell_reference(cell)

    PatchCell->>PatchModule: notify_agent_added(actor)
    PatchModule->>PatchModule: update_cell_statistics()

    PatchCell->>Logger: log_agent_addition(actor)
    PatchCell-->>Actor: agent_added_successfully

    Note over Actor,Logger: Agent can now access cell attributes

    Actor->>PatchCell: cell.fertility
    PatchCell->>PatchCell: get_raster_attribute("fertility")
    PatchCell-->>Actor: fertility_value

    Actor->>PatchCell: cell.neighbors(radius=1)
    PatchCell->>PatchModule: get_neighbors(pos, radius)
    PatchModule->>PatchModule: find_neighboring_cells()
    PatchModule-->>PatchCell: neighboring_cells
    PatchCell-->>Actor: neighbor_cells
```

## Raster Attribute Access Sequence

```mermaid
sequenceDiagram
    participant Actor
    participant PatchCell
    participant PatchModule
    participant xr.DataArray
    participant Logger

    Actor->>PatchCell: cell.fertility

    PatchCell->>PatchCell: get_raster_attribute("fertility")
    PatchCell->>PatchModule: get_raster_value(pos, "fertility")

    PatchModule->>PatchModule: validate_attribute_exists("fertility")
    PatchModule->>xr.DataArray: sel(x=pos[0], y=pos[1])
    xr.DataArray->>xr.DataArray: extract_value_at_position()
    xr.DataArray-->>PatchModule: raster_value

    PatchModule->>PatchModule: process_raster_value(value)
    PatchModule-->>PatchCell: processed_value
    PatchCell->>PatchCell: cache_attribute_value("fertility", value)
    PatchCell-->>Actor: fertility_value

    Note over Actor,Logger: Value is cached for future access

    Actor->>PatchCell: cell.fertility
    PatchCell->>PatchCell: get_cached_attribute("fertility")
    PatchCell-->>Actor: cached_value
```

## Spatial Query Sequence

```mermaid
sequenceDiagram
    participant User
    participant PatchModule
    participant PatchCell
    participant BaseGeometry
    participant Logger

    User->>PatchModule: module.neighbors(pos, radius=2)

    PatchModule->>PatchModule: validate_position(pos)
    PatchModule->>PatchModule: calculate_search_bounds(pos, radius)
    PatchModule->>PatchModule: find_cells_in_bounds()

    loop For each cell in bounds
        PatchModule->>PatchCell: get_geometry()
        PatchCell->>BaseGeometry: get_geometry()
        BaseGeometry-->>PatchCell: geometry

        PatchModule->>BaseGeometry: distance_to(pos)
        BaseGeometry->>BaseGeometry: calculate_distance()
        BaseGeometry-->>PatchModule: distance

        PatchModule->>PatchModule: check_distance_threshold(distance, radius)

        alt Within radius
            PatchModule->>PatchModule: add_to_neighbors(cell)
        end
    end

    PatchModule->>Logger: log_spatial_query(pos, radius, neighbor_count)
    PatchModule-->>User: neighboring_cells
```

## Cell Attribute Update Sequence

```mermaid
sequenceDiagram
    participant User
    participant PatchCell
    participant PatchModule
    participant xr.DataArray
    participant Logger

    User->>PatchCell: cell.fertility = 0.8

    PatchCell->>PatchCell: validate_attribute("fertility")
    PatchCell->>PatchCell: update_local_attribute("fertility", 0.8)
    PatchCell->>PatchModule: notify_attribute_change("fertility", 0.8)

    PatchModule->>PatchModule: update_raster_at_position(pos, "fertility", 0.8)
    PatchModule->>xr.DataArray: update_value_at_position(pos, 0.8)
    xr.DataArray->>xr.DataArray: set_value_at_coordinates()
    xr.DataArray-->>PatchModule: value_updated

    PatchModule->>PatchModule: invalidate_cell_cache(pos)
    PatchModule->>PatchCell: clear_cached_attributes()
    PatchCell->>PatchCell: clear_attribute_cache()

    PatchModule->>Logger: log_attribute_update("fertility", pos, 0.8)
    PatchModule-->>PatchCell: attribute_updated
    PatchCell-->>User: update_completed
```

## Key Interactions

### Spatial Module Creation
1. **Module Validation**: Module name and parameters are validated
2. **Raster Initialization**: Empty raster array is created
3. **Cell Creation**: Individual cells are created for each position
4. **Registration**: Module is registered with BaseNature
5. **Logging**: Creation process is logged

### Raster Application
1. **Compatibility Check**: Raster data is validated for compatibility
2. **Data Update**: Raster array is updated with new data
3. **Cell Update**: All cells are updated with new attribute values
4. **Caching**: Attribute values are cached for performance
5. **Logging**: Application process is logged

### Cell Agent Interaction
1. **Agent Validation**: Agent is validated before addition
2. **Container Update**: Agent is added to cell's agent container
3. **Reference Setting**: Agent's cell reference is set
4. **Statistics Update**: Cell statistics are updated
5. **Logging**: Agent addition is logged

### Raster Attribute Access
1. **Position Lookup**: Raster value is extracted at cell position
2. **Value Processing**: Raw raster value is processed
3. **Caching**: Value is cached for future access
4. **Return**: Processed value is returned to caller

### Spatial Query
1. **Bounds Calculation**: Search bounds are calculated
2. **Distance Calculation**: Distance to each cell is calculated
3. **Threshold Check**: Cells within radius are identified
4. **Result Collection**: Neighboring cells are collected
5. **Logging**: Query results are logged

### Cell Attribute Update
1. **Validation**: Attribute update is validated
2. **Local Update**: Cell's local attribute is updated
3. **Raster Update**: Raster data is updated at position
4. **Cache Invalidation**: Cached values are cleared
5. **Logging**: Update process is logged
