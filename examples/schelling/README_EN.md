# Schelling Segregation Model

A classic social segregation Agent-Based Model that **demonstrates ABSESpy's seamless Mesa integration**.

## Model Overview

The Schelling segregation model shows how even mild individual preferences can lead to significant macro-level segregation:
- Agents come in two types (blue and orange)
- Each agent wants at least a certain fraction of similar neighbors
- Unsatisfied agents move to empty cells
- Results in highly segregated spatial patterns

**Key Insight**: Even when individuals only require 40% similar neighbors (accepting 60% different), the outcome is still highly segregated communities.

## 🎯 Core ABSESpy Features Demonstrated

This example showcases the following ABSESpy-specific features:

| Feature | Description | Code Location |
|---------|-------------|---------------|
| **MainModel** | Simulation framework base class with built-in agent management | `Schelling(MainModel)` |
| **Mesa Agent Compatibility** | Directly uses Mesa's Agent class | `SchellingAgent(Agent)` |
| **agents.shuffle_do()** | Random-order agent activation | `self.agents.shuffle_do("step")` |
| **self.random** | Unified random number generator | `self.random.random()` |
| **self.p** | Convenient parameter access | `self.p.height`, `self.p.homophily` |
| **Mesa Grid Integration** | Directly uses Mesa's Grid system | `SingleGrid`, `grid.place_agent()` |
| **Mesa DataCollector** | Uses Mesa's data collection | `DataCollector` |
| **Auto-scheduling** | Built-in agent scheduling mechanism | No manual management needed |

## Dependencies

**Important**: This example requires additional Mesa dependencies (not mandatory for ABSESpy core):

```bash
# Install with pip
pip install mesa solara

# Or use poetry (recommended)
poetry install
```

## Running the Model

### Interactive Visualization

```bash
# 1. Ensure dependencies are installed
pip install mesa solara

# 2. Launch Solara visualization interface
cd examples/schelling
solara run app.py

# 3. Open in browser: http://127.0.0.1:8765/
```

**Note**: If you encounter Solara environment issues (e.g., `KeyError: 'load_extensions'`), you can:
1. Try reinstalling: `pip install --upgrade solara jupyter`
2. Or use the programmatic run method below

### Programmatic Run

**Method 1: Use provided script**

```bash
cd examples/schelling
python run_simple.py
```

This script runs the model and prints detailed progress information.

**Method 2: Custom code**

```python
from examples.schelling.model import Schelling

# Create model (ABSESpy parameter format)
params = {
    "model": {
        "width": 20,
        "height": 20,
        "density": 0.8,
        "minority_pc": 0.5,
        "homophily": 0.4,  # 40% similar neighbors needed
        "radius": 1
    }
}
model = Schelling(parameters=params, seed=42)

# Run until convergence
step = 0
while model.running and step < 100:
    model.step()
    step += 1
    if step % 10 == 0:
        pct = model.happy / len(model.agents) * 100
        print(f"Step {step}: {model.happy}/{len(model.agents)} happy ({pct:.1f}%)")

print(f"✓ Converged after {step} steps")
print(f"✓ Final: {model.happy}/{len(model.agents)} happy")
```

## Key Features Explained

### 1. **MainModel + agents.shuffle_do()**: Agent Scheduling

```python
class Schelling(MainModel):  # ✨ ABSESpy: Simulation framework
    def step(self):
        self.happy = 0
        # ✨ ABSESpy: Random-order agent activation
        self.agents.shuffle_do("step")
        # Termination: stop when all agents are happy
        self.running = self.happy < len(self.agents)
```

**Why is this special?**
- `agents.shuffle_do("step")`: Automatically activates all agents in random order
- No manual: `random.shuffle(agents); for a in agents: a.step()`
- Built-in scheduler: Automatically manages agent order
- One line implements random activation pattern

---

### 2. **self.random**: Unified Random Number Generation

```python
def __init__(self, seed=None, **kwargs):
    super().__init__(seed=seed, **kwargs)

    # ✨ ABSESpy: Unified random number generator
    for _, pos in self.grid.coord_iter():
        if self.random.random() < self.p.density:
            agent_type = 1 if self.random.random() < self.p.minority_pc else 0
```

**Why is this special?**
- `self.random`: Shared RNG across all components
- Seed control: Set once, works globally
- Reproducibility: Same seed produces same results
- No manual random object passing

---

### 3. **self.p**: Convenient Parameter Access

```python
class Schelling(MainModel):
    def __init__(self, seed=None, **kwargs):
        super().__init__(seed=seed, **kwargs)
        # ✨ ABSESpy: Parameters automatically stored in self.p
        height, width = int(self.p.height), int(self.p.width)

class SchellingAgent(Actor):
    def step(self):
        # ✨ ABSESpy: Agents can also access model parameters
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.p.radius
        )
```

