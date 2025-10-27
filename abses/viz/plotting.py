#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Plotting utilities for spatial data visualization in ABSESpy.

This module provides convenience functions for quickly visualizing
spatial raster attributes from PatchModule instances.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from matplotlib import pyplot as plt
from matplotlib.colors import Colormap, ListedColormap

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from abses.space.patch import PatchModule


class PlotableAttribute:
    """A wrapper for raster attributes that enables convenient plotting.

    This class allows you to call `.plot()` on raster attributes
    accessed through PatchModule, providing a fluent API for visualization.

    Examples:
        >>> # Access attribute through module
        >>> module.state.plot(cmap={0: 'black', 1: 'green'})
        >>> # Save plot without displaying
        >>> module.elevation.plot(cmap='terrain', save_path='elev.png', show=False)
    """

    def __init__(self, module: "PatchModule", attr_name: str) -> None:
        """
        Initialize a plotable attribute.

        Args:
            module: The PatchModule instance.
            attr_name: Name of the raster attribute.
        """
        self._module = module
        self._attr_name = attr_name

    def plot(
        self,
        *,
        cmap: Optional[Union[Colormap, Dict[Any, str]]] = None,
        ax: Optional[plt.Axes] = None,
        title: Optional[str] = None,
        show: bool = True,
        save_path: Optional[str] = None,
        **kwargs: Any,
    ) -> "Figure":
        """
        Plot the raster attribute.

        Args:
            cmap: Colormap or color dictionary. If a dictionary is provided,
                maps attribute values to colors. If None, uses default colormap.
            ax: Optional matplotlib axes. If None, creates a new figure.
            title: Optional title for the plot. Defaults to attr name.
            show: Whether to display the plot immediately. Default: True.
            save_path: Optional path to save the figure. If None, don't save.
            **kwargs: Additional arguments passed to xarray.DataArray.plot().

        Returns:
            matplotlib.figure.Figure: The figure containing the plot.

        Examples:
            >>> # Simple plot with default colormap
            >>> module.state.plot()
            >>>
            >>> # Plot with color dictionary
            >>> module.state.plot(cmap={0: 'black', 1: 'green', 2: 'red'})
            >>>
            >>> # Save to file without displaying
            >>> module.elevation.plot(save_path='elev.png', show=False)
        """
        return plot_raster(
            module=self._module,
            attr=self._attr_name,
            cmap=cmap,
            ax=ax,
            title=title,
            show=show,
            **kwargs,
        )


def plot_raster(
    module: "PatchModule",
    attr: str,
    *,
    cmap: Optional[Union[Colormap, Dict[Any, str]]] = None,
    ax: Optional[plt.Axes] = None,
    title: Optional[str] = None,
    show: bool = True,
    save_path: Optional[str] = None,
    **kwargs: Any,
) -> "Figure":
    """
    Plot a raster attribute from a PatchModule.

    This function provides a convenient way to visualize spatial data attributes
    from a PatchModule, automatically handling color mapping and coordinate systems.

    Args:
        module: The PatchModule instance containing the spatial data.
        attr: Name of the raster attribute to plot.
        cmap: Colormap or color dictionary. If a dictionary is provided,
            maps attribute values to colors. If None, uses default colormap.
        ax: Optional matplotlib axes. If None, creates a new figure.
        title: Optional title for the plot. Defaults to attr name.
        show: Whether to display the plot immediately. Default: True.
        save_path: Optional path to save the figure. If None, don't save.
        **kwargs: Additional arguments passed to xarray.DataArray.plot().

    Returns:
        matplotlib.figure.Figure: The figure containing the plot.

    Examples:
        >>> # Using a color dictionary
        >>> colors = {0: 'black', 1: 'green', 2: 'red'}
        >>> plot_raster(grid, 'state', cmap=colors)
        >>>
        >>> # Using matplotlib colormap
        >>> plot_raster(grid, 'elevation', cmap='terrain')
        >>>
        >>> # Save to file
        >>> plot_raster(grid, 'moisture', save_path='moisture.png', show=False)
    """
    # Get spatial data
    data = module.get_xarray(attr)

    # Handle colormap
    if isinstance(cmap, dict):
        # Create ListedColormap from dictionary
        # Convert enum keys to integers for proper mapping
        int_cmap = {}
        for key, color in cmap.items():
            int_key = (
                int(key)
                if hasattr(key, "__int__") and not isinstance(key, int)
                else key
            )
            int_cmap[int_key] = color
        categories = sorted(int_cmap.keys())
        color_list = [int_cmap[c] for c in categories]

        # Create ListedColormap
        cmap = ListedColormap(color_list)

        # Set vmin and vmax to ensure correct color mapping for discrete values
        # Add 0.5 offset to center each category in its color range
        if "vmin" not in kwargs:
            kwargs["vmin"] = min(categories) - 0.5
        if "vmax" not in kwargs:
            kwargs["vmax"] = max(categories) + 0.5
    elif cmap is None:
        # Use default colormap
        cmap = plt.cm.viridis

    # Create figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    else:
        fig = ax.figure

    # Plot the data
    data.plot(ax=ax, cmap=cmap, **kwargs)

    # Set title
    if title is None:
        title = attr.replace("_", " ").title()
    ax.set_title(title)

    # Adjust layout
    fig.tight_layout()

    # Save to file if path provided
    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return fig


def quick_plot(
    module: "PatchModule",
    attr: str,
    **kwargs: Any,
) -> "Figure":
    """
    Quick plotting function with minimal configuration.

    This is a convenience wrapper around plot_raster() that uses sensible defaults.

    Args:
        module: The PatchModule instance.
        attr: Attribute name to plot.
        **kwargs: Arguments passed to plot_raster().

    Returns:
        matplotlib.figure.Figure: The figure.

    Examples:
        >>> quick_plot(grid, 'state', cmap={0: 'black', 1: 'green'})
    """
    return plot_raster(module, attr, **kwargs)
