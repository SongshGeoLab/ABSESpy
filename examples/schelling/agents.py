"""
Schelling Segregation Agent demonstrating ABSESpy's Mesa integration.

This module showcases:
- Mesa Agent compatibility with ABSESpy MainModel
- Neighbor similarity calculation
- Conditional movement based on satisfaction
- Integration with Mesa's spatial grid

Note: This uses Mesa's native Agent class to demonstrate
that ABSESpy MainModel is fully compatible with Mesa components.
"""

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:
    from .model import Schelling


class SchellingAgent(Agent):
    """
    Agent in Schelling segregation model.

    Each agent has a type (0 or 1) and prefers to live near
    similar neighbors. If the fraction of similar neighbors
    falls below the homophily threshold, the agent moves.

    Attributes:
        type: Agent type identifier (0=majority, 1=minority).

    Note: Uses Mesa's native Agent class to demonstrate
    ABSESpy MainModel's compatibility with Mesa components.
    """

    def __init__(self, model: "Schelling", agent_type: int) -> None:
        """
        Create a new Schelling agent.

        Args:
            model: The Schelling model instance.
            agent_type: Type indicator (0=majority, 1=minority).
        """
        super().__init__(model)
        self.type = agent_type

    def step(self) -> None:
        """
        Execute one time step: check happiness and move if necessary.

        Calculates the fraction of similar neighbors within the
        specified radius. If below the homophily threshold, moves
        to a random empty cell.

        Uses Mesa's grid.get_neighbors() and grid.move_to_empty().
        """
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.p.radius
        )

        # Count similar neighbors
        similar_neighbors = len([n for n in neighbors if n.type == self.type])

        # Calculate the fraction of similar neighbors
        if (valid_neighbors := len(neighbors)) > 0:
            similarity_fraction = similar_neighbors / valid_neighbors
        else:
            # If there are no neighbors, the similarity fraction is 0
            similarity_fraction = 0.0

        # Move if unhappy
        if similarity_fraction < self.model.p.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1
