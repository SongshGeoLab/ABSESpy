---
title: Configuration Schema
authors: ABSESpy Team
date: 2024-12-20
---

# Configuration Schema Reference

This document provides a comprehensive reference for the ABSESpy configuration schema. All configurations are managed through [Hydra](https://hydra.cc/) and use YAML format. The schema is designed to be simple, clear, and support both single-run experiments and parameter sweeps.

## Overview

ABSESpy uses a hierarchical configuration system based on OmegaConf (via Hydra). The configuration file is organized into **four core sections**:

1. **`time`** - Time driver configuration
2. **`exp`** - Experiment management settings
3. **`model`** - All model parameters
4. **`tracker`** - Data collection and tracking configuration

### Basic Configuration Structure

```yaml
defaults:
  - default
  - _self_

# 1. Time driver configuration
time:
  start: "2020-01-01"
  end: 100

# 2. Experiment management
exp:
  name: my_experiment
  repeats: 1
  seed: 42

# 3. Model parameters
model:
  density: 0.7
  n_agents: 50

# 4. Data tracking
tracker:
  model: {}
  agents: {}
  final: {}
```

## Table of Contents

- [1. Time Configuration](#1-time-configuration)
- [2. Experiment Configuration](#2-experiment-configuration)
- [3. Model Parameters](#3-model-parameters)
- [4. Tracker Configuration](#4-tracker-configuration)
- [Parameter Sweeps](#parameter-sweeps)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

---

## 1. Time Configuration

The `time` section configures the simulation time driver. It controls when the simulation starts, ends, and how time progresses.

### Time Schema

```yaml
time:
  # Start time (optional)
  start: str | datetime | null    # ISO format string or datetime, null = current time

  # End condition (required for auto-stop)
  end: int | str | datetime | null  # int = max ticks, str/datetime = end date, null = no auto-stop

  # Time step configuration (optional)
  days: int                        # Duration in days
  hours: int                       # Duration in hours
  minutes: int                     # Duration in minutes
  seconds: int                    # Duration in seconds

  # Advanced options
  irregular: bool                  # Enable irregular time mode (default: false)
```

### Examples

#### Simple: Maximum Steps

```yaml
time:
  end: 100  # Run for 100 steps
```

#### Calendar Time

```yaml
time:
  start: "2020-01-01"
  end: "2020-12-31"  # Run until end of year
```

#### Duration Mode

```yaml
time:
  start: "2020-01-01"
  days: 365  # Run for 365 days
```

#### Combined

```yaml
time:
  start: "2020-01-01"
  end: 200  # Or stop at 200 ticks, whichever comes first
  days: 1   # Each step = 1 day
```

### Time Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | str/datetime/null | Current time | Simulation start time (ISO format) |
| `end` | int/str/datetime/null | null | End condition: int=tick limit, str/datetime=end date |
| `days` | int | 0 | Time step duration in days |
| `hours` | int | 0 | Time step duration in hours |
| `minutes` | int | 0 | Time step duration in minutes |
| `seconds` | int | 0 | Time step duration in seconds |
| `irregular` | bool | false | Enable irregular time mode |

---

## 2. Experiment Configuration

The `exp` section configures batch experiment settings, including repetitions, output management, and random seeds.

### Experiment Schema

```yaml
exp:
  name: str                        # Experiment name
  outdir: str                      # Output directory
  repeats: int                     # Number of repetitions
  seed: int | null                 # Base random seed (null = no seed)
  logging: str | bool              # Logging mode: "once" | "always" | false
```

### Examples

#### Single Run

```yaml
exp:
  name: "single_run"
  outdir: "outputs"
  repeats: 1
  seed: 42
```

#### Batch Run with Repetitions

```yaml
exp:
  name: "batch_experiment"
  outdir: "outputs"
  repeats: 11  # Run 11 times with different seeds
  seed: 42     # Base seed for reproducibility
  logging: "once"  # Log only first repeat
```

### Experiment Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "ABSESpy" | Experiment name (used in output paths) |
| `outdir` | str | "out" | Output directory for results |
| `repeats` | int | 1 | Number of repetitions (each with different seed) |
| `seed` | int/null | null | Base random seed (null = no seeding) |
| `logging` | str/bool | "once" | Logging mode: "once", "always", or false |

---

## 3. Model Parameters

The `model` section contains **all model-specific parameters**. These can be accessed in your model code via `model.params` or `model.p`.

### Basic Model Parameters

```yaml
model:
  # Simple parameters
  name: "my_model"
  shape: [100, 100]
  density: 0.7
  n_agents: 50
```

### Nested Parameters

Organize parameters hierarchically for better structure:

```yaml
model:
  grid:
    width: 100
    height: 100
    torus: true
  agents:
    sheep:
      initial_count: 100
      reproduction_rate: 0.1
    wolves:
      initial_count: 20
      reproduction_rate: 0.05
  environment:
    temperature: 20.0
    humidity: 0.6
```

**Access in code:**
```python
width = model.params.grid.width
count = model.params.agents.sheep.initial_count
```

### Parameter Types

| Type | Example | Description |
|------|---------|-------------|
| `int` | `42` | Integer values |
| `float` | `3.14` | Floating-point numbers |
| `str` | `"hello"` | String values |
| `bool` | `true` | Boolean values |
| `list` | `[1, 2, 3]` | Lists/arrays |
| `dict` | `{key: value}` | Nested dictionaries |

### Parameter Ranges (for Sweeps)

Define parameter ranges for automated parameter sweeps:

```yaml
model:
  density:
    value: 0.7        # Default/single value
    min: 0.5          # Minimum for sweep
    max: 0.9          # Maximum for sweep
    step: 0.1         # Step size

  n_agents:
    value: 50
    min: 10
    max: 100
    step: 10
```

**Note:** When using parameter sweeps with Hydra, you'll use the sweeper syntax (see [Parameter Sweeps](#parameter-sweeps) section).

---

## 4. Tracker Configuration

The `tracker` section (formerly `reports`) defines what data to collect during simulation. It supports three types of tracking:

1. **Model trackers**: Collect model-level metrics at each step
2. **Agent trackers**: Collect agent-level attributes at each step
3. **Final trackers**: Collect metrics only at the end of simulation

### Tracker Schema

```yaml
tracker:
  # Model-level trackers (collected every step)
  model:
    metric_name: "attribute_name"  # Simple format
    # OR (future extension)
    metric_name:
      source: "attribute_name"
      alias: "custom_name"

  # Agent-level trackers (collected every step)
  agents:
    AgentBreedName:                 # Agent class name (exact match)
      attribute_name: "attribute_name"
      # OR (future extension)
      attribute_name:
        source: "attribute_name"
        alias: "custom_name"
        aggregate: "mean"           # Optional: mean, sum, count, min, max, std

  # Final trackers (collected only at end)
  final:
    final_metric: "method_name"
```

### Simple Format (Recommended)

The simplest and most common format uses a string that references an attribute or method name:

```yaml
tracker:
  model:
    n_sheep: "n_sheep"              # Collects model.n_sheep at each step
    n_wolves: "n_wolves"            # Collects model.n_wolves at each step
    population_ratio: "population_ratio"  # Collects model.population_ratio

  agents:
    Sheep:                          # Agent breed name (class name)
      energy: "energy"             # Collects agent.energy for all Sheep
      age: "age"                   # Collects agent.age for all Sheep
    Wolf:
      energy: "energy"
      hunger: "hunger"

  final:
    burned_rate: "burned_rate"     # Calls model.burned_rate() at end
    total_agents: "total_agents"
```

### Model Trackers

Model trackers collect data from the model instance at each simulation step.

**Requirements:**
- The referenced attribute/method must exist on your model class
- Methods should take no arguments (or only `self`)
- Should return a scalar value (int, float, bool, str)

**Example Model Class:**

```python
class MyModel(MainModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_sheep = 0
        self.n_wolves = 0

    @property
    def population_ratio(self) -> float:
        """Calculate sheep to wolf ratio."""
        if self.n_wolves == 0:
            return 0.0
        return self.n_sheep / self.n_wolves

    def total_population(self) -> int:
        """Get total population."""
        return self.n_sheep + self.n_wolves
```

**Corresponding Config:**

```yaml
tracker:
  model:
    n_sheep: "n_sheep"                    # Property access
    n_wolves: "n_wolves"                  # Property access
    population_ratio: "population_ratio"  # Property access
    total_population: "total_population"  # Method call
```

### Agent Trackers

Agent trackers collect data from agent instances at each step.

**Requirements:**
- The breed name must match the agent class name **exactly** (case-sensitive)
- The referenced attribute must exist on the agent class
- Attributes should be scalar values

**Example Agent Classes:**

```python
class Sheep(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy = 50
        self.age = 0

    @property
    def is_alive(self) -> bool:
        return self.energy > 0

class Wolf(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy = 100
        self.hunger = 0.0
```

**Corresponding Config:**

```yaml
tracker:
  agents:
    Sheep:                    # Must match class name exactly
      energy: "energy"
      age: "age"
      is_alive: "is_alive"     # Property access
    Wolf:
      energy: "energy"
      hunger: "hunger"
```

### Final Trackers

Final trackers are called once at the end of the simulation.

**Requirements:**
- Should be a method on the model class
- Method should take no arguments (or only `self`)
- Can return any type (will be stored as-is)

**Example:**

```python
class MyModel(MainModel):
    def burned_rate(self) -> float:
        """Calculate final burn rate."""
        burned = self.nature.select({"state": "burned"})
        total = len(self.nature.cells)
        return len(burned) / total if total > 0 else 0.0
```

**Corresponding Config:**

```yaml
tracker:
  final:
    burned_rate: "burned_rate"
```

### Common Tracker Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AttributeError: 'MyModel' has no attribute 'n_sheep'` | Attribute doesn't exist | Check attribute name spelling |
| `KeyError: 'Sheep'` | Agent breed name mismatch | Use exact class name (case-sensitive) |
| Empty DataFrame | No trackers defined | Add at least one tracker |
| `TypeError: 'str' object is not callable` | Tried to call a string | Use method name without quotes in code |

---

## Parameter Sweeps

ABSESpy supports parameter sweeps for automated batch experiments using Hydra's sweeper. You can define parameter ranges that Hydra will automatically expand into all combinations.

### Using Hydra Sweeper

Define parameter ranges in your config and use Hydra's sweeper syntax:

```yaml
# config.yaml
defaults:
  - default
  - _self_

# Base parameter values
model:
  density: 0.7
  n_agents: 50

# Hydra sweeper configuration
hydra:
  sweeper:
    params:
      model.density: "range(0.5, 0.9, 0.1)"      # 5 values: 0.5, 0.6, ..., 0.9
      model.n_agents: "range(10, 100, 10)"       # 10 values: 10, 20, ..., 100
      # Total: 5 × 10 = 50 combinations
```

**Run with:**
```bash
python main.py --multirun
```

### Range Syntax

```yaml
hydra:
  sweeper:
    params:
      # Integer range: range(start, stop, step)
      model.n_agents: "range(10, 100, 10)"

      # Float range: range(start, stop, step)
      model.density: "range(0.5, 0.9, 0.1)"

      # Discrete values: [value1, value2, ...]
      model.reproduction_rate: "[0.05, 0.1, 0.15, 0.2]"
```

### Multiple Parameter Combinations

Hydra generates all combinations automatically:

```yaml
hydra:
  sweeper:
    params:
      model.density: "range(0.5, 0.9, 0.1)"      # 5 values
      model.n_agents: "range(10, 100, 10)"       # 10 values
      model.reproduction_rate: "[0.05, 0.1, 0.2]" # 3 values
      # Total: 5 × 10 × 3 = 150 combinations
```

### Nested Parameter Sweeps

```yaml
model:
  agents:
    sheep:
      reproduction_rate: 0.1
      initial_energy: 50

hydra:
  sweeper:
    params:
      model.agents.sheep.reproduction_rate: "range(0.05, 0.2, 0.05)"
      model.agents.sheep.initial_energy: "range(30, 70, 10)"
```

### Accessing Swept Parameters in Code

When using parameter sweeps, access the actual value in your model:

```python
class MyModel(MainModel):
    def initialize(self):
        # Hydra will set the actual value for each run
        density = self.params.density  # Could be 0.5, 0.6, ..., 0.9
        n_agents = self.params.n_agents  # Could be 10, 20, ..., 100

        # Use in your model logic
        self.create_agents(n_agents, density)
```

---

## Complete Examples

### Example 1: Simple Model

```yaml
defaults:
  - default
  - _self_

# Time: Run for 100 steps
time:
  end: 100

# Experiment: Single run
exp:
  name: simple_model
  outdir: outputs
  repeats: 1

# Model: Basic parameters
model:
  name: "SimpleModel"
  shape: [50, 50]
  n_agents: 100

# Tracker: Basic data collection
tracker:
  model:
    n_agents: "n_agents"
    step_count: "time.tick"
  agents:
    Actor:
      unique_id: "unique_id"
  final:
    total_steps: "time.tick"
```

### Example 2: Parameter Sweep Experiment

```yaml
defaults:
  - default
  - _self_

# Time: Calendar time simulation
time:
  start: "2020-01-01"
  end: 365
  days: 1  # Each step = 1 day

# Experiment: Batch run with repetitions
exp:
  name: parameter_sweep
  outdir: outputs
  repeats: 5
  seed: 42

# Model: Parameters with ranges
model:
  density:
    value: 0.7
    min: 0.5
    max: 0.9
    step: 0.1
  n_agents:
    value: 50
    min: 20
    max: 100
    step: 20

# Tracker: Comprehensive tracking
tracker:
  model:
    density: "params.density"
    n_agents: "params.n_agents"
    population: "agents.count"
  final:
    final_population: "agents.count"

# Hydra sweeper configuration
hydra:
  sweeper:
    params:
      model.density: "range(0.5, 0.9, 0.1)"
      model.n_agents: "range(20, 100, 20)"
```

### Example 3: Complex Ecosystem Model

```yaml
defaults:
  - default
  - _self_

# Time: One year simulation
time:
  start: "2020-01-01"
  end: 365
  days: 1

# Experiment: Multiple repetitions
exp:
  name: ecosystem_simulation
  outdir: outputs
  repeats: 11
  seed: 42
  logging: "once"

# Model: Hierarchical parameters
model:
  grid:
    width: 100
    height: 100
    torus: true
  agents:
    sheep:
      initial_count: 100
      reproduction_rate: 0.1
      initial_energy: 50
    wolves:
      initial_count: 20
      reproduction_rate: 0.05
      initial_energy: 100
  environment:
    grass_growth_rate: 0.2
    initial_grass_coverage: 0.8

# Tracker: Multi-level tracking
tracker:
  model:
    n_sheep: "n_sheep"
    n_wolves: "n_wolves"
    grass_coverage: "grass_coverage"
    population_ratio: "population_ratio"
  agents:
    Sheep:
      energy: "energy"
      age: "age"
      is_alive: "is_alive"
    Wolf:
      energy: "energy"
      hunger: "hunger"
      is_alive: "is_alive"
  final:
    final_sheep_count: "n_sheep"
    final_wolf_count: "n_wolves"
    survival_rate: "calculate_survival_rate"
```

---

## Best Practices

### 1. Organize Parameters Hierarchically

```yaml
# ✅ Good: Organized by component
model:
  grid:
    width: 100
    height: 100
  agents:
    sheep: {...}
    wolves: {...}

# ❌ Bad: Flat structure
model:
  grid_width: 100
  grid_height: 100
  sheep_count: 100
  wolf_count: 20
```

### 2. Use Descriptive Names

```yaml
# ✅ Good: Clear names
tracker:
  model:
    sheep_population: "n_sheep"
    wolf_population: "n_wolves"

# ❌ Bad: Unclear names
tracker:
  model:
    s: "n_sheep"
    w: "n_wolves"
```

### 3. Match Agent Breed Names Exactly

```yaml
# ✅ Good: Exact class name match
tracker:
  agents:
    Sheep:  # Must match class name exactly
      energy: "energy"

# ❌ Bad: Name mismatch
tracker:
  agents:
    sheep:  # Wrong: lowercase
      energy: "energy"
```

### 4. Document Custom Parameters

```yaml
model:
  # Reproduction probability per step
  reproduction_rate: 0.1

  # Initial energy for new agents
  initial_energy: 50
```

### 5. Define Parameter Ranges for Future Sweeps

Even if not using sweeper immediately, define ranges:

```yaml
model:
  density:
    value: 0.7      # Current value
    min: 0.5       # For future sweeps
    max: 0.9
    step: 0.1
```

### 6. Keep Configurations Simple

Start with simple tracker format, upgrade to advanced format only when needed:

```yaml
# ✅ Good: Simple and clear
tracker:
  model:
    n_sheep: "n_sheep"

# ⚠️ Advanced: Only when needed
tracker:
  model:
    n_sheep:
      source: "n_sheep"
      alias: "sheep_count"
```

---

## Configuration Quick Reference

### Minimal Configuration

```yaml
defaults:
  - default
  - _self_

time:
  end: 100

exp:
  name: my_experiment

model: {}

tracker: {}
```

### Full Configuration Template

```yaml
defaults:
  - default
  - _self_

# Time driver
time:
  start: "2020-01-01"
  end: 365
  days: 1

# Experiment management
exp:
  name: my_experiment
  outdir: outputs
  repeats: 1
  seed: 42
  logging: "once"

# Model parameters
model:
  # Your parameters here
  param1: value1
  param2: value2

# Data tracking
tracker:
  model:
    metric1: "attribute1"
  agents:
    AgentBreed:
      attr1: "attr1"
  final:
    final_metric: "method_name"

# Parameter sweeps (optional)
hydra:
  sweeper:
    params:
      model.param1: "range(min, max, step)"
```

---

## Troubleshooting

### Configuration Not Loading

**Problem:** Config file not found or not loading.

**Solutions:**
- Check file path in `config_path`
- Ensure YAML syntax is correct (use a YAML validator)
- Check Hydra defaults list includes `default` and `_self_`

### Tracker Not Collecting Data

**Problem:** Empty DataFrames or missing columns.

**Solutions:**
- Verify attribute/method names match exactly (case-sensitive)
- Check that attributes exist on model/agent classes
- Ensure trackers are defined in `tracker` section
- Check logs for validation warnings

### Parameter Sweep Not Working

**Problem:** Sweeper not generating combinations.

**Solutions:**
- Verify Hydra sweeper configuration
- Check parameter range syntax: `range(min, max, step)`
- Ensure `--multirun` flag is used
- Check Hydra output directory for generated configs

### Agent Breed Name Not Found

**Problem:** `KeyError` when accessing agent trackers.

**Solutions:**
- Ensure breed name matches class name exactly (case-sensitive)
- Check that agents of that breed exist in the model
- Verify agent class is properly registered

---

## Migration from Old Schema

### From `reports` to `tracker`

The `reports` section has been renamed to `tracker` for clarity. The old name is still supported for backward compatibility but will be normalized automatically.

**Old (still works):**
```yaml
reports:
  model:
    n_sheep: "n_sheep"
```

**New (recommended):**
```yaml
tracker:
  model:
    n_sheep: "n_sheep"
```

### From `agent` to `agents`

The deprecated `agent` key is automatically normalized to `agents`.

**Old (still works):**
```yaml
tracker:
  agent:
    Actor:
      energy: "energy"
```

**New (recommended):**
```yaml
tracker:
  agents:
    Actor:
      energy: "energy"
```

---

## See Also

- [Getting Started Guide](get_started.md) - Basic usage
- [Parameter Management Tutorial](../tutorial/beginner/manage_parameters.ipynb) - Hands-on examples
- [Experiment API](../api/experiment.md) - Batch experiment details
- [Time Control API](../api/time.md) - Time driver details
- [Hydra Documentation](https://hydra.cc/docs/intro/) - Hydra framework reference
