#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
每一个世界里的斑块
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Tuple

from mesa_geo.raster_layers import RasterBase
from pyproj import CRS

from abses.agents.container import _CellAgentsContainer
from abses.core.base import BaseModelElement
from abses.core.protocols import ActorProtocol
from abses.human.links import _LinkNodeCell
from abses.utils.errors import ABSESpyError

if TYPE_CHECKING:
    from abses.core.types import ActorsList, Pos, TargetName
    from abses.space.patch import PatchModule


def raster_attribute(func_or_property):
    """Turn the method into a property that the patch can extract.

    This decorator can be used in two ways:
    1. As a simple decorator for a method: @raster_attribute
    2. With an existing property that has getter and setter: @property_name.setter

    Example:
        ```
        class TestCell(Cell):
            # Simple usage
            @raster_attribute
            def test(self):
                return 1

            # With setter
            @raster_attribute
            def state(self):
                return self._state

            @state.setter
            def state(self, value):
                self._state = value

        # Using this test cell to create a PatchModule.
        module = PatchModule.from_resolution(
            model=MainModel(),
            shape=(3, 3),
            cell_cls=TestCell,
        )

        # now, the attribute 'test' of TestCell can be accessible in the module, as spatial data (i.e., raster layer).

        >>> module.cell_properties
        >>> set('test', 'state')

        >>> array = module.get_raster('test')
        >>> np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ])
        ```
    """
    if isinstance(func_or_property, property):
        # 如果已经是一个 property，保留其 getter 和 setter
        prop = func_or_property
        setattr(prop.fget, "is_decorated", True)
        return prop
    else:
        # 如果是一个普通方法，将其转换为 property
        func = func_or_property
        setattr(func, "is_decorated", True)
        return property(func)


class PatchCell(_LinkNodeCell, BaseModelElement, ActorProtocol):
    """A patch cell of a `RasterLayer`.
    Subclassing this class to create a custom cell.
    When class attribute `max_agents` is assigned,
    the `agents` property will be limited to the number of agents.

    Attributes:
        agents:
            The agents located at here.
        layer:
            The `RasterLayer` where this `PatchCell` belongs.
    """

    max_agents: Optional[int] = None

    def __init__(
        self,
        layer: PatchModule,
        indices: Pos,
        pos: Optional[Pos] = None,
    ):
        BaseModelElement.__init__(self, model=layer.model)
        _LinkNodeCell.__init__(self)
        self.indices = indices
        self.pos = pos
        self._set_layer(layer=layer)

    def __repr__(self) -> str:
        return f"<Cell at {self.layer}[{self.indices}]>"

    @classmethod
    def __attribute_properties__(cls) -> set[str]:
        """Properties that should be found in the `RasterLayer`.

        Users should decorate a property attribute when subclassing `PatchCell` to make it accessible in the `RasterLayer`.
        """
        return {
            name
            for name, method in cls.__dict__.items()
            if isinstance(method, property)
            and getattr(method.fget, "is_decorated", False)
        }

    @property
    def layer(self) -> PatchModule:
        """`RasterLayer` where this `PatchCell` belongs."""
        if self._layer is None:
            raise ABSESpyError(
                "PatchCell must belong to a layer."
                f"However, {self} has no layer."
                "Did you create this cell in the correct way?"
            )
        return self._layer

    @property
    def agents(self) -> _CellAgentsContainer:
        """The agents located at here."""
        return self._agents

    @property
    def coordinate(self) -> Tuple[float, float]:
        """The position of this cell."""
        row, col = self.indices
        return self.layer.transform_coord(row=row, col=col)

    @property
    def geo_type(self) -> str:
        """Return the geo_type"""
        # TODO: 返回地理类型，可以是 Geometry 或 Raster
        return "Cell"

    @property
    def crs(self) -> Optional[CRS]:
        """The crs of this cell, the same as the layer."""
        return self.layer.crs

    @property
    def is_empty(self) -> bool:
        """Check if the cell is empty."""
        return len(self.agents) == 0

    def _set_layer(self, layer: PatchModule) -> None:
        if not isinstance(layer, RasterBase):
            raise TypeError(f"{type(layer)} is not valid layer.")
        # set layer property
        self._layer = layer
        # set agents container
        self._agents = _CellAgentsContainer(
            layer.model, cell=self, max_len=getattr(self, "max_agents", float("inf"))
        )

    def get(
        self,
        attr: str,
        target: Optional[TargetName] = None,
        default: Any = None,
    ) -> Any:
        """Gets the value of an attribute or registered property.
        Automatically update the value if it is the dynamic variable of the layer.

        Parameters:
            attr: The name of attribute to get.
            target: Optional target name.
            default: Default value if attribute is not found.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: Attribute value of the associated patch cell.
        """
        # if attr in self.layer.dynamic_variables:
        #     self.layer.dynamic_var(attr_name=attr)
        return super().get(attr=attr, target=target, default=default)

    def neighboring(
        self,
        moore: bool = False,
        radius: int = 1,
        include_center: bool = False,
        annular: bool = False,
    ) -> ActorsList["PatchCell"]:
        """Get the grid around the patch.

        Parameters:
            moore: Whether to include the Moore neighborhood.
            radius: The radius of the neighborhood.
            include_center: Whether to include the center cell.
            annular: Whether to use an annular neighborhood.

        Returns:
            ActorsList[PatchCell]: The neighboring cells.
        """
        return self.layer.get_neighboring_by_indices(
            self.indices,
            moore=moore,
            radius=radius,
            include_center=include_center,
            annular=annular,
        )
