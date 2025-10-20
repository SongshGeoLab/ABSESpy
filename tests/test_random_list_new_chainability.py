#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Tests for ListRandom semantics (choice/new) to ensure return types and chainability.
"""

from typing import TYPE_CHECKING

import numpy as np
import pytest
from omegaconf import DictConfig

from abses import MainModel
from abses.agents import Actor
from abses.space import BaseNature, PatchModule

if TYPE_CHECKING:
    pass


class _DummyActor(Actor):
    def setup(self) -> None:
        self.size = 1


class _Nature(BaseNature):
    def initialize(self) -> None:
        # Minimal layer with a fixed shape for cell creation
        # Use constructor parameters of PatchModule to define raster
        self.create_module(
            name="cells", module_cls=PatchModule, shape=(2, 2), resolution=1
        )


def _build_model() -> MainModel:
    cfg = DictConfig({"model": {"name": "random-tests"}})
    # MainModel.__init__ already drives DEFAULT_INIT_ORDER via do_each("_initialize")
    # and subsystems handle their own initialize(). So we just return the model.
    return MainModel(parameters=cfg, nature_class=_Nature)


def test_choice_as_list_true_returns_python_list() -> None:
    """choice(as_list=True) must return a Python list to match existing API."""
    model = _build_model()
    cells = model.nature.major_layer.cells_lst  # type: ignore[attr-defined]
    selected = cells.random.choice(size=2, replace=False, as_list=True)
    assert isinstance(selected, list)
    assert len(selected) == 2


def test_choice_as_list_false_returns_actorslist() -> None:
    """choice(as_list=False) should return ActorsList for multiple selection."""
    model = _build_model()
    cells = model.nature.major_layer.cells_lst  # type: ignore[attr-defined]
    selected = cells.random.choice(size=2, replace=False, as_list=False)
    # must support .apply, indicating ActorsList
    _ = selected.apply(lambda c: c)  # type: ignore[attr-defined]


def test_random_new_returns_actorslist_and_chainable_apply() -> None:
    """random.new(...) should return an ActorsList and support .apply chaining."""
    model = _build_model()
    cells = model.nature.major_layer.cells_lst  # type: ignore[attr-defined]
    actors = cells.random.new(_DummyActor, size=2, replace=False)
    # must support apply
    sizes = actors.apply(lambda a: a.size)  # numpy array
    assert isinstance(sizes, np.ndarray)
    assert sizes.shape[0] == 2


def test_random_new_respects_replace_flag() -> None:
    model = _build_model()
    cells = model.nature.major_layer.cells_lst  # type: ignore[attr-defined]
    with pytest.raises(Exception):
        _ = cells.random.new(_DummyActor, size=10, replace=False)
