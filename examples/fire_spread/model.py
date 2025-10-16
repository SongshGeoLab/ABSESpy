#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Forest fire spread model demonstrating ABSESpy's spatial modeling capabilities.

This example showcases:
- PatchCell state management
- Spatial diffusion through neighbor interaction
- Raster attribute extraction
- Batch operations with ActorsList
"""

from typing import Optional

import hydra
import numpy as np
from matplotlib import pyplot as plt
from omegaconf import DictConfig

from abses import Experiment, MainModel, PatchCell, raster_attribute
from abses.agents.sequences import ActorsList


class Tree(PatchCell):
    """
    Tree cell with four distinct states.

    States:
        0: Empty (no tree).
        1: Intact tree.
        2: Burning.
        3: Scorched (burned, cannot burn again).

    ABSESpy Features Used:
        - PatchCell: Base class for spatial cells
        - @raster_attribute: Decorator to extract state as raster data
        - neighboring(): Get adjacent cells
        - select(): Filter cells by attributes
        - trigger(): Batch method invocation
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = 0

    def step(self) -> None:
        """
        Execute one time step for this tree cell.

        If burning, ignites neighboring intact trees using Von Neumann neighborhood.
        Then transitions to scorched state.
        """
        if self._state == 2:
            neighbors = self.neighboring(moore=False, radius=1)
            # apply to all neighboring patches: trigger ignite method
            neighbors.select({"state": 1}).trigger("ignite")
            # after then, it becomes scorched and cannot be burned again.
            self._state = 3

    def grow(self) -> None:
        """Grow a tree on this cell (state transitions to 1)."""
        self._state = 1

    def ignite(self) -> None:
        """Ignite this tree if intact (state transitions from 1 to 2)."""
        if self._state == 1:
            self._state = 2

    @raster_attribute
    def state(self) -> int:
        """
        Return the current state code.

        The @raster_attribute decorator enables extraction of this property
        as spatial raster data via module.get_raster('state').
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

    def setup(self) -> None:
        """
        Initialize the forest grid and set initial conditions.

        Creates a spatial grid with Tree cells, randomly distributes trees
        according to density parameter, and ignites leftmost column.
        """
        # Create spatial grid using nature subsystem
        grid = self.nature.create_module(
            name="forest",
            shape=self.params.shape,
            cell_cls=Tree,
            major_layer=True,
        )
        # Randomly select cells for tree placement
        all_cells = ActorsList(self, grid.array_cells.flatten())
        chosen_patches = all_cells.random.choice(
            size=self.num_trees, replace=False, as_list=True
        )
        # Grow trees on selected patches using trigger for batch operation
        ActorsList(self, chosen_patches).trigger("grow")
        # Ignite leftmost column trees using ActorsList
        ActorsList(self, grid.array_cells[:, 0]).trigger("ignite")

    def step(self) -> None:
        """
        Execute one time step of the simulation.

        Iterates through all cells and executes their step method.
        """
        for tree in self.nature.array_cells.flatten():
            tree.step()

    @property
    def burned_rate(self) -> float:
        """
        Calculate the proportion of burned trees.

        Returns:
            Ratio of scorched trees (state=3) to total trees.
        """
        state = self.nature.get_raster("state")
        burned_count = np.squeeze(state == 3).sum()
        return float(burned_count) / self.num_trees if self.num_trees > 0 else 0.0

    @property
    def num_trees(self) -> int:
        """
        Calculate total number of trees based on density parameter.

        Returns:
            Integer number of trees (grid_size * density).
        """
        shape = self.params.shape
        return int(shape[0] * shape[1] * self.params.density)

    def plot_state(self) -> None:
        """
        Visualize the current state of all trees.

        Uses get_xarray() to extract spatial data with coordinates,
        displaying empty (black), intact (green), burning (orange),
        and scorched (red) cells.
        """
        categories = {
            0: "black",  # Empty
            1: "green",  # Intact
            2: "orange",  # Burning
            3: "red",  # Scorched
        }
        cmap = plt.cm.colors.ListedColormap([categories[i] for i in sorted(categories)])
        data = self.nature.get_xarray("state")
        data.plot(cmap=cmap)
        plt.show()


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
