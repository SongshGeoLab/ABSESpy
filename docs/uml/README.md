# ABSESpy UML Documentation

This directory contains comprehensive UML documentation for the ABSESpy library, including class diagrams and sequence diagrams for all major modules and user scenarios.

## 📁 Directory Structure

```
docs/uml/
├── README.md                           # This file
├── core_architecture_class_diagram.md   # Core system architecture
├── agents/
│   ├── class_diagram.md                # Agents module class diagram
│   └── sequence_diagrams.md            # Agents module sequence diagrams
├── space/
│   ├── class_diagram.md                # Space module class diagram
│   └── sequence_diagrams.md            # Space module sequence diagrams
├── human/
│   └── class_diagram.md                # Human module class diagram
├── utils/
│   └── class_diagram.md                # Utils module class diagram
├── core/
│   └── sequence_diagrams.md            # Core module sequence diagrams
├── user_scenarios.md                   # User scenario sequence diagrams
└── internal_flows.md                    # Internal system flow diagrams
```

## 🏗️ Architecture Overview

ABSESpy follows a modular architecture with the following main components:

### Core Components
- **MainModel**: Central orchestrator managing all subsystems
- **BaseNature**: Spatial subsystem managing raster layers and cells
- **BaseHuman**: Human subsystem managing human actors and collections
- **TimeDriver**: Time management and progression
- **DataCollector**: Data collection and storage

### Agent System
- **Actor**: Base class for all agents
- **ActorsList**: Collection of agents with batch operations
- **Container Classes**: Manage agents at model and cell levels

### Spatial System
- **PatchModule**: Individual raster layers
- **PatchCell**: Spatial units that can host agents
- **Raster Attributes**: Dynamic attributes linked to raster data

### Human System
- **BaseHuman**: Human system management
- **Human Collections**: Groups of human actors
- **Social Networks**: Relationships between human actors

### Utilities
- **Data Collection**: Model and agent data collection
- **Time Management**: Simulation time progression
- **Configuration**: Parameter management
- **Logging**: System logging and debugging

## 📊 Class Diagrams

### 1. Core Architecture
**File**: `core_architecture_class_diagram.md`
- Shows relationships between MainModel, BaseNature, BaseHuman, Actor, PatchCell
- Illustrates the overall system architecture
- Key design patterns: Observer, Factory, Container

### 2. Agents Module
**File**: `agents/class_diagram.md`
- Shows Actor, ActorsList, and container classes
- Illustrates agent management and batch operations
- Key design patterns: Container, Strategy, Decorator

### 3. Space Module
**File**: `space/class_diagram.md`
- Shows PatchCell, PatchModule, BaseNature
- Illustrates spatial operations and raster attributes
- Key design patterns: Module, Cell, Raster

### 4. Human Module
**File**: `human/class_diagram.md`
- Shows BaseHuman, HumanModule, and human collections
- Illustrates human decision-making and social networks
- Key design patterns: Collection, Network, Decision

### 5. Utils Module
**File**: `utils/class_diagram.md`
- Shows utility classes for data collection, time management, logging
- Illustrates system utilities and error handling
- Key design patterns: Utility, Manager, Handler

## 🔄 Sequence Diagrams

### 1. Core Module Sequences
**File**: `core/sequence_diagrams.md`
- Model initialization sequence
- Model step execution sequence
- Data collection sequence
- Model run sequence
- Error handling sequence

### 2. Agents Module Sequences
**File**: `agents/sequence_diagrams.md`
- Agent creation sequence
- Agent selection sequence
- Batch operations sequence
- Agent movement sequence
- Agent death sequence
- Chainable operations sequence

### 3. Space Module Sequences
**File**: `space/sequence_diagrams.md`
- Spatial module creation sequence
- Raster application sequence
- Cell agent interaction sequence
- Raster attribute access sequence
- Spatial query sequence
- Cell attribute update sequence

### 4. User Scenarios
**File**: `user_scenarios.md`
- Creating a simple model
- Adding agents to the model
- Running a simulation
- Data collection and analysis
- Spatial operations
- Agent interactions

### 5. Internal Flows
**File**: `internal_flows.md`
- Module lifecycle management
- State management
- Observer pattern implementation
- Random number generation
- Error handling and recovery
- Data flow and caching

