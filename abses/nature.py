#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import List, Optional, Tuple, Union

import numpy as np
from agentpy.grid import AgentSet

from abses.actor import Actor
from abses.boundary import Boundaries

from .algorithms.spatial import points_to_polygons, polygon_to_mask
from .container import AgentsContainer
from .factory import PatchFactory
from .modules import CompositeModule
from .patch import Patch, get_buffer
from .sequences import ActorsList, Selection
from .tools.func import norm_choice

DEFAULT_WORLD = {
    "width": 9,
    "height": 9,
    "resolution": 10,
    # 'units': 'm',
}


class PositionSet(AgentSet):
    def __init__(self, model, index, accessible, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self._index: Tuple[int, int] = index
        self._accessible: bool = accessible

    @property
    def index(self):
        return self._index

    @property
    def accessible(self):
        return self._accessible

    def add(self, actor: Actor):
        if self._accessible is False:
            raise KeyError(f"{self.index} is not accessible.")
        else:
            super().add(actor)


class BaseNature(CompositeModule, PatchFactory):
    def __init__(self, model, name="nature", **kwargs):
        CompositeModule.__init__(self, model, name=name)
        PatchFactory.__init__(self, model=model, **kwargs)
        self._boundary: Boundaries = None
        self._grid: np.ndarray = None

    # @property
    # def patches(self):
    #     return tuple(self._patches.keys())

    def __getitem__(self, key: Union[Tuple[int, int], slice]) -> ActorsList:
        items = self.grid[key]
        if isinstance(items, AgentSet):
            return ActorsList(self.model, items)
        else:
            return self._aggregate_agents(items)

    @property
    def boundary(self) -> Boundaries:
        return self._boundary

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def _aggregate_agents(self, items: np.ndarray) -> ActorsList:
        """Aggregating searched `PositionSet`s into an `ActorsList`."""
        agents = ActorsList(self.model)
        for item in items.flatten():
            agents.extend(item)
        return agents

    def _setup_grid(self, shape: Tuple[int, int]):
        """A numpy 2-d Grid where agents are saved in."""
        array = np.empty(shape=shape, dtype=object)
        it = np.nditer(array, flags=["refs_ok", "multi_index"])
        for _ in it:
            index = it.multi_index
            access = self.accessible[index]
            array[index] = PositionSet(
                model=self.model, accessible=access, index=index
            )
        self._grid = array

    def _after_parsing(self):
        """After parsing parameters, setup grid and geographic settings."""
        settings = self.params.get("world", DEFAULT_WORLD).copy()
        self.geo.auto_setup(settings=settings)
        boundary_settings = self.params.get("boundary", {})
        self._boundary = Boundaries(shape=self.geo.shape, **boundary_settings)
        self._setup_grid(shape=self.geo.shape)

    # def send_patch(self, attr: str, **kwargs) -> Patch:
    #     if hasattr(self, attr):
    #         obj = getattr(self, attr)
    #         return obj
    #     elif attr in self.patches:
    #         module = self._patches[attr]
    #         obj = module.get_patch(attr, **kwargs)
    #         return obj
    #     else:
    #         raise ValueError(f"Unknown patch {attr}.")

    # def transfer_var(self, sender: object, var: str) -> None:
    #     if var not in self.patches:
    #         self._patches[var] = sender
    #     else:
    #         module = self._patches[var]
    #         if sender is module:
    #             self.logger.warning(
    #                 f"Transfer exists {var} of {module}, please use 'update' function to do so."
    #             )
    #         self.logger.error(
    #             f"{sender} wants to transfer an exists var '{var}', which was created by {module}!"
    #         )

    # def transfer_update(
    #     self, sender: object, patch_name: str, **kwargs
    # ) -> None:
    #     # update a patch
    #     if patch_name in self.patches:
    #         owner = self._patches[patch_name]
    #         getattr(owner, patch_name).update(**kwargs)
    #         self.logger.debug(
    #             f"{sender} requires {patch_name} of {owner} to update."
    #         )

    def random_positions(
        self,
        k: int,
        where: np.ndarray = None,
        probabilities: np.ndarray = None,
        only_empty: bool = False,
        replace: bool = False,
    ) -> List[Tuple[int, int]]:
        """
        Choose 'k' patches in the world randomly.

        Args:
            k (int): number of patches to choose.
            mask (np.ndarray, optional): bool mask, only True patches can be choose. If None, all patches are accessible. Defaults to None.
            replace (bool, optional): If a patch can be chosen more than once. Defaults to False.

        Returns:
            List[Tuple[int, int]]: iterable coordinates of chosen patches.
        """
        if where is None:
            where = self.accessible
        else:
            where = self.accessible & where
        if only_empty is True:
            where = where & ~self.has_agent().astype(bool)
        where = self.create_patch(where, "where")
        potential_pos = [(x, y) for x, y in where.arr.where()]
        if probabilities is not None:
            probabilities = probabilities[where]
        pos_index = norm_choice(
            np.arange(len(potential_pos)),
            size=k,
            p=probabilities,
            replace=replace,
        )
        positions = [potential_pos[i] for i in pos_index]
        return positions

    # def random_move(
    #     self,
    #     agent,
    #     only_empty: bool = True,
    #     avoid_breed: str = None,
    #     only_accessible: bool = True,
    # ):
    #     mask = self.create_patch(True, "mask")
    #     if only_accessible:
    #         mask = mask | self.accessible
    #     if only_empty:
    #         mask = mask | ~self.has_agent(avoid_breed)
    #     pos = self.random_positions(1, mask)[0]
    #     self.move_to(agent, pos)

    def add_agents(
        self,
        agents: ActorsList,
        positions=None,
    ):
        if positions is None:
            positions = self.random_positions(len(agents))
        for agent, pos in zip(agents, positions):
            agent.settle_down(position=pos)
            self.grid[pos].add(agent)
        # msg = f"Randomly placed {len(agents)} '{agents.breed()}' in nature."
        # self.mediator.transfer_event(self, msg)

    def land_allotment(
        self, agents: ActorsList, where: np.ndarray = None
    ) -> AgentsContainer:
        """
        > For each cell in the grid, find the nearest agent and assign that agent's id to the cell

        :param mask: a boolean array that indicates which cells should be assigned an owner
        :return: The pattern of the agents.
        """
        where = self.geo.wrap_data(where, masked=True)
        points = agents.array("pos")
        polygons = points_to_polygons(points)
        for i, agent in enumerate(agents):
            owned_land = polygon_to_mask(polygons[i], shape=self.shape)
            owned_land = owned_land & where
            agent.attach_places(name="owned", place=owned_land)

    def lookup_agents(
        self, where: np.ndarray, selection: Optional[Selection] = None
    ) -> ActorsList:
        """
        Search agents.

        Args:
            where (np.ndarray): bool mask, when a cell is False, ignore agents here.
            selection (Optional[Selection], optional): filter results after search. see `ActorsList.select()` for more information. Defaults to None, meaning that no further selection, just returns the actual agents distribution.

        Returns:
            ActorsList: all qualified agents.
        """
        where = self.geo.wrap_data(where, masked=True)
        where_bool = where.to_numpy().astype(bool)
        agents = self._aggregate_agents(self.grid[where_bool])
        if selection is None:
            return agents
        else:
            return agents.select(selection)

    def find_neighbors(
        self,
        pos: Tuple[int, int],
        distance: int = 0,
        neighbors: int = 4,
        selection: Optional[Selection] = None,
    ) -> ActorsList:
        """
        Find all agents nearby with a given position and distance.

        Args:
            pos (Tuple[int, int]): a specific position in the world.
            distance (int, optional): distances to search. Defaults to 0.
            neighbors (int, optional): neighbor rule. Defaults to 4.
            breed (str, optional): filter results after search. see `ActorsList.select()` for more information. Defaults to None, meaning that no further selection, just returns the actual agents distribution.

        Returns:
            ActorsList: all qualified agents.
        """
        position = self.geo.zeros()
        position[pos] = True
        buffer = get_buffer(buffer=distance, neighbors=neighbors)
        return self.lookup_agents(buffer, selection=selection)

    def has_agent(self, selection: Optional[Selection] = None) -> Patch:
        """
        How many qualified agents are available in each cell.

        Args:
            selection (Optional[Selection], optional): selection, see `ActorsList.select()` for more information. Defaults to None, meaning that no further selection, just returns the actual agents distribution.

        Returns:
            Patch[int]: number of qualified agents in each cell.
        """

        def counts_agent(agents, selection):
            agents = ActorsList(self.model, agents)
            if selection is not None:
                return len(agents.select(selection))
            else:
                return len(agents)

        has_agents = np.vectorize(counts_agent)(self.grid, selection)
        patch = self.create_patch(has_agents, "has_agent", True)
        return patch
