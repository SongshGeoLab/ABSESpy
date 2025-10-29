#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/
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

import numpy as np

from abses import Actor, MainModel, PatchModule


class SchellingAgent(Actor):
    """
    Agent in Schelling segregation model.

    Each agent has a type (0 or 1) and prefers to live near
    similar neighbors. If the fraction of similar neighbors
    falls below the homophily threshold, the agent moves.

    Attributes:
        type: Agent type identifier (0=majority, 1=minority).
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Create a new Schelling agent.

        Args:
            model: The Schelling model instance.
        """
        super().__init__(*args, **kwargs)
        prob = self.p.minority_prob
        self.type = 1.0 if self.random.random() < prob else 0.0

    @property
    def is_happy(self) -> bool:
        """Check if agent is happy based on similar neighbors."""
        homophily = self.model.params.get("homophily", 0.3)

        # Get neighboring cells
        neighbors = self.at.neighboring(moore=True)

        # Get agents on neighboring cells
        neighbor_agents = neighbors.linked_agents

        if len(neighbor_agents) == 0:
            return True  # No neighbors, consider happy

        # Count similar neighbors
        similarity = neighbor_agents.array("type") == self.type
        similarity_ratio = similarity.sum() / len(similarity)
        return similarity_ratio >= homophily

    def move_to_empty(self) -> None:
        """Move agent to a random empty cell on the entire grid."""
        # Get all empty cells on the grid
        empty_cells = self.model.nature.grid.cells_lst.select({"is_empty": True})

        if len(empty_cells) > 0:
            self.move.to(empty_cells.random.choice())

    def step(self) -> None:
        """
        Execute one time step: move if unhappy.

        If the agent is not happy based on its neighbors,
        it moves to a random empty cell on the grid.
        """
        if not self.is_happy:
            self.move_to_empty()


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

    def initialize(self) -> None:
        """
        Initialize grid and create agents.

        ABSESpy Feature: initialize() is called automatically by MainModel.__init__.
        """
        # Initialize grid (Mesa component, compatible with ABSESpy)
        height = int(self.params.get("height", 20))
        width = int(self.params.get("width", 20))
        grid: PatchModule = self.nature.create_module(
            name="grid",
            shape=[height, width],
            major_layer=True,
        )
        expected_n_agents = int(height * width * self.params.get("density", 0.7))
        cells = grid.cells_lst.random.choice(size=expected_n_agents)
        cells.apply(lambda a: a.agents.new(SchellingAgent))

    def step(self) -> None:
        """
        Execute one time step of the model.

        Activates all agents in random order, allowing them to
        evaluate their happiness and potentially move. Continues
        until all agents are happy.

        ABSESpy Feature: agents.shuffle_do() provides randomized
        activation order without manual shuffling.
        """
        # Activate all agents in random order
        self.agents.shuffle_do("step")
        # Collect data
        self.datacollector.collect(self)
        # Stop if everyone is happy
        if self.agents.array("is_happy").all():
            self.running = False

    def show_type(self) -> np.ndarray:
        """Show the type of the agents as float array (empty -> NaN)."""
        return self.nature.grid.apply_agents(attr="type", default=np.nan, dtype="numpy")

    @property
    def happy_ratio(self) -> float:
        """Calculate the ratio of happy agents."""
        return self.agents.array("is_happy").sum() / len(self.agents)
