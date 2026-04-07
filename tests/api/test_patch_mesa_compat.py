#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Regression tests for PatchModule vs mesa-geo raster initialization order."""

from __future__ import annotations

import numpy as np
import pytest

from abses.core.model import MainModel
from abses.space.mesa_raster_compat import maybe_sync_cell_xy
from abses.space.patch import PatchModule


def test_create_patch_module_no_recursion(model: MainModel) -> None:
    """Creating a grid must complete without RecursionError (mesa-geo 0.9.3+)."""
    module = model.nature.create_module(shape=(4, 4), resolution=1.0)
    assert isinstance(module, PatchModule)
    assert module.array_cells.shape == (4, 4)
    assert len(module.cells) == 4


def test_update_transform_after_init_is_safe(model: MainModel) -> None:
    """Transform updates after cells exist must remain safe."""
    module = model.nature.create_module(shape=(2, 3), resolution=1.0)
    module._update_transform()
    module._update_transform()
    assert module.transform is not None


def test_maybe_sync_cell_xy_skips_without_cells() -> None:
    """Helper must not fail when ``_cells`` is absent or sync is undefined."""

    class _NoSync:
        pass

    layer = _NoSync()
    maybe_sync_cell_xy(layer)

    layer.__dict__["_cells"] = None
    maybe_sync_cell_xy(layer)


@pytest.mark.parametrize("shape", [(1, 1), (5, 7)])
def test_create_module_various_shapes(model: MainModel, shape: tuple[int, int]) -> None:
    """Smoke test multiple raster dimensions."""
    module = model.nature.create_module(shape=shape, resolution=1.0)
    assert module.width == shape[1]
    assert module.height == shape[0]
    module.apply_raster(np.ones(module.shape3d), attr_name="ones")
    assert module.get_raster("ones").sum() == shape[0] * shape[1]
