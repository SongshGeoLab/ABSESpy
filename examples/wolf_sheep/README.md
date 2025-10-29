# Wolf-Sheep Predation Model

A classic predator-prey model demonstrating ABSESpy's advanced agent-based modeling capabilities, showcasing how modern Python frameworks make complex simulations accessible.

## Overview

This model simulates an ecosystem with three components:
- **🌿 Grass**: Regenerates after being consumed
- **🐑 Sheep**: Herbivores that graze on grass
- **🐺 Wolves**: Carnivores that hunt sheep

Each agent consumes energy to survive, gains energy by feeding, and reproduces probabilistically based on configuration.

## Quick Start

```python
from model import WolfSheepModel
import hydra

# Load configuration
with hydra.initialize(config_path=".", version_base=None):
    cfg = hydra.compose(config_name="config")

# Create and run model
model = WolfSheepModel(parameters=cfg)
model.run_model(steps=200)

# Access results
print(f"Final populations: {model.n_sheep} sheep, {model.n_wolves} wolves")
```

See `wolf_sheep_quick_start.ipynb` for a complete interactive tutorial.

## Key ABSESpy Features Demonstrated

### 1. **Batch Operations with `shuffle_do()`**
Execute operations on all agents or cells with a single line:

```python
# Move all agents randomly
self.agents.shuffle_do("move_to", to="random", layer=grassland)

# Grow grass on all cells
self.nature.grassland.cells_lst.shuffle_do("grow")
```

### 2. **Dynamic Spatial Visualization**
Plot agent distributions with `.plot()`:

```python
# Visualize where agents are located
sheep_map = grassland.count_agents(Sheep, dtype="xarray")
sheep_map.plot(cmap="YlGn", title="Sheep Distribution")
```

### 3. **Agent Movement Wrapper**
Convenient movement methods:

```python
# In model setup
self.agents.shuffle_do("move_to", to="random", layer=grassland)
```

Behind the scenes, a simple wrapper enables batch operations:

```python
def move_to(self, to="random", layer=None):
    """Move actor to a location (wrapper for move.to)."""
    self.move.to(to=to, layer=layer)
```

### 4. **Automatic Data Collection**
Configure reporting in `config.yaml`:

```yaml
reports:
  model:
    n_sheep: "n_sheep"
    n_wolves: "n_wolves"
    population_ratio: "population_ratio"
```

Access collected data:

```python
data = model.datacollector.get_model_vars_dataframe()
data.plot()
```

### 5. **Module-Level Agent Counting**
Count agents across entire spatial modules:

```python
# Returns numpy array (default)
sheep_array = grassland.count_agents(Sheep)

# Returns xarray with spatial coordinates (recommended)
sheep_xda = grassland.count_agents(Sheep, dtype="xarray")
```

### 6. **Energy-Based Lifecycle**
Natural agent lifecycle with automatic cleanup:

```python
def update(self):
    self.energy -= 1
    if self.energy <= 0:
        self.die()  # Automatic removal
```

## Comparison with Other Frameworks

### Mesa (Python)

| Task | Mesa | ABSESpy |
|------|------|---------|
| Agent movement | Manual iteration<br>`for agent in self.schedule.agents:`<br>`    agent.move()` | `self.agents.shuffle_do("move_to", layer=grassland)` |
| Agent placement | Manual placement logic | `agents.new()` + `shuffle_do()` with params |
| Spatial queries | Iterate all cells | `module.count_agents(type, dtype="xarray")` |
| Data collection | Manual `self.datacollector.collect()` in each step | **Declarative in config.yaml - no manual calls** |
| Visualization | External plotting code | **Built-in `.plot()` with CRS support** |
| Config management | Hard-coded parameters | **Hydra-based YAML configuration** |

### NetLogo (Logo-based)

