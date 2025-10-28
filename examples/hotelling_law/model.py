#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# @GitHub   : https://github.com/SongshGeo
# @Website: https://cv.songshgeo.com/

"""
Hotelling's Law model implemented in an idiomatic ABSESpy style.

This example uses ABSESpy primitives for:
- Spatial cells as customers (`PatchCell`)
- Mobile shops as agents (`Actor`)
- Batch operations via `ActorsList`
- Minimal loops with vectorized distance computation

Key ideas:
- Each customer (cell) links to its preferred shop (nearest + cheapest)
- Shops adapt price and position to maximize their service area
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from abses import Actor, ActorsList, MainModel, PatchCell


class Customer(PatchCell):
    """Customer cell.

    Each `Customer` occupies exactly one spatial cell. Preference is represented
    as a link to the chosen `Shop` (link name: "prefer").
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._prefer_idx: int = -1

    def find_preference(self) -> None:
        """Find and link to preferred shop using ABSESpy batch helpers.

        - Collect shop positions/prices via ActorsList.evaluate/array
        - Vectorize distance computation; pick argmin
        - Record internal prefer index for later rasterization
        """
        shops: ActorsList[Actor] = self.model.actors
        if len(shops) == 0:
            self._prefer_idx = -1
            self.link.clean()
            return

        # Positions/prices as numpy arrays
        positions = shops.apply(lambda s: s.at.indices).astype(float)  # (n,2)
        prices = shops.apply(lambda s: s.price).astype(float)  # (n,)

        deltas = positions - np.asarray(self.indices, dtype=float)
        distances = np.sqrt((deltas**2).sum(axis=1))  # (n,)
        scores = distances + prices

        prefer_idx = int(np.argmin(scores))
        self._prefer_idx = prefer_idx

        # Update link
        self.link.clean()
        self.link.by(shops[prefer_idx], link_name="prefer")


class Shop(Actor):
    """Shop agent that adapts price and position."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.price: float = 10.0
        self.next_position: Optional[PatchCell] = None
        self.next_price: Optional[float] = None

    @property
    def area_count(self) -> int:
        """Number of customers preferring this shop."""
        return len(self.link.get("prefer", direction="out"))

    def step(self) -> None:
        self.adjust_price()
        self.adjust_position()

    def advance(self) -> None:
        self.affect_price()
        self.affect_position()

    def adjust_price(self) -> None:
        init_price: float = float(self.price)
        candidate_prices = np.asarray(
            [init_price - 1.0, init_price, init_price + 1.0], dtype=float
        )
        # One-liner: choose best price candidate with automatic rollback of price
        best_price = self.evaluate(
            candidate_prices,
            lambda actor, p: (
                setattr(actor, "price", float(p))
                or actor.model.recalculate_preferences()
                or float(actor.area_count) * float(actor.price)
            ),
            dtype=float,
            how="max",
            preserve_attrs=("price",),
        )
        self.next_price = (
            (init_price - 1.0) if best_price is None else float(best_price)
        )

    def adjust_position(self) -> None:
        cell_now: PatchCell = self.at
        candidates: ActorsList[PatchCell] = self.at.neighboring(
            moore=True, include_center=False
        )
        if len(candidates) == 0:
            self.next_position = cell_now
            return
        # One-liner: choose best move candidate with automatic rollback of position
        self.next_position = self.evaluate(
            candidates,
            lambda actor, cell: (
                actor.move.to(cell)
                or actor.model.recalculate_preferences()
                or int(actor.area_count)
            ),
            dtype=int,
            how="max",
            preserve_position=True,
        )


class Hotelling(MainModel):
    """Hotelling's Law model class using ABSESpy primitives."""

    def setup(self) -> None:
        num_agents: int = int(self.params.get("n_agents", 3))
        layer = self.nature.create_module(
            cell_cls=Customer,
            name="market",
            shape=(10, 10),
        )
        shops: ActorsList[Shop] = self.agents.new(Shop, num_agents)
        shops.apply(lambda shop: shop.move.to("random", layer=layer))

    def step(self) -> None:
        self.recalculate_preferences()
        self.agents.shuffle_do("step")

    def advance(self) -> None:
        self.agents.shuffle_do("advance")

    def recalculate_preferences(self) -> None:
        """Batch-recalculate preferences and expose a raster for visualization."""
        # Batch trigger preference update on all customers
        self.nature.select().trigger("find_preference")
        # Expose prefer index as raster attribute via apply
        prefer_idx_raster = self.nature.apply(lambda c: getattr(c, "_prefer_idx", -1))
        self.nature.apply_raster(prefer_idx_raster, attr_name="prefer_idx")
