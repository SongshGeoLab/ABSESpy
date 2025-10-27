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

import matplotlib.pyplot as plt

from abses import Actor, MainModel, PatchCell, alive_required, raster_attribute


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
        self.energy = 50  # Start with much more energy to survive until finding food

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

    @alive_required
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

        Gains 5 energy when successfully catching a sheep (higher reward).

        ABSESpy Features:
            - at.agents.select(): Filter agents in current cell
            - random.choice(): Select random agent from list
            - die(): Automatic cleanup of eaten sheep
        """
        sheep = self.at.agents.select(agent_type=Sheep)
        if a_sheep := sheep.random.choice(when_empty="return None"):
            a_sheep.die()
            self.energy += 10  # Much higher energy reward to sustain wolves


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

        Gains 3 energy when successfully eating grass. Marks the cell
        as empty after grazing.

        ABSESpy Features:
            - at: Direct access to current cell
            - Cell property access: Direct read/modify of cell state
        """
        if not self.on_earth or self.at is None:
            return
        if not self.at.empty:
            self.energy += 3  # Higher energy reward
            self.at._empty = True


class WolfSheepModel(MainModel):
    """
    Wolf-Sheep predation model simulating ecosystem dynamics.

    Classic predator-prey ABM demonstrating population dynamics,
    energy-based lifecycle, and spatial interactions.

    ABSESpy Features Demonstrated:
        - MainModel: Base class for simulation models
        - nature.create_module(): Create spatial grid
        - agents.new(): Batch create agents
        - agents.move.to(): Batch place agents
        - agents.has(): Count agents by type
        - cells_lst.shuffle_do(): Batch operations on cells
        - nature.select(): Filter cells by attributes
        - Dynamic plotting API: module.attr.plot()
        - Automatic agent scheduling and lifecycle management
    """

    def initialize(self) -> None:
        """
        Initialize the grassland grid.

        Creates spatial grid with Grass cells.
        """
        # Initialize a grid with custom Grass cells
        self.nature.create_module(
            shape=self.params.shape,
            name="grassland",
            cell_cls=Grass,
            major_layer=True,
        )
        # Create initial populations using batch creation
        self.agents.new(Wolf, self.params.n_wolves)
        self.agents.new(Sheep, self.params.n_sheep)
        # Place all agents at random locations using batch operation
        # shuffle_do accepts method name and kwargs
        self.agents.shuffle_do("move_to", to="random", layer=self.nature.grassland)

    def step(self) -> None:
        """
        Execute one time step of the simulation.

        Updates grass growth state and checks termination conditions.
        Agent steps are scheduled here.
        """
        # Apply grow to all grass cells using batch operation
        self.nature.grassland.cells_lst.shuffle_do("grow")
        # Schedule agent steps
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
        self.check_end()

    @property
    def n_sheep(self) -> int:
        """Get current number of sheep."""
        return self.agents.has(Sheep)

    @property
    def n_wolves(self) -> int:
        """Get current number of wolves."""
        return self.agents.has(Wolf)

    @property
    def grass_coverage(self) -> float:
        """
        Calculate proportion of cells with grass.

        Returns:
            Proportion between 0.0 and 1.0.
        """
        grassland = self.nature.grassland
        if grassland is None:
            return 0.0

        total = len(grassland.cells_lst)
        if total == 0:
            return 0.0
        empty_count = len(grassland.select({"empty": True}))
        return (total - empty_count) / total

    def check_end(self) -> None:
        """
        Check and enforce termination conditions.

        Model stops if:
        - All sheep die (wolves win)
        - All wolves die (sheep win)
        - Sheep population exceeds 400 (overpopulation)

        ABSESpy Feature: agents.has() counts agents by type.
        """
        if not self.agents.has(Sheep) or not self.agents.has(Wolf):
            self.running = False
        elif self.agents.has(Sheep) >= 400:
            self.running = False

    @property
    def population_ratio(self) -> float:
        """
        Calculate the ratio of sheep to total population.

        Returns:
            Float between 0.0 and 1.0.
        """
        total = self.n_sheep + self.n_wolves
        return self.n_sheep / total if total > 0 else 0.0

    def plot_state(self) -> None:
        """
        Plot the current ecosystem state.

        Shows grass coverage and agent positions.
        """
        # Plot grass coverage
        color_map = {False: "green", True: "brown"}

        # Use dynamic plotting API
        self.nature.empty.plot(cmap=color_map, title="Grass Coverage")
        plt.show()
