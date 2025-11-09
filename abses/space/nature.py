#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
The spatial module.
"""

from __future__ import annotations

from typing import Any, Type

from mesa_geo import GeoSpace

from abses.core.base import BaseSubSystem
from abses.core.primitives import DEFAULT_CRS
from abses.core.protocols import MainModelProtocol, NatureSystemProtocol
from abses.space.patch import PatchModule


class BaseNature(BaseSubSystem, GeoSpace, NatureSystemProtocol):
    """Base class for managing spatial components in an ABSESpy model.

    This class serves as a container for different raster layers (PatchModules).
    It is not a raster layer itself, but manages multiple PatchModule instances.

    Attributes:
        major_layer: Primary raster layer of the model. Defaults to first created layer.
        total_bounds: Spatial extent of the model's area of interest.
        crs: Coordinate Reference System used by the nature module.
        layers: Collection of all managed raster layers.
        modules: Factory for creating and managing PatchModules.

    Note:
        By default, an initialized ABSESpy model will create an instance of BaseNature
        as its 'nature' module.
    """

    def __init__(self, model: MainModelProtocol, name: str = "nature") -> None:
        """Initializes a new BaseNature instance.

        Args:
            model: Parent model instance this nature module belongs to.
            name: Name identifier for this module (defaults to "nature").
        """
        GeoSpace.__init__(self, crs=DEFAULT_CRS)
        BaseSubSystem.__init__(self, model, name=name)

    def create_module(
        self,
        *args: Any,
        module_cls: Type[PatchModule] = PatchModule,
        major_layer: bool = False,
        write_crs: bool = False,
        **kwargs: Any,
    ) -> PatchModule:
        """Creates a new raster layer (PatchModule) in this nature module.

        Args:
            module_cls: Custom PatchModule subclass to instantiate. If None, uses base PatchModule.
            major_layer: If True, sets created module as the major layer.
            write_crs: If True, assigns nature's CRS to module if module's CRS is None.
            **kwargs: Additional arguments passed to the creation method.

        Returns:
            Newly created PatchModule instance.

        Note:
            The first created module automatically becomes the major layer.
            The module is automatically added to nature's layers collection.
        """
        # Create the module directly with the unified API
        module = super().create_module(
            module_cls=module_cls,
            *args,
            **kwargs,
        )

        if major_layer is True:
            self.major_layer = module
        self.convert_crs(module, write_crs=write_crs)
        if module not in self.layers:
            self.add_layer(module)
        return module

    def convert_crs(self, module: PatchModule, write_crs: bool = True):
        """Convert the CRS of a module to the space's CRS.

        Args:
            module: The module to convert the CRS of.
            write_crs: If True, sets the module's CRS to the space's CRS.

        Returns:
            The module with the converted CRS.
        """
        if module.name not in self.modules:
            raise ValueError(f"{module} is not in {self}.")
        if module.crs is None:
            if write_crs:
                module.crs = self.crs
            else:
                raise ValueError(
                    f"{module.name}'s default CRS is None.Space CRS is {self.crs}.",
                )
        return module
