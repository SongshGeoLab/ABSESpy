#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""PatchModule class"""

from __future__ import annotations

import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)

import geopandas as gpd
import numpy as np
import pyproj
import rioxarray
import xarray as xr
from geocube.api.core import make_geocube
from loguru import logger
from mesa.space import Coordinate
from mesa_geo.raster_layers import RasterLayer
from numpy.typing import NDArray
from rasterio.enums import Resampling
from shapely import Geometry

from abses.agents.actor import Actor
from abses.agents.sequences import ActorsList
from abses.core.base import BaseModule
from abses.core.primitives import DEFAULT_CRS
from abses.space.cells import PatchCell
from abses.utils.errors import ABSESpyError
from abses.utils.func import get_buffer, set_null_values
from abses.utils.random import ListRandom

if TYPE_CHECKING:
    from abses.core.types import (
        CellFilter,
        MainModelProtocol,
        Number,
        Raster,
        T,
    )


class PatchModule(BaseModule, RasterLayer):
    """Base class for managing raster-based spatial modules in ABSESpy.

    Inherits from both Module and RasterLayer to provide comprehensive spatial data management.
    Extends mesa-geo's RasterLayer with additional capabilities for:
    - Agent placement and management
    - Integration with xarray/rasterio for data I/O
    - Dynamic attribute handling
    - Spatial operations and analysis

    Attributes:
        cell_properties: Set of accessible cell attributes (decorated by @raster_attribute).
        attributes: All accessible attributes including cell_properties.
        shape2d: Raster dimensions as (height, width).
        shape3d: Raster dimensions as (1, height, width) for rasterio compatibility.
        array_cells: NumPy array of PatchCell objects.
        coords: Coordinate system dictionary with 'x' and 'y' arrays.
        random: Random selection proxy for cells.
        mask: Boolean array indicating accessible cells.
        cells_lst: ActorsList containing all cells.
        plot: Visualization interface for the module.
    """

    def __init__(
        self,
        model: MainModelProtocol,
        name: Optional[str] = None,
        cell_cls: Type[PatchCell] = PatchCell,
        *,
        # Resolution-based creation parameters
        shape: Optional[Coordinate] = None,
        resolution: Number | None | Tuple[Number, Number] = 1,
        # Layer copy parameters
        source_layer: Optional[PatchModule] = None,
        # Xarray-based creation parameters
        xda: Optional[xr.DataArray] = None,
        attr_name: Optional[str] = None,
        apply_raster: bool = False,
        masked: bool = True,
        # Vector-based creation parameters
        vector_file: Optional[Union[str, gpd.GeoDataFrame]] = None,
        # Raster file-based creation parameters
        raster_file: Optional[str] = None,
        band: int = 1,
        # Common parameters
        crs: Optional[Union[pyproj.CRS, str]] = None,
        total_bounds: Optional[List[float]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        **kwargs: Any,
    ):
        """Initializes a new PatchModule instance with a unified API.

        This constructor automatically determines the appropriate creation method based on the
        provided parameters. It supports creating a PatchModule from:
        - Resolution and shape
        - Copying an existing layer
        - xarray DataArray
        - Vector file or GeoDataFrame
        - Raster file

        Args:
            model: Parent model instance.
            name: Module identifier. Defaults to lowercase class name.
            cell_cls: Class to use for creating cells. Defaults to PatchCell.

            # Resolution-based creation parameters
            shape: Array shape (height, width) for creating a new module.
            resolution: Spatial resolution when creating coordinates.

            # Layer copy parameters
            source_layer: Existing PatchModule to copy.

            # Xarray-based creation parameters
            xda: xarray DataArray containing raster data.
            attr_name: Attribute name for the loaded raster data.
            apply_raster: Whether to apply raster data to cells.
            masked: Whether to use mask from the data.

            # Vector-based creation parameters
            vector_file: Path to vector file or GeoDataFrame.

            # Raster file-based creation parameters
            raster_file: Path to raster file.
            band: Band number to use from raster file.

            # Common parameters
            crs: Coordinate Reference System.
            total_bounds: Spatial bounds [minx, miny, maxx, maxy].
            width: Width of the raster in cells.
            height: Height of the raster in cells.
            **kwargs: Additional arguments passed to RasterLayer initialization.
        """
        # Initialize BaseModule
        BaseModule.__init__(self, model, name=name)

        # Normalize CRS if provided
        if crs is not None:
            crs = crs

        # Determine creation method based on provided parameters
        if raster_file is not None:
            # Create from raster file
            xda = rioxarray.open_rasterio(raster_file, masked=masked, **kwargs)
            xda = xda.sel(band=band)

            # Update parameters for xarray-based creation
            width = xda.rio.width
            height = xda.rio.height
            crs = xda.rio.crs
            total_bounds = xda.rio.bounds()

            # Apply raster data if attr_name is provided (backward compatibility)
            # In 0.7.x, providing attr_name automatically applied the raster data
            if attr_name is not None:
                apply_raster = True

        elif vector_file is not None:
            # Create from vector file
            if resolution is None:
                raise ValueError(
                    "Resolution must be provided when creating from vector file"
                )

            # Convert to GeoDataFrame if needed
            if isinstance(vector_file, str):
                gdf = gpd.read_file(vector_file)
            elif isinstance(vector_file, gpd.GeoDataFrame):
                gdf = vector_file
            else:
                raise TypeError(f"Unsupported vector type: {type(vector_file)}")

            # Set attribute name if not provided
            if attr_name is None:
                gdf, attr_name = gdf.reset_index(), "index"

            # Convert resolution to tuple if needed
            if isinstance(resolution, (int, float)):
                resolution = (resolution, resolution)

            # Create xarray from vector
            xda = make_geocube(gdf, measurements=[attr_name], resolution=resolution)[
                attr_name
            ]

            # Update parameters for xarray-based creation
            width = xda.rio.width
            height = xda.rio.height
            crs = xda.rio.crs
            total_bounds = xda.rio.bounds()

            # Apply raster data if attr_name is provided (backward compatibility)
            if attr_name is not None:
                apply_raster = True

        elif xda is not None:
            # Create from xarray DataArray
            # Flip data if y-axis is ascending
            if xda.y[0].item() < xda.y[-1].item():
                xda.data = np.flipud(xda.data)

            # Update parameters
            width = xda.rio.width
            height = xda.rio.height
            crs = xda.rio.crs
            total_bounds = xda.rio.bounds()

            # Apply raster data if attr_name is provided (backward compatibility)
            if attr_name is not None:
                apply_raster = True

        elif source_layer is not None:
            # Copy from existing layer
            if not isinstance(source_layer, PatchModule):
                raise TypeError(f"{source_layer} is not a valid PatchModule.")

            # Copy parameters from source layer
            width = source_layer.width
            height = source_layer.height
            crs = source_layer.crs
            total_bounds = source_layer.total_bounds

        elif shape is not None:
            # Create from resolution and shape
            assert isinstance(resolution, (int, float))
            assert width is None and height is None
            height, width = shape
            if crs is None:
                crs = DEFAULT_CRS  # Already normalized
            total_bounds = [0, 0, width * resolution, height * resolution]

        # Ensure required parameters are provided
        if width is None or height is None or crs is None or total_bounds is None:
            raise ValueError(
                "Insufficient parameters provided. Must provide either: "
                "1) shape and resolution, 2) source_layer, 3) xda, "
                "4) vector_file and resolution, or 5) raster_file"
            )

        # Remove PatchModule-specific parameters that shouldn't be passed to RasterLayer
        # Even though they are explicit parameters, we remove them from kwargs as a safeguard
        for key in ["apply_raster", "attr_name"]:
            kwargs.pop(key, None)

        # Initialize RasterLayer with the determined parameters
        RasterLayer.__init__(
            self,
            model=model,
            width=width,
            height=height,
            crs=crs,  # Now using normalized CRS
            total_bounds=total_bounds,
            cell_cls=cell_cls,
            **kwargs,
        )

        logger.info("Initializing a new Model Layer...")
        self._mask: np.ndarray = np.ones(self.shape2d).astype(bool)

        # Apply mask if provided
        if masked and xda is not None:
            self.mask = xda.notnull().to_numpy()

        # Apply raster data if requested
        if apply_raster and xda is not None and attr_name is not None:
            self.apply_raster(xda.to_numpy(), attr_name=attr_name)

    def _initialize_cells(
        self,
        model: MainModelProtocol,
        cell_cls: type[PatchCell],
    ) -> None:
        """Override the method of RasterLayer."""
        if model is not self.model:
            raise ValueError("Model mismatching.")
        self._cells = []
        for x in range(self.width):
            col: List = []
            for y in range(self.height):
                row_idx, col_idx = self.height - y - 1, x
                col.append(
                    cell_cls(
                        self,
                        pos=(x, y),
                        indices=(row_idx, col_idx),
                    )
                )
            self._cells.append(col)

    @functools.cached_property
    def cells_lst(self) -> ActorsList[PatchCell]:
        """The cells stored in this layer."""
        return ActorsList(self.model, self.array_cells[self.mask])

    @property
    def mask(self) -> np.ndarray:
        """Where is not accessible."""
        return self._mask

    @mask.setter
    def mask(self, array: np.ndarray) -> None:
        """Setting mask."""
        if array.shape != self.shape2d:
            raise ABSESpyError(
                f"Shape mismatching, setting mask {array.shape}."
                f"but the module is expecting shape {self.shape2d}."
            )
        self._mask = array.astype(bool)

    def __repr__(self):
        return f"<{self.name}{self.shape2d}: {len(self.attributes)} vars>"

    @property
    def cell_properties(self) -> set[str]:
        """The accessible attributes of cells stored in this layer.
        All `PatchCell` methods decorated by `raster_attribute` should be appeared here.
        """
        return self.cell_cls.__attribute_properties__()

    @property
    def xda(self) -> xr.DataArray:
        """Get the xarray raster layer with spatial coordinates."""
        xda = xr.DataArray(data=self.mask, coords=self.coords)
        xda = xda.rio.write_crs(self.crs)
        xda = xda.rio.set_spatial_dims("x", "y")
        xda = xda.rio.write_transform(self.transform)
        return xda.rio.write_coordinate_system()

    @property
    def attributes(self) -> set[str]:
        """All accessible attributes from this layer."""
        return self._attributes | self.cell_properties

    @property
    def shape2d(self) -> Coordinate:
        """Raster shape in 2D (height, width).
        This is useful when working with 2d `numpy.array`.
        """
        return self.height, self.width

    @property
    def shape3d(self) -> Coordinate:
        """Raster shape in 3D (1, heigh, width).
        This is useful when working with `rasterio` band.
        """
        return 1, self.height, self.width

    @functools.cached_property
    def cells(self) -> List[List[PatchCell]]:
        """The cells stored in this layer."""
        return self._cells

    @functools.cached_property
    def array_cells(self) -> NDArray[T]:
        """Array type of the `PatchCell` stored in this module."""
        return np.flipud(np.array(self._cells, dtype=object).T)

    @property
    def coords(self) -> Coordinate:
        """Coordinate system of the raster data.

        This is useful when working with `xarray.DataArray`.
        """
        transform = self.transform
        # 注意 y 方向的分辨率通常是负值
        res_x, res_y = transform.a, -transform.e
        minx, miny, maxx, maxy = self.total_bounds
        x_coord = np.arange(minx, maxx, res_x)
        # 注意 y 坐标是从上到下递减的
        y_coord = np.flip(np.arange(miny, maxy, res_y))
        return {
            "y": y_coord,
            "x": x_coord,
        }

    @property
    def agents(self) -> ActorsList[Actor]:
        """Return a list of all agents in the module."""
        agents = []
        for c in self.cells_lst:
            agents.extend(list(c.agents))
        return ActorsList(self.model, agents)

    def transform_coord(self, row: int, col: int) -> Coordinate:
        """Converts grid indices to real-world coordinates.

        Args:
            row: Grid row index.
            col: Grid column index.

        Returns:
            Tuple of (x, y) real-world coordinates.

        Raises:
            IndexError: If indices are out of bounds.
        """
        if self.indices_out_of_bounds(pos=(row, col)):
            raise IndexError(f"Out of bounds: {row, col}")
        return self.transform * (col, row)

    def _attr_or_array(
        self, data: None | str | np.ndarray | xr.DataArray
    ) -> np.ndarray:
        """Determine the incoming data type and turn it into a reasonable array."""
        if data is None:
            return np.ones(self.shape2d)
        if isinstance(data, xr.DataArray):
            data = data.to_numpy()
        if isinstance(data, np.ndarray):
            if data.shape == self.shape2d:
                return data
            raise ABSESpyError(
                f"Shape mismatch: {data.shape} [input] != {self.shape2d} [expected]."
            )
        if isinstance(data, str) and data in self.attributes:
            return self.get_raster(data)
        raise TypeError("Invalid data type or shape.")

    def dynamic_var(
        self,
        attr_name: str,
        dtype: Literal["numpy", "xarray"] = "numpy",
    ) -> np.ndarray:
        """Update and get dynamic variable.

        Parameters:
            attr_name:
                The dynamic variable to retrieve.

        Returns:
            2D numpy.ndarray data of the variable.
        """
        # 获取动态变量，及其附加属性
        array = super().dynamic_var(attr_name)
        assert isinstance(array, (np.ndarray, xr.DataArray, xr.Dataset))
        kwargs = super().dynamic_variables[attr_name].attrs
        # 将矩阵转换为三维，并更新空间数据
        self.apply_raster(array, attr_name=attr_name, **kwargs)
        if dtype == "numpy":
            return self.get_raster(attr_name, update=False)
        if dtype == "xarray":
            return self.get_xarray(attr_name, update=False)
        raise ValueError(f"Unknown expected dtype {dtype}.")

    def get_xarray(
        self,
        attr_name: Optional[str] = None,
        update: bool = True,
    ) -> xr.DataArray:
        """Creates an xarray DataArray representation with spatial coordinates.

        Args:
            attr_name: Attribute to retrieve. If None, returns all attributes.
            update: If True, updates dynamic variables before retrieval.

        Returns:
            xarray.DataArray with spatial coordinates and CRS information.
        """
        data = self.get_raster(attr_name=attr_name, update=update)
        if attr_name:
            name = attr_name
            data = data.reshape(self.shape2d)
            coords = self.coords
        else:
            coords = {"variable": list(self.attributes)}
            coords |= self.coords
            name = self.name
        return xr.DataArray(
            data=data,
            name=name,
            coords=coords,
        ).rio.write_crs(self.crs)

    @property
    def random(self) -> ListRandom:
        """Randomly"""
        return self.cells_lst.random

    def _select_by_geometry(
        self,
        geometry: Geometry,
        **kwargs: Dict[str, Any],
    ) -> np.ndarray:
        """Gets all the cells that intersect the given geometry.

        Parameters:
            geometry:
                Shapely Geometry to search intersected cells.
            **kwargs:
                Args pass to the function `rasterasterio.mask.mask`.

        Returns:
            A numpy array of clipped cells.
        """
        # TODO 研究一下为什么需要转换为整数，转换bool结果不一样了
        return self.xda.astype(np.int32, casting="safe").rio.clip(
            [geometry], all_touched=False, drop=False, **kwargs
        )

    def select(
        self,
        where: Optional[CellFilter] = None,
    ) -> ActorsList[PatchCell]:
        """Selects cells based on specified criteria.

        Args:
            where: Selection filter. Can be:
                - None: Select all cells
                - str: Select by attribute name
                - numpy.ndarray: Boolean mask array
                - Shapely.Geometry: Select cells intersecting geometry

        Returns:
            ActorsList containing selected cells.

        Raises:
            TypeError: If where parameter is of unsupported type.

        Example:
            >>> # Select cells with elevation > 100
            >>> high_cells = module.select(module.get_raster("elevation") > 100)
            >>> # Select cells within polygon
            >>> cells = module.select(polygon)
        """
        if isinstance(where, Geometry):
            mask_ = self._select_by_geometry(geometry=where)
        elif isinstance(where, (np.ndarray, str, xr.DataArray)) or where is None:
            mask_ = self._attr_or_array(where).reshape(self.shape2d)
        else:
            raise TypeError(f"{type(where)} is not supported for selecting cells.")
        mask_ = np.nan_to_num(mask_, nan=0.0).astype(bool)
        return ActorsList(self.model, self.array_cells[mask_])

    sel = select

    def apply(self, ufunc: Callable[..., Any], *args: Any, **kwargs: Any) -> np.ndarray:
        """Apply a function to array cells.

        Parameters:
            ufunc:
                A function to apply.
            *args:
                Positional arguments to pass to the function.
            **kwargs:
                Keyword arguments to pass to the function.

        Returns:
            The result of the function applied to the array cells.
        """
        func = functools.partial(ufunc, *args, **kwargs)
        return np.vectorize(func)(self.array_cells)

    def coord_iter(self) -> Iterator[tuple[Coordinate, PatchCell]]:
        """
        An iterator that returns coordinates as well as cell contents.
        """
        return np.ndenumerate(self.array_cells)

    def _add_attribute(
        self,
        data: np.ndarray,
        attr_name: Optional[str] = None,
        flipud: bool = False,
        apply_mask: bool = False,
    ) -> None:
        try:
            data = data.reshape(self.shape2d)
        except ValueError as e:
            raise ValueError(
                f"Data shape does not match raster shape. "
                f"Expected {self.shape2d}, received {data.shape}."
            ) from e
        if apply_mask:
            set_null_values(data, ~self.mask)
        if attr_name is None:
            attr_name = f"attribute_{len(self.attributes)}"
        self._attributes.add(attr_name)
        if flipud:
            data = np.flipud(data)
        np.vectorize(setattr)(self.array_cells, attr_name, data)

    def _add_dataarray(
        self,
        data: xr.DataArray,
        attr_name: Optional[str] = None,
        cover_crs: bool = False,
        resampling_method: str = "nearest",
        flipud: bool = False,
    ) -> None:
        if cover_crs:
            data.rio.write_crs(self.crs, inplace=True)
        resampling = getattr(Resampling, resampling_method)
        data = data.rio.reproject_match(
            self.xda,
            resampling=resampling,
        ).to_numpy()
        self._add_attribute(data, attr_name, flipud=flipud)

    def apply_raster(
        self, data: Raster, attr_name: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Applies raster data to cells as attributes.

        Args:
            data: Input raster data. Can be:
                - numpy.ndarray: 2D array matching module shape
                - xarray.DataArray: With spatial coordinates
                - xarray.Dataset: With named variables
            attr_name: Name for the new attribute. Required for xarray.Dataset.
            **kwargs: Additional options:
                cover_crs: Whether to override input data CRS
                resampling_method: Method for resampling ("nearest", etc.)
                flipud: Whether to flip data vertically

        Raises:
            ValueError: If attr_name not provided for Dataset input.
            ValueError: If data shape doesn't match module shape.

        Example:
            >>> # Apply elevation data
            >>> module.apply_raster(elevation_array, attr_name="elevation")
            >>> # Apply data from xarray
            >>> module.apply_raster(xda, resampling_method="bilinear")
        """
        if isinstance(data, np.ndarray):
            self._add_attribute(data, attr_name, **kwargs)
        elif isinstance(data, xr.DataArray):
            self._add_dataarray(data, attr_name, **kwargs)
        elif isinstance(data, xr.Dataset):
            if attr_name is None:
                raise ValueError("Attribute name is required for xr.Dataset.")
            dataarray = data[attr_name]
            self._add_dataarray(dataarray, attr_name, **kwargs)

    def get_raster(
        self,
        attr_name: Optional[str] = None,
        update: bool = True,
    ) -> np.ndarray:
        """Obtaining the Raster layer by attribute.

        Parameters:
            attr_name:
                The attribute to retrieve.
                If None (by default), retrieve all attributes as a 3D array.

        Returns:
            A 3D array of attribute.
        """
        if attr_name in self.dynamic_variables and update:
            return self.dynamic_var(attr_name=attr_name).reshape(self.shape3d)
        if attr_name is not None and attr_name not in self.attributes:
            raise ValueError(
                f"Attribute {attr_name} does not exist. "
                f"Choose from {self.attributes}, or set `attr_name` to `None` to retrieve all."
            )
        if attr_name is None:
            assert bool(self.attributes), "No attribute available."
            attr_names = self.attributes
        else:
            attr_names = {attr_name}
        data = []
        for name in attr_names:
            array = np.vectorize(getattr)(self.array_cells, name)
            data.append(array)
        return np.stack(data)

    def reproject(
        self,
        xda: xr.DataArray,
        resampling: Resampling | str = "nearest",
        **kwargs,
    ) -> xr.DataArray:
        """Reproject the xarray data to the same CRS as this layer."""
        if isinstance(resampling, str):
            resampling = getattr(Resampling, resampling)
        return xda.rio.reproject_match(self.xda, resampling=resampling, **kwargs)

    def get_neighboring_cells(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
    ) -> ActorsList[PatchCell]:
        """Gets neighboring cells around a position.

        Args:
            pos: Center position (x, y).
            moore: If True, uses Moore neighborhood (8 neighbors).
                  If False, uses von Neumann neighborhood (4 neighbors).
            include_center: Whether to include the center cell.
            radius: Neighborhood radius in cells.

        Returns:
            ActorsList containing neighboring cells.

        Example:
            >>> # Get Moore neighborhood with radius 2
            >>> neighbors = module.get_neighboring_cells((5,5), moore=True, radius=2)
        """
        cells = super().get_neighboring_cells(pos, moore, include_center, radius)
        return ActorsList(self.model, cells)

    @functools.lru_cache(maxsize=1000)
    def get_neighboring_by_indices(
        self,
        indices: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1,
        annular: bool = False,
    ) -> ActorsList[PatchCell]:
        """Getting neighboring positions of the given coordinate.

        Parameters:
            indices:
                The indices to get the neighborhood.
            moore:
                Whether to use Moore neighborhood.
                If False, use Von Neumann neighborhood.
            include_center:
                Whether to include the center cell.
                Default is False.
            radius:
                The radius of the neighborhood.
                Default is 1.
            annular:
                Whether to use annular (ring) neighborhood.
                Default is False.

        Returns:
            An `ActorsList` of neighboring cells.
        """
        row, col = indices
        mask_arr = np.zeros(self.shape2d, dtype=bool)
        mask_arr[row, col] = True
        mask_arr = get_buffer(mask_arr, radius=radius, moor=moore, annular=annular)
        mask_arr[row, col] = include_center
        return ActorsList(self.model, self.array_cells[mask_arr])

    def indices_out_of_bounds(self, pos: Coordinate) -> bool:
        """
        Determines whether position is off the grid.

        Parameters:
            pos: Position to check.

        Returns:
            True if position is off the grid, False otherwise.
        """

        row, col = pos
        return row < 0 or row >= self.height or col < 0 or col >= self.width