| Feature | NetLogo | ABSESpy |
|---------|---------|---------|
| Language | Logo dialect | **Pure Python with type hints** |
| Batch ops | `ask patches [ ... ]` | `cells_lst.shuffle_do("method")` |
| Agent creation | `create-turtles 100` | `agents.new(Agent, 100)` |
| Spatial data | Custom patches | **@raster_attribute with automatic raster extraction** |
| Extensibility | Limited to NetLogo primitives | **Full Python ecosystem (pandas, xarray, sklearn)** |
| Data export | Limited | **pandas/xarray integration - export to CSV, NetCDF, GeoTIFF** |
| Configuration | Hard-coded | **YAML-based declarative config** |

## Model Configuration

Configuration is managed via `config.yaml`:

```yaml
model:
  shape: [50, 50]      # Grid dimensions
  n_sheep: 50          # Initial sheep population
  n_wolves: 10         # Initial wolf population
  rep_rate: 0.01        # Reproduction probability

time:
  end: 200              # Simulation length

reports:
  stepwise:
    n_sheep: "n_sheep"
    n_wolves: "n_wolves"
    population_ratio: "population_ratio"
```

## Agent Behavior

### Energy System
- **Initial**: 50 energy (high to allow survival)
- **Consumption**: -1 per tick
- **Sheep eating grass**: +3 energy
- **Wolves eating sheep**: +10 energy
- **Death**: when energy ≤ 0

### Movement
- **Random walk**: `agent.move.random()`
- **Spatial constraints**: Grid boundaries enforced

### Reproduction
- **Probability**: Based on `rep_rate` parameter
- **Energy cost**: Splits agent energy in half
- **Offspring placement**: Current cell

## ABSESpy Advantages

### 1. **Declarative Configuration with Hydra**
Automatic data collection configured in YAML:

```yaml
reports:
  stepwise:
    n_sheep: "n_sheep"  # Auto-collected every step
    n_wolves: "n_wolves"
    population_ratio: "population_ratio"
```

No need to manually call `collect()` - ABSESpy handles it automatically.

### 2. **Module-Level Spatial Operations**
Count agents across entire spatial modules with one call:

```python
# Returns xarray with full spatial metadata
sheep_map = grassland.count_agents(Sheep, dtype="xarray")
sheep_map.plot()  # Automatic spatial visualization
```

### 3. **Batch Operations with Parameter Passing**
Mesa's `shuffle_do` works on methods, but ABSESpy extends it to pass parameters:

```python
# Pass parameters to batch operations
self.agents.shuffle_do("move_to", to="random", layer=grassland)
```

### 4. **Integrated Spatial Data Framework**
Built-in support for geospatial operations:

```python
# Direct xarray integration
grassland.count_agents(Sheep, dtype="xarray")  # Full CRS, transform, coords
```

### 5. **Type Safety and Modern Python**
Python's type system provides:
- Auto-completion in IDEs
- Type checking with mypy
- Better error messages

### 6. **Seamless Ecosystem Integration**
Works with the entire Python scientific stack:
- pandas for data analysis
- xarray for geospatial data
- matplotlib/seaborn for visualization
- scikit-learn for machine learning

## Files

- `model.py` - Main model implementation
- `config.yaml` - Configuration file
- `wolf_sheep_quick_start.ipynb` - Interactive tutorial
- `README.md` - This file

## Running the Model

### Command Line
```bash
cd examples/wolf_sheep
python model.py
```

### Jupyter Notebook
Open `wolf_sheep_quick_start.ipynb` for an interactive tutorial.

### Batch Experiments
```python
from abses import Experiment

exp = Experiment.new(
    model_cls=WolfSheepModel,
    cfg=cfg,
    seed=42
)

exp.batch_run(
    overrides={"model.n_wolves": [5, 10, 15, 20, 25]},
    repeats=5
)
```

## Results

Typical simulation shows:
- **Balanced dynamics**: Both populations can coexist
- **Cycles**: Predator-prey oscillations
- **Spatial patterns**: Clustering due to movement and interactions

For detailed analysis, see the notebook which includes:
- Population dynamics plots
- Spatial distribution visualization
- Statistical summaries
- Batch experiment results
