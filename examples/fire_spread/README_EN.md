# Forest Fire Spread Model

A classic forest fire propagation model that **demonstrates ABSESpy's unique spatial modeling capabilities**.

## Model Overview

Simulates wildfire propagation process:
- Trees are randomly distributed on a grid
- Trees in the leftmost column are ignited
- Fire spreads to adjacent (non-diagonal) trees
- Burned trees become scorched and cannot burn again

## 🎯 Core ABSESpy Features Demonstrated

This example showcases the following ABSESpy-specific features:

| Feature | Description | Code Location |
|---------|-------------|---------------|
| **PatchCell** | Spatial grid cell base class with state management | `Tree(PatchCell)` |
| **@raster_attribute** | Decorator to extract cell properties as raster data | `@raster_attribute def state()` |
| **neighboring()** | Get neighbor cells (Moore/Von Neumann) | `self.neighboring(moore=False)` |
| **select()** | Flexible cell filtering (dict/function/string) | `neighbors.select({"state": 1})` |
| **trigger()** | Batch method invocation | `cells.trigger("ignite")` |
| **ActorsList** | Enhanced agent list for batch operations | `ActorsList(self, cells)` |
| **nature.create_module()** | Create spatial modules (raster/vector) | `self.nature.create_module()` |
| **get_raster() / get_xarray()** | Extract raster data (numpy/xarray) | `self.nature.get_raster("state")` |
| **Experiment** | Batch experiment management (repeats/sweeps) | `Experiment(Forest, cfg)` |
| **Hydra Integration** | YAML configuration management | `@hydra.main()` |

## Running the Model

```bash
# Direct run (uses config.yaml)
cd examples/fire_spread
python model.py

# Run as module
python -m examples.fire_spread.model

# Batch run (11 repetitions)
python model.py
```

## Key Features Explained

### 1. **PatchCell + @raster_attribute**: Spatial State Management

```python
class Tree(PatchCell):  # ✨ ABSESpy: Spatial cell base class
    """Tree with 4 states: 0=empty, 1=intact, 2=burning, 3=scorched"""

    @raster_attribute  # ✨ ABSESpy: Property extractable as raster
    def state(self) -> int:
        """State can be extracted as spatial raster data"""
        return self._state
```

**Why is this special?**
- `@raster_attribute`: Automatically converts cell properties to spatial raster data
- No manual array construction needed—just call `module.get_raster('state')`
- Supports xarray format with preserved spatial coordinates

---

### 2. **neighboring() + select()**: Spatial Neighbor Interaction

```python
def step(self):
    if self._state == 2:  # If burning
        # ✨ ABSESpy: Get neighbor cells
        neighbors = self.neighboring(moore=False, radius=1)
        # ✨ ABSESpy: Filter cells with dict syntax
        neighbors.select({"state": 1}).trigger("ignite")
        self._state = 3
```

**Why is this special?**
- `neighboring()`: One-line neighbor retrieval (Moore/Von Neumann)
- `select({"state": 1})`: Dict syntax cleaner than lambda
- `trigger()`: Batch method calls, avoiding manual loops

---

### 3. **ActorsList + trigger()**: Batch Operations

```python
# ✨ ABSESpy: ActorsList batch operations
chosen_patches = grid.random.choice(self.num_trees, replace=False)
chosen_patches.trigger("grow")  # Batch call grow method

# Batch ignite leftmost column
ActorsList(self, grid.array_cells[:, 0]).trigger("ignite")
```

**Why is this special?**
- `ActorsList`: Enhanced agent list supporting method chaining
- `trigger()`: Batch method invocation without explicit loops
- `random.choice()`: Integrated with numpy random generator

---

### 4. **get_raster() / get_xarray()**: Raster Data Extraction

```python
# ✨ ABSESpy: Extract as numpy array
state_array = self.nature.get_raster("state")
# shape: (1, 100, 100)

# ✨ ABSESpy: Extract as xarray (with coordinates)
state_xr = self.nature.get_xarray("state")
# Can be directly used for visualization and spatial analysis
state_xr.plot(cmap=cmap)
```

