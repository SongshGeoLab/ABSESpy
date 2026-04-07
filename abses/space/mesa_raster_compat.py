"""Compatibility helpers for mesa-geo raster APIs across versions.

Mesa-geo's ``RasterLayer`` initialization and ``_update_transform`` behavior
varies between releases. ABSESpy uses ``PatchModule`` with ``_cells`` and a
``cached_property`` for ``cells``; upstream probes like ``getattr(self,
"cells", None)`` during early construction can recurse through ``__getattr__``.
This module centralizes safe, capability-based handling.
"""

from __future__ import annotations

from typing import Any


def raster_base_update_transform(instance: Any) -> None:
    """Apply ``RasterBase._update_transform`` without ``RasterLayer`` side effects.

    Args:
        instance: A ``RasterLayer`` subclass instance (e.g. ``PatchModule``).
    """
    from mesa_geo.raster_layers import RasterBase

    RasterBase._update_transform(instance)


def maybe_sync_cell_xy(instance: Any) -> None:
    """Call ``_sync_cell_xy`` when the upstream class provides it and cells exist.

    Older mesa-geo releases do not define ``_sync_cell_xy``. Newer releases
    sync cell centers after transform updates when cell storage is ready.

    Args:
        instance: A ``RasterLayer`` subclass instance (e.g. ``PatchModule``).
    """
    if instance.__dict__.get("_cells") is None:
        return
    sync = getattr(type(instance), "_sync_cell_xy", None)
    if sync is None:
        return
    sync(instance)
