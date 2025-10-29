#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Tests for the plotting utilities.

Tests the plot_raster and quick_plot functions to ensure they
properly visualize spatial data from PatchModule instances.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from abses.viz import PlotableAttribute, plot_raster, quick_plot

if TYPE_CHECKING:
    from abses.core.model import MainModel


class TestPlotRaster:
    """Test the plot_raster function."""

    def test_plot_raster_with_dict_colormap(self, model: "MainModel") -> None:
        """Test plot_raster with dictionary colormap."""
        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)
        color_dict = {0: "blue", 1: "red", 2: "green"}

        fig = plot_raster(module, "value", cmap=color_dict, show=False)
        assert fig is not None

    def test_plot_raster_with_custom_title(self, model: "MainModel") -> None:
        """Test plot_raster with custom title."""
        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)

        fig = plot_raster(module, "value", title="Custom Title", show=False)
        assert fig is not None

    def test_plot_raster_save_functionality(self, model: "MainModel") -> None:
        """Test plot_raster with save_path parameter."""
        import os
        import tempfile

        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            temp_path = tmp_file.name

        try:
            plot_raster(module, "value", save_path=temp_path, show=False)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestPlotableAttribute:
    """Test the PlotableAttribute class."""

    def test_plotable_attribute_creation(self, model: "MainModel") -> None:
        """Test PlotableAttribute creation and basic functionality."""
        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)

        # Create PlotableAttribute
        plotable = PlotableAttribute(module, "value")
        assert plotable._module is module
        assert plotable._attr_name == "value"

        # Test plot method
        fig = plotable.plot(show=False)
        assert fig is not None

    def test_dynamic_attribute_access(self, model: "MainModel") -> None:
        """Test dynamic access to attributes through __getattr__."""
        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)

        # Access attribute dynamically
        plotable = module.value

        # Verify it's a PlotableAttribute
        assert isinstance(plotable, PlotableAttribute)

        # Test plot method
        fig = plotable.plot(show=False)
        assert fig is not None


class TestQuickPlot:
    """Test the quick_plot function."""

    def test_quick_plot_basic(self, model: "MainModel") -> None:
        """Test quick_plot basic functionality."""
        from abses.space.cells import PatchCell, raster_attribute

        class TestCell(PatchCell):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._value = 0

            @raster_attribute
            def value(self) -> int:
                return self._value

        module = model.nature.create_module(shape=(5, 5), cell_cls=TestCell)
        fig = quick_plot(module, "value", show=False)
        assert fig is not None