**Why is this special?**
- `self.p.*`: Unified parameter access interface
- Auto-storage: kwargs automatically converted to p object
- Type-safe: Supports nested parameters and defaults
- Agent access: `model.p.homophily`

---

### 4. **Mesa Integration**: Best Compatibility

```python
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from abses import MainModel, Actor

class Schelling(MainModel):  # ✨ ABSESpy: MainModel base class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ✨ Seamless Mesa component integration
        self.grid = SingleGrid(width, height, torus=True)
        self.datacollector = DataCollector(...)
```

**Why is this special?**
- **Full Mesa compatibility**: Grid, Space, DataCollector work seamlessly
- **Inherits Mesa.Model**: ABSESpy's MainModel extends Mesa.Model
- **Mix and match**: Use ABSESpy features + Mesa components
- **Gradual migration**: Existing Mesa models can adopt ABSESpy incrementally

---

### 5. **Mesa Agent Compatibility**: Fully Interoperable

```python
from mesa import Agent  # Directly use Mesa's Agent

class SchellingAgent(Agent):
    """Uses Mesa's native Agent class"""

    def __init__(self, model, agent_type: int):
        super().__init__(model)  # Mesa Agent initialization
        self.type = agent_type

# ABSESpy MainModel can directly manage Mesa Agents
model.agents.shuffle_do("step")  # ✨ ABSESpy feature works with Mesa Agent
```

**Why is this special?**
- **Full Compatibility**: ABSESpy MainModel directly manages Mesa Agents
- **No Modification**: Existing Mesa Agent code works without changes
- **Mix and Match**: Can use Mesa Agent and ABSESpy Actor in same model
- **Gradual Upgrade**: Start with MainModel enhancements, optionally upgrade to Actor later

## Configuration Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| width | Grid width | 20 | >0 |
| height | Grid height | 20 | >0 |
| density | Initial occupation density | 0.8 | 0-1 |
| minority_pc | Minority group fraction | 0.5 | 0-1 |
| homophily | Required similar neighbor fraction | 0.4 | 0-1 |
| radius | Neighbor search radius | 1 | ≥1 |

## Testing

```bash
# Run all Schelling model tests
pytest tests/examples/test_schelling.py -v

# Test coverage:
# - SchellingAgent (2 tests)
# - Schelling model (6 tests)
```

**Test Results**: ✅ 8/8 all passed

## 🎓 Learning Points

### ABSESpy MainModel vs Pure Mesa Model

| Feature | ABSESpy MainModel + Mesa Agent | Pure Mesa Model + Agent |
|---------|--------------------------------|------------------------|
| **Random Activation** | `agents.shuffle_do("step")` | `random.shuffle(agents); for a in agents: a.step()` |
| **Parameter Access** | `self.p.height` | `self.height` (manual storage) |
| **Random Numbers** | `self.random` (unified) | Manual random object passing |
| **Agent Types** | Mesa `Agent` or ABSESpy `Actor` | Mesa `Agent` |
| **Grid/Space** | ✅ Fully compatible with Mesa | ✅ Native |
| **DataCollector** | ✅ Fully compatible | ✅ Native |

### Key Advantages

1. **shuffle_do()**: One line implements random activation (works with Mesa Agents!)
2. **Unified RNG**: Seed controls all random behavior
3. **Parameter Management**: self.p provides unified access
4. **Full Mesa Compatibility**: Directly use Mesa's Agent, Grid, DataCollector
5. **Gradual Migration**: Just change `mesa.Model` to `abses.MainModel` for enhancements
6. **Mix and Match**: Same model can contain both Mesa Agents and ABSESpy Actors

### Model Dynamics

- **Micro Preferences**: Individuals only need 40% similar neighbors
- **Macro Result**: Produces near 100% homogeneous communities
- **Self-Organization**: No central control, only individual decisions
- **Emergence**: Collective behavior can't be simply summed from individuals

## Related Files

- `model.py`: Schelling model class
- `agents.py`: SchellingAgent agent class
- `app.py`: Solara visualization interface
- `analysis.ipynb`: Parameter sweep and analysis examples
- `tests/examples/test_schelling.py`: Complete test suite

## Extension Ideas

Try experimenting with:
- Add a third agent type
- Implement different neighbor definitions (Manhattan distance)
- Add movement costs (limit movement frequency)
- Collect time-series data on segregation degree
- Parameter sweep: homophily vs final segregation

## Theoretical Background

Based on:

**Original Paper**:
[Schelling, Thomas C. "Dynamic Models of Segregation." Journal of Mathematical Sociology, 1971.](https://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf)

**Interactive Demo**:
[Parable of the Polygons](http://ncase.me/polygons/) by Vi Hart and Nicky Case

---

*This model demonstrates how ABSESpy seamlessly integrates with the Mesa ecosystem, retaining Mesa's powerful features while adding convenient enhancements.*

