#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Tests for the Solara visualization utilities.

Tests the visualization components to ensure they properly handle
agent portrayal functions returning both dict and AgentPortrayalStyle objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from abses.viz.solara import (
    collect_agent_data,
    draw_orthogonal_grid,
    make_mpl_space_component,
)

if TYPE_CHECKING:
    from abses.core.model import MainModel
    from abses.space.patch import PatchModule


class TestCollectAgentData:
    """Test the collect_agent_data function."""

    def test_collect_agent_data_with_dict(self, model: "MainModel") -> None:
        """Test collect_agent_data with dict-based agent portrayal."""
        from abses.agents.actor import Actor

        # Create a simple agent class
        class TestAgent(Actor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.agent_type = 0

        # Create space and agents
        space: PatchModule = model.nature.create_module(shape=(5, 5))
        for i in range(3):
            agent = TestAgent(model=model)
            cell = space.cells_lst[i]
            agent.move.to(cell)

        # Define agent portrayal function returning dict
        def agent_portrayal(agent: TestAgent) -> dict:
            return {
                "color": "tab:orange" if agent.agent_type == 0 else "tab:blue",
                "size": 50,
                "marker": "o",
            }

        # Collect agent data
        result = collect_agent_data(space, agent_portrayal)

        # Verify results
        assert "loc" in result
        assert len(result["loc"]) == 3
        assert len(result["c"]) == 3
        assert len(result["s"]) == 3
        assert all(c == "tab:orange" for c in result["c"])

    def test_collect_agent_data_with_agentportrayalstyle(
        self, model: "MainModel"
    ) -> None:
        """Test collect_agent_data with AgentPortrayalStyle object (Mesa 3.3+)."""
        try:
            from mesa.visualization.components import AgentPortrayalStyle
        except ImportError:
            pytest.skip("AgentPortrayalStyle not available (requires Mesa 3.3+)")

        from abses.agents.actor import Actor

        # Create a simple agent class
        class TestAgent(Actor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.agent_type = 0

        # Create space and agents
        space: PatchModule = model.nature.create_module(shape=(5, 5))
        for i in range(3):
            agent = TestAgent(model=model)
            cell = space.cells_lst[i]
            agent.move.to(cell)

        # Define agent portrayal function returning AgentPortrayalStyle
        def agent_portrayal(agent: TestAgent) -> AgentPortrayalStyle:
            return AgentPortrayalStyle(
                color="tab:orange" if agent.agent_type == 0 else "tab:blue",
                size=50,
            )

        # Collect agent data
        result = collect_agent_data(space, agent_portrayal)

        # Verify results
        assert "loc" in result
        assert len(result["loc"]) == 3
        assert len(result["c"]) == 3
        assert len(result["s"]) == 3
        assert all(c == "tab:orange" for c in result["c"])

    def test_collect_agent_data_empty_space(self, model: "MainModel") -> None:
        """Test collect_agent_data with empty space."""
        space: PatchModule = model.nature.create_module(shape=(5, 5))

        def agent_portrayal(agent) -> dict:
            return {"color": "red", "size": 10}

        # Collect agent data from empty space
        result = collect_agent_data(space, agent_portrayal)

        # Verify results
        assert "loc" in result
        assert len(result["loc"]) == 0
        assert result["loc"].shape == (0, 2)


class TestDrawOrthogonalGrid:
    """Test the draw_orthogonal_grid function."""

    def test_draw_orthogonal_grid_basic(self, model: "MainModel") -> None:
        """Test draw_orthogonal_grid with basic setup."""
        import matplotlib.pyplot as plt

        from abses.agents.actor import Actor

        # Create a simple agent class
        class TestAgent(Actor):
            pass

        # Create space and agents
        space: PatchModule = model.nature.create_module(shape=(5, 5))
        for i in range(3):
            agent = TestAgent(model=model)
            cell = space.cells_lst[i]
            agent.move.to(cell)

        # Define agent portrayal function
        def agent_portrayal(agent) -> dict:
            return {"color": "tab:blue", "size": 25}

        # Draw grid
        ax = draw_orthogonal_grid(space, agent_portrayal, draw_grid=True)

        # Verify axes properties
        assert ax is not None
        assert ax.get_xlim() == (-0.5, 4.5)
        assert ax.get_ylim() == (-0.5, 4.5)

        plt.close(ax.figure)

    def test_draw_orthogonal_grid_without_grid_lines(self, model: "MainModel") -> None:
        """Test draw_orthogonal_grid without grid lines."""
        import matplotlib.pyplot as plt

        from abses.agents.actor import Actor

        # Create a simple agent class
        class TestAgent(Actor):
            pass

        # Create space
        space: PatchModule = model.nature.create_module(shape=(3, 3))

        # Define agent portrayal function
        def agent_portrayal(agent) -> dict:
            return {}

        # Draw grid without grid lines
        ax = draw_orthogonal_grid(space, agent_portrayal, draw_grid=False)

        # Verify axes properties
        assert ax is not None
        assert ax.get_xlim() == (-0.5, 2.5)
        assert ax.get_ylim() == (-0.5, 2.5)

        plt.close(ax.figure)


class TestMakeMplSpaceComponent:
    """Test the make_mpl_space_component function."""

    def test_make_mpl_space_component_basic(self, model: "MainModel") -> None:
        """Test make_mpl_space_component with basic setup."""

        # Define agent portrayal function
        def agent_portrayal(agent) -> dict:
            return {"color": "tab:blue", "size": 25}

        # Create component factory
        component_factory = make_mpl_space_component(agent_portrayal=agent_portrayal)

        # Verify it's callable
        assert callable(component_factory)

        # Create component
        component = component_factory(model)

        # Verify component is created (it's a Solara component)
        assert component is not None

    def test_make_mpl_space_component_with_property_layers(
        self, model: "MainModel"
    ) -> None:
        """Test make_mpl_space_component with property layers."""

        # Define agent portrayal function
        def agent_portrayal(agent) -> dict:
            return {"color": "tab:blue", "size": 25}

        # Define property layer portrayal
        # Note: This test just verifies the component can be created with property layers
        # The actual layer data would need to be set up properly in a real scenario
        propertylayer_portrayal = {
            "mask": {"colormap": "viridis", "alpha": 0.5, "colorbar": False}
        }

        # Create component factory
        component_factory = make_mpl_space_component(
            agent_portrayal=agent_portrayal,
            propertylayer_portrayal=propertylayer_portrayal,
        )

        # Verify it's callable
        assert callable(component_factory)

        # Create component (may raise error if layer doesn't exist, which is expected)
        # We just verify the factory works
        try:
            component = component_factory(model)
            assert component is not None
        except (ValueError, KeyError, AttributeError):
            # Expected if layer doesn't exist - the factory still works
            pass

    def test_make_mpl_space_component_default_agent_portrayal(
        self, model: "MainModel"
    ) -> None:
        """Test make_mpl_space_component with default agent portrayal."""
        # Create component factory without agent_portrayal
        component_factory = make_mpl_space_component()

        # Verify it's callable
        assert callable(component_factory)

        # Create component
        component = component_factory(model)

        # Verify component is created
        assert component is not None