**Why is this special?**
- Automatically collects attributes from all cells and constructs raster
- `get_xarray()`: Preserves spatial coordinates for geospatial analysis
- Seamless integration with rasterio/xarray ecosystem

---

### 5. **Experiment + Hydra**: Batch Experiment Management

```python
# ✨ ABSESpy: Hydra configuration management
@hydra.main(version_base=None, config_path="", config_name="config")
def main(cfg: Optional[DictConfig] = None):
    # ✨ ABSESpy: Experiment batch runs
    exp = Experiment(Forest, cfg=cfg)
    exp.batch_run()  # Run 11 repetitions
```

**Why is this special?**
- Hydra integration: YAML configuration with command-line overrides
- `Experiment`: Automatically handles repeats and parameter sweeps
- Output management: Auto-creates timestamped directories, saves logs and data

## Configuration File (`config.yaml`)

```yaml
defaults:
  - default
  - _self_

exp:
  name: fire_spread
  outdir: out  # Output directory
  repeats: 11  # Run 11 repetitions

model:
  density: 0.4  # Tree density (40% of cells have trees)
  shape: [100, 100]  # Grid size

time:
  end: 25  # Maximum 25 steps

reports:
  final:
    burned: "burned_rate"  # Collect final burn rate
```

## Testing

```bash
# Run complete test suite
pytest tests/examples/test_fire.py -v

# Test coverage:
# - Tree cell functionality (2 tests)
# - Forest model (4 tests, parameterized)
```

**Test Results**: ✅ 6/6 all passed

## Output Results

After running, generates in `out/fire_spread/YYYY-MM-DD/HH-MM-SS/`:
- `fire_spread.log`: Run logs
- Data collection results (if configured)

## Performance Metrics

```python
@property
def burned_rate(self) -> float:
    """Calculate burn rate"""
    state = self.nature.get_raster("state")
    return np.squeeze(state == 3).sum() / self.num_trees
```

## 🎓 Learning Points

### ABSESpy vs Pure Mesa/NetLogo

| Feature | ABSESpy | Pure Mesa | NetLogo |
|---------|---------|-----------|---------|
| **Get Neighbors** | `cell.neighboring(moore=False)` | Manual implementation | `neighbors4` |
| **Filter by Attribute** | `cells.select({"state": 1})` | Manual loop + filter | `with [state = 1]` |
| **Batch Call** | `cells.trigger("ignite")` | Manual loop | `ask patches [ ignite ]` |
| **Raster Extraction** | `module.get_raster("state")` | Manual array construction | `export-view` |
| **Configuration** | Hydra YAML | Manual parsing | BehaviorSpace |
| **Batch Experiments** | `Experiment.batch_run()` | Manual loop | BehaviorSpace |

### Key Advantages

1. **Declarative Syntax**: `select({"state": 1})` cleaner than `filter(lambda x: x.state == 1)`
2. **Automatic Rasterization**: `@raster_attribute` eliminates manual array construction
3. **Spatial Operations**: `neighboring()` encapsulates common neighbor patterns
4. **Batch Experiments**: `Experiment` auto-manages outputs and logs
5. **Geospatial Integration**: Native support for xarray/rasterio/geopandas

## Extension Ideas

Try experimenting with:
- Modify tree density and observe burn rate changes
- Add wind direction (faster spread in one direction)
- Implement different tree species (varying burn probability)
- Add firefighter agents
- Collect more metrics (spread rate, area, etc.)

## Theoretical Background

This model demonstrates:
- **Percolation Theory**: Connectivity at critical density
- **Spatial Diffusion**: Local interactions produce global patterns
- **Simple Rules, Complex Phenomena**: Simple burning rules create complex spread patterns

---

*This model is an ideal starting point for learning ABSESpy—simple yet feature-complete.*