## 🎯 Key Design Patterns

### 1. Observer Pattern
- Actors observe model state changes
- Notifications are sent to all registered observers
- Enables loose coupling between components

### 2. Factory Pattern
- ModuleFactory creates PatchModule instances
- Agent containers create actor instances
- Provides flexible object creation

### 3. Container Pattern
- Various containers manage collections
- _ModelAgentsContainer manages all model agents
- _CellAgentsContainer manages cell-specific agents

### 4. Strategy Pattern
- Different selection strategies for ActorsList
- Configurable decision-making in human system
- Flexible behavior patterns

### 5. Decorator Pattern
- @raster_attribute for dynamic cell attributes
- @alive_required for agent method validation
- @with_axes for spatial method enhancement

## 🔧 Usage Examples

### Basic Model Creation
```python
# Create model
model = MainModel()

# Add agents
farmers = model.agents.new(Farmer, num=10)

# Create spatial module
nature = model.nature
dem_module = nature.create_module("dem", shape=(100, 100))

# Run simulation
model.run_model()
```

### Agent Operations
```python
# Select and filter agents
active_farmers = (model.agents
                  .select(lambda a: a.energy > 0)
                  .select(lambda a: a.pos is not None))

# Batch operations
farmers.shuffle_do("work")
farmers.apply(lambda a: a.collect_resources())

# Random selection
random_farmer = farmers.random_choice()
```

### Spatial Operations
```python
# Create spatial module
nature = model.nature
land_module = nature.create_module("land", shape=(50, 50))

# Apply raster data
elevation_raster = xr.open_dataarray("elevation.tif")
land_module.apply_raster(elevation_raster)

# Access cells
cell = land_module.get_cell((25, 25))
neighbors = cell.neighbors(radius=2)
```

### Data Collection
```python
# Set up data collection
collector = model.datacollector
collector.add_model_reporter("population", lambda m: len(m.agents))

# Collect data during simulation
collector.collect(model)

# Extract results
model_data = collector.get_model_vars_dataframe()
agent_data = collector.get_agent_vars_dataframe()
```

## 📈 System Interactions

### Model Lifecycle
1. **Initialization**: Model and subsystems are created
2. **Setup**: All components are initialized
3. **Execution**: Model runs through time steps
4. **Data Collection**: Data is gathered during execution
5. **Analysis**: Results are extracted and analyzed

### Agent Lifecycle
1. **Creation**: Agents are created through containers
2. **Placement**: Agents are placed on spatial cells
3. **Interaction**: Agents interact with environment and other agents
4. **Movement**: Agents can move between cells
5. **Death**: Agents can die and be removed from the system

### Spatial Operations
1. **Module Creation**: Spatial modules are created
2. **Raster Application**: Raster data is applied to modules
3. **Cell Access**: Individual cells are accessed
4. **Attribute Access**: Cell attributes are accessed
5. **Spatial Queries**: Neighbor and distance queries are performed

## 🚀 Getting Started

1. **Read Core Architecture**: Start with `core_architecture_class_diagram.md`
2. **Understand Modules**: Review module-specific class diagrams
3. **Learn Sequences**: Study sequence diagrams for key operations
4. **Explore Scenarios**: Review user scenarios for common use cases
5. **Understand Flows**: Study internal flows for system behavior

## 📚 Additional Resources

- [ABSESpy Documentation](https://absespy.readthedocs.io/)
- [GitHub Repository](https://github.com/SongshGeo/ABSESpy)
- [Tutorials](https://absespy.readthedocs.io/en/latest/tutorial/)
- [API Reference](https://absespy.readthedocs.io/en/latest/api/)

## 🤝 Contributing

When contributing to ABSESpy:
1. Update relevant UML diagrams
2. Ensure diagrams reflect actual code changes
3. Add new sequence diagrams for new features
4. Update this README if structure changes

## 📝 Notes

- All diagrams use Mermaid syntax for GitHub compatibility
- Diagrams are kept up-to-date with code changes
- Sequence diagrams show both happy path and error scenarios
- Class diagrams include key methods and relationships
- User scenarios focus on common use cases
- Internal flows show system-level processes