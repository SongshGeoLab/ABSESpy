#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Wolf-Sheep Predation Model demonstrating ABSESpy's agent-based modeling capabilities.

This example showcases:
- Actor lifecycle management (birth, death, reproduction)
- Agent movement and spatial interactions
- Inter-agent interactions (predation)
- Cell-agent interactions (grazing)
- Energy-based dynamics
"""

from abses import Actor, MainModel, PatchCell, raster_attribute


class Grass(PatchCell):
    """
    Grass cell that can be eaten and regrows after a countdown.

    Attributes:
        _empty: Whether the grass has been eaten.
        _countdown: Ticks remaining until grass regrows (starts at 5).

    ABSESpy Features Used:
        - PatchCell: Base class for spatial cells
        - @raster_attribute: Enables extraction of 'empty' state as raster data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._empty = False
        self._countdown = 5

    def grow(self) -> None:
        """
        Regrow grass after countdown reaches zero.

        If the cell is empty, counts down each tick. When countdown
        reaches 0, grass regrows and countdown resets to 5.
        """
        # countdown on brown patches: if you reach 0, grow some grass
        if self._empty is True:
            if self._countdown <= 0:
                self._empty = False
                self._countdown = 5
            else:
                self._countdown -= 1

    @raster_attribute
    def empty(self) -> bool:
        """
        Return whether the cell is empty (grass eaten).

        The @raster_attribute decorator enables extraction of this property
        as spatial raster data via module.get_raster('empty').

        Returns:
            True if grass has been eaten, False if grass is present.
        """
        return self._empty


class Animal(Actor):
    """
    Base class for animals with energy-based lifecycle.

    Attributes:
        energy: Current energy level (starts at 5).

    ABSESpy Features Used:
        - Actor: Base class for autonomous agents
        - die(): Lifecycle management (automatic cleanup)
        - at.agents.new(): Create offspring at current location
        - random: Integrated random number generator
    """

    def __init__(self, *args, **kwargs):
        Actor.__init__(self, *args, **kwargs)
        self.energy = 5

    def update(self) -> None:
        """
        Update the animal's state each tick.

        Consumes 1 energy per tick. If energy drops to or below 0,
        the animal dies (automatically removed from simulation).
        """
        # consume energy
        self.energy -= 1
        if self.energy <= 0:
            self.die()

    def reproduce(self) -> None:
        """
        Reproduce with probability-based on rep_rate parameter.

        If reproduction occurs, energy is split in half and a new
        offspring of the same class is created at the current location.

        ABSESpy Feature: at.agents.new() creates agent at current cell.
        """
        rep_rate = self.model.params.get("rep_rate", 0.05)
        if self.random.random() < rep_rate:
            self.energy //= 2
            self.at.agents.new(self.__class__)


class Wolf(Animal):
    """
    Wolf agent that hunts sheep for energy.

    ABSESpy Features Demonstrated:
        - move.random(): Random movement to neighboring cells
        - at.agents.select(): Filter agents by type
        - random.choice(): Select random agent from filtered set
        - die(): Remove agent from simulation
    """

    def step(self) -> None:
        """
        Execute one time step for the wolf.

        Sequence: move → hunt → reproduce → consume energy.
        """
        self.move.random()
        self.eat_sheep()
        self.reproduce()
        self.update()

    def eat_sheep(self) -> None:
        """
        Hunt and eat a sheep if present in the current cell.

        Gains 2 energy when successfully catching a sheep.

        ABSESpy Features:
            - at.agents.select(agent_type=Sheep): Filter agents by type
            - random.choice(when_empty="return None"): Handle empty results
            - die(): Automatic cleanup of eaten sheep
        """
        sheep = self.at.agents.select(agent_type=Sheep)
        if a_sheep := sheep.random.choice(when_empty="return None"):
            a_sheep.die()
            self.energy += 2


class Sheep(Animal):
    """
    Sheep agent that grazes on grass for energy.

    ABSESpy Features Demonstrated:
        - move.random(): Random movement to neighboring cells
        - at: Access to current cell location
        - Cell property access: Reading and modifying cell state
    """

    def step(self) -> None:
        """
        Execute one time step for the sheep.

        Sequence: move → graze → reproduce → consume energy.
        """
        self.move.random()
        self.eat_grass()
        self.reproduce()
        self.update()

    def eat_grass(self) -> None:
        """
        Graze on grass if present in the current cell.

        Gains 2 energy when successfully eating grass. Marks the cell
        as empty after grazing.

        ABSESpy Feature: at provides direct access to current cell and its properties.
        """
        cell = self.at
        if cell is not None and cell.empty is False:
            self.energy += 2
            cell._empty = True


class WolfSheepModel(MainModel):
    """
    Wolf-Sheep predation model simulating ecosystem dynamics.

    Classic predator-prey ABM demonstrating population dynamics,
    energy-based lifecycle, and spatial interactions.

    ABSESpy Features Demonstrated:
        - MainModel: Base class for simulation models
        - nature.create_module(): Create spatial grid
        - agents.new(): Batch create agents
        - move.to(): Place agents on grid
        - agents.has(): Count agents by type
        - Automatic agent scheduling and lifecycle management
    """

    def setup(self) -> None:
        """
        Initialize the grassland grid and populate with agents.

        Creates a spatial grid with Grass cells, then adds wolves and sheep
        at random locations.
        """
        # Initialize a grid with custom Grass cells
        grassland = self.nature.create_module(
            shape=self.params.shape,
            name="grassland",
            cell_cls=Grass,
        )
        # Create initial populations using batch creation
        self.agents.new(Wolf, self.params.n_wolves)
        self.agents.new(Sheep, self.params.n_sheep)
        # Place agents at random locations on the grassland
        # ABSESpy Feature: move.to() with "random" placement
        for agent in self.agents:
            agent.move.to("random", layer=grassland)

    def step(self) -> None:
        """
        Execute one time step of the simulation.

        Updates grass growth state and checks termination conditions.
        Agent steps are automatically scheduled by ABSESpy.
        """
        # Apply grow to all grass cells
        for cell in self.nature.array_cells.flatten():
            cell.grow()
        self.check_end()

    def check_end(self) -> None:
        """
        Check and enforce termination conditions.

        Model stops if:
        - All sheep die (wolves win)
        - All wolves die (sheep win)
        - Sheep population exceeds 400 (overpopulation)

        ABSESpy Feature: agents.has() counts agents by type.
        """
        # end model
        if not self.agents.has(Sheep):
            self.running = False
        elif not self.agents.has(Wolf):
            self.running = False
        elif self.agents.has(Sheep) >= 400:
            self.running = False
