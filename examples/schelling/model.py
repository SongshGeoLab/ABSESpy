"""
Schelling Segregation Model demonstrating ABSESpy's ABM capabilities.

Classic model showing how mild individual preferences can lead to
significant macro-level segregation patterns.

This example showcases:
- MainModel as simulation framework
- Mesa grid integration for spatial structure
- Data collection and reporting
- Agent scheduling with shuffle_do()
- Termination conditions based on agent states
"""

from typing import Optional

from mesa.datacollection import DataCollector
from mesa.space import SingleGrid

from abses import MainModel

from .agents import SchellingAgent


class Schelling(MainModel):
    """
    Schelling segregation model implementation.

    Demonstrates how individual preferences for similar neighbors
    can lead to large-scale segregation, even when individuals
    would be happy with diverse neighborhoods.

    ABSESpy Features Demonstrated:
        - MainModel: Simulation framework with built-in agent management
        - agents.shuffle_do(): Random activation of agents
        - random: Integrated random number generator
        - p (params): Convenient parameter access
        - Mesa integration: Compatible with Mesa's grid and datacollection
    """

    def __init__(self, seed: Optional[int] = None, **kwargs) -> None:
        """
        Create a new Schelling segregation model.

        Args:
            seed: Random seed for reproducibility.
            **kwargs: Additional parameters including:
                - width: Grid width
                - height: Grid height
                - density: Initial cell occupation probability (0-1)
                - minority_pc: Probability of being minority type (0-1)
                - homophily: Minimum fraction of similar neighbors for happiness (0-1)
                - radius: Neighborhood search radius

        ABSESpy Feature: Parameters accessible via self.p
        """
        super().__init__(seed=seed, **kwargs)
        height, width = int(self.p.height), int(self.p.width)

        # Initialize grid (Mesa component, compatible with ABSESpy)
        self.grid = SingleGrid(width, height, torus=True)

        # Track happiness metric
        self.happy = 0

        # Set up data collection (Mesa DataCollector)
        self.datacollector = DataCollector(
            model_reporters={
                "happy": "happy",
                "pct_happy": lambda m: (m.happy / len(m.agents)) * 100
                if len(m.agents) > 0
                else 0,
                "population": lambda m: len(m.agents),
                "minority_pct": lambda m: (
                    sum(1 for agent in m.agents if agent.type == 1)
                    / len(m.agents)
                    * 100
                    if len(m.agents) > 0
                    else 0
                ),
            },
            agent_reporters={"agent_type": "type"},
        )

        # Create agents and place them on the grid
        # ABSESpy Feature: self.random for consistent random number generation
        for _, pos in self.grid.coord_iter():
            if self.random.random() < self.p.density:
                agent_type = 1 if self.random.random() < self.p.minority_pc else 0
                agent = SchellingAgent(self, agent_type)
                self.grid.place_agent(agent, pos)

        # Collect initial state
        self.datacollector.collect(self)

    def step(self) -> None:
        """
        Execute one time step of the model.

        Activates all agents in random order, allowing them to
        evaluate their happiness and potentially move. Continues
        until all agents are happy.

        ABSESpy Feature: agents.shuffle_do() provides randomized
        activation order without manual shuffling.
        """
        self.happy = 0  # Reset counter of happy agents
        # ABSESpy Feature: shuffle_do activates agents in random order
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)  # Collect data
        # Termination condition: stop when everyone is happy
        self.running = self.happy < len(self.agents)
