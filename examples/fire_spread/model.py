#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Forest fire spread model demonstrating ABSESpy's spatial modeling capabilities.

This example showcases:
- PatchCell tree_state management
- Spatial diffusion through neighbor interaction
- Raster attribute extraction
- Batch operations with ActorsList
"""

from enum import IntEnum
from typing import Optional

import hydra
from omegaconf import DictConfig

from abses import Experiment, MainModel, PatchCell, raster_attribute


class Tree(PatchCell):
    """
    Tree cell with four distinct states.

    ABSESpy Features Used:
        - PatchCell: Base class for spatial cells
        - @raster_attribute: Decorator to extract tree_state as raster data
        - neighboring(): Get adjacent cells
        - select(): Filter cells by attributes
        - trigger(): Batch method invocation
    """

    class State(IntEnum):
        """Tree cell states."""

        EMPTY = 0
        INTACT = 1
        BURNING = 2
        SCORCHED = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = self.State.EMPTY

    def step(self) -> None:
        """
        Execute one time step for this tree cell.

        If burning, ignites neighboring intact trees using Von Neumann neighborhood.
        Then transitions to scorched tree_state.
        """
        if self._state == self.State.BURNING:
            neighbors = self.neighboring(moore=False, radius=1)
            # Apply to all neighboring patches: trigger ignite method
            neighbors.select({"tree_state": self.State.INTACT}).shuffle_do("ignite")
            # After then, it becomes scorched and cannot be burned again.
            self._state = self.State.SCORCHED

    def grow(self) -> None:
        """Grow a tree on this cell (tree_state transitions to INTACT)."""
        self._state = self.State.INTACT

    def ignite(self) -> None:
        """Ignite this tree if intact (tree_state transitions from INTACT to BURNING)."""
        if self._state == self.State.INTACT:
            self._state = self.State.BURNING

    @property
    def state(self) -> int:
        """Get the current state value."""
        return int(self._state)

    @raster_attribute
    def tree_state(self) -> int:
        """
        Return the current tree_state code.

        The @raster_attribute decorator enables extraction of this property
        as spatial raster data via module.get_raster('tree_state').
        """
        return self._state


class Forest(MainModel):
    """
    Forest fire spread simulation model.

    Simulates wildfire propagation through a grid of trees using
    cellular automaton dynamics.

    ABSESpy Features Demonstrated:
        - MainModel: Base class for simulation models
        - PatchModule: Spatial grid management
        - ActorsList: Batch operations on cells
        - Hydra integration: Configuration management
        - Experiment: Batch runs and parameter sweeps
    """

    def initialize(self) -> None:
        # Create spatial grid using nature subsystem
        self.nature.create_module(
            name="forest",
            shape=self.params.shape,
            cell_cls=Tree,
            major_layer=True,
        )
        # Randomly select cells for tree placement
        chosen_patches = self.nature.forest.random.choice(
            size=self.num_trees, replace=False
        )
        # Grow trees on selected patches
        chosen_patches.shuffle_do("grow")

    def setup(self) -> None:
        """
        Initialize the forest grid and set initial conditions.

        Creates a spatial grid with Tree cells, randomly distributes trees
        according to density parameter, and ignites leftmost column.
        """
        # Ignite leftmost column trees (automatically returns ActorsList)
        self.nature.forest[:, 0].shuffle_do("ignite")

    def step(self) -> None:
        """
        Execute one time step of the simulation.

        Executes step method on all cells using batch operation.
        """
        self.nature.cells_lst.shuffle_do("step")

    @property
    def burned_rate(self) -> float:
        """
        Calculate the proportion of burned trees.

        Returns:
            Ratio of scorched trees to total trees.
        """
        # Select all cells with SCORCHED tree_state
        burned_trees = self.nature.select({"tree_state": Tree.State.SCORCHED})
        # Calculate the proportion
        return len(burned_trees) / self.num_trees if self.num_trees > 0 else 0.0

    @property
    def num_trees(self) -> int:
        """
        Calculate total number of trees based on density parameter.

        Returns:
            Integer number of trees (grid_size * density).
        """
        shape = self.params.shape
        return int(shape[0] * shape[1] * self.params.density)


@hydra.main(version_base=None, config_path="", config_name="config")
def main(cfg: Optional[DictConfig] = None) -> None:
    """
    Main entry point for running the forest fire model.

    Uses Hydra for configuration management and Experiment for batch runs.
    Configuration is loaded from config.yaml in the same directory.

    Args:
        cfg: Hydra configuration object (loaded from config.yaml).
    """
    exp = Experiment(Forest, cfg=cfg)
    exp.batch_run()


if __name__ == "__main__":
    main()
