# Wolf-Sheep Predation Model

A classic predator-prey Agent-Based Model that **demonstrates ABSESpy's agent modeling capabilities**.

## Model Overview

This model simulates dynamic interactions between wolves, sheep, and grass:
- **Sheep** eat grass for energy, consume energy, and reproduce
- **Wolves** eat sheep for energy, consume energy, and reproduce
- **Grass** regrows after a delay when eaten

## 🎯 Core ABSESpy Features Demonstrated

This example showcases the following ABSESpy-specific features:

| Feature | Description | Code Location |
|---------|-------------|---------------|
| **Actor** | Autonomous agent base class with lifecycle management | `Animal(Actor)` |
| **die()** | Automatic cleanup and removal of agents | `agent.die()` |
| **move.random()** | Random movement to neighbor cells | `self.move.random()` |
| **move.to()** | Move to specified location | `agent.move.to("random", layer)` |
| **at** | Access agent's current cell | `self.at` |
| **at.agents.new()** | Create new agent on cell | `self.at.agents.new(Class)` |
| **at.agents.select()** | Filter agents in cell | `self.at.agents.select(agent_type=Sheep)` |
| **random.choice()** | Random selection from list | `agents.random.choice(when_empty=...)` |
| **agents.new()** | Batch create agents | `self.agents.new(Wolf, num)` |
| **agents.has()** | Count agents by type | `self.agents.has(Sheep)` |
| **Auto-scheduling** | Agents automatically execute step() | No manual scheduling needed |

## Running the Model

```bash
# Method 1: Direct run (simple demo)
python model.py

# Method 2: Run as module
python -m examples.wolf_sheep.model
```

## Key Features Explained

### 1. **Actor + Lifecycle**: Automatic Agent Management

```python
class Animal(Actor):  # ✨ ABSESpy: Agent base class
    """Energy-driven agent"""

    def update(self):
        self.energy -= 1
        if self.energy <= 0:
            self.die()  # ✨ ABSESpy: Automatic cleanup

    def reproduce(self):
        # ✨ ABSESpy: Create offspring at current location
        self.at.agents.new(self.__class__)
```

**Why is this special?**
- `Actor`: Built-in location, movement, perception capabilities
- `die()`: Automatically removes from model, cell, and visualization
- `at.agents.new()`: Create new agent directly at current location
- No manual list management for adding/removing agents

---

### 2. **move System**: Declarative Movement

```python
class Wolf(Animal):
    def step(self):
        # ✨ ABSESpy: Random movement
        self.move.random()

# Random placement during initialization
# ✨ ABSESpy: move.to() flexible placement
agent.move.to("random", layer=grassland)
```

**Why is this special?**
- `move.random()`: Automatically moves to random neighbor cell
- `move.to("random")`: String parameter, no coordinate calculation needed
- `move.to(cell)`: Also supports direct cell object
- Automatically handles boundaries, position updates, triggers events

---

### 3. **at + agents.select()**: Agent Interactions

```python
class Wolf(Animal):
    def eat_sheep(self):
        # ✨ ABSESpy: Access current cell
        # ✨ ABSESpy: Filter agents by type
        sheep = self.at.agents.select(agent_type=Sheep)

        # ✨ ABSESpy: Random selection + empty handling
        if a_sheep := sheep.random.choice(when_empty="return None"):
            a_sheep.die()  # ✨ ABSESpy: Automatic cleanup
            self.energy += 2
```

**Why is this special?**
- `at`: Single property access to current cell and all related info
- `agents.select(agent_type=Class)`: Type filtering without lambda
- `random.choice(when_empty=...)`: Elegant empty list handling
- `die()`: One-line complete cleanup

---

### 4. **agents.new() + agents.has()**: Batch Management

```python
def setup(self):
    # ✨ ABSESpy: Batch creation
    self.agents.new(Wolf, self.params.n_wolves)  # Create 50 wolves
    self.agents.new(Sheep, self.params.n_sheep)  # Create 100 sheep

def check_end(self):
    # ✨ ABSESpy: Count by type
    if not self.agents.has(Sheep):  # Sheep extinct?
        self.running = False
    elif self.agents.has(Sheep) >= 400:  # Too many sheep?
        self.running = False
```

**Why is this special?**
- `agents.new(Class, num)`: Batch creation, returns list
- `agents.has(Class)`: Count by type, no manual counting needed
- Automatically assigns unique IDs, registers with scheduler
- Supports singleton pattern: `agents.new(Class, singleton=True)`

---

### 5. **Auto-scheduling**: No Manual Loops

```python
class WolfSheepModel(MainModel):
    def step(self):
        # Only handle environment updates
        for cell in self.nature.array_cells.flatten():
            cell.grow()
        # ✨ ABSESpy: Agents automatically execute step()
        # No need to manually call wolf.step(), sheep.step()
```

**Why is this special?**
- ABSESpy automatically schedules all agents' `step()` methods
- Executes in creation order (customizable)
- Dead agents automatically skipped
- Newly created agents join next round

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| shape | Grid size (height, width) | (50, 50) |
| n_wolves | Initial wolf population | 50 |
| n_sheep | Initial sheep population | 100 |
| rep_rate | Reproduction probability | 0.04 |

## Testing

```bash
# Run all wolf_sheep model tests
pytest tests/examples/test_sheep_wolf.py -v

# Test coverage:
# - Grass cell functionality (3 tests)
# - Animal base class (4 tests)
# - Wolf-specific behavior (1 test)
# - Sheep-specific behavior (1 test)
# - Complete model (6 tests)
```

## 🎓 Learning Points

### ABSESpy vs Pure Mesa/NetLogo

| Feature | ABSESpy | Pure Mesa | NetLogo |
|---------|---------|-----------|---------|
| **Create Agents** | `agents.new(Wolf, 50)` | Manual loop + add | `create-wolves 50` |
| **Movement** | `agent.move.random()` | Manual neighbor calc + move | `move-to one-of neighbors` |
| **Location Access** | `agent.at` | Manual grid query | `patch-here` |
| **Create on Cell** | `cell.agents.new(Class)` | Manual position setting | `hatch` |
| **Filter by Type** | `agents.select(agent_type=Sheep)` | `[a for a in ... if isinstance()]` | `sheep-here` |
| **Count** | `agents.has(Sheep)` | Manual count | `count sheep` |
| **Lifecycle** | `agent.die()` auto cleanup | Manual remove + cleanup | `die` |

### Key Advantages

1. **Declarative Movement**: `move.random()` cleaner than manual neighbor calculation
2. **Automatic Lifecycle**: `die()` handles all cleanup work
3. **Type-safe Filtering**: `select(agent_type=Class)` clearer than isinstance loops
4. **Location Awareness**: `at` property provides unified access to cell and agents
5. **Batch Operations**: `agents.new()` supports batch creation

### Model Dynamics

1. **Energy Management**: Each animal has energy, movement and actions consume energy
2. **Predation**: Wolves eat sheep, sheep eat grass
3. **Reproduction**: Probabilistic reproduction when energy sufficient
4. **Termination**: Model stops when one species goes extinct or sheep overpopulate

## Extension Ideas

Try experimenting with:
- Add grass regrowth rate parameter
- Implement different predator types
- Add spatial heterogeneity (varying grass growth rates)
- Collect and analyze population dynamics data

## Related Files

- `model.py`: Model implementation
- `tests/examples/test_sheep_wolf.py`: Complete test suite (15 tests)

---

*This model demonstrates ABSESpy's simplicity and power in classic ABM implementation.*

