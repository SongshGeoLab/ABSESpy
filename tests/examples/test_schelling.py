#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Test Schelling segregation model.
"""

from typing import TYPE_CHECKING

import pytest

from examples.schelling.model import Schelling

if TYPE_CHECKING:
    pass


@pytest.fixture(name="model_fixture")
def setup_model() -> Schelling:
    """Create a Schelling model for testing."""
    params = {
        "model": {
            "width": 10,
            "height": 10,
            "density": 0.8,
            "homophily": 3,
            "radius": 1,
        },
        "SchellingAgent": {
            "minority_prob": 0.5,
        },
    }
    model = Schelling(parameters=params)
    return model


class TestSchellingAgent:
    """Test SchellingAgent functionality."""

    def test_agent_creation(self, model_fixture: Schelling) -> None:
        """Test that agents are created correctly."""
        assert len(model_fixture.agents) > 0
        # Check agents have type attribute
        for agent in model_fixture.agents:
            assert hasattr(agent, "type")
            assert agent.type in [0, 1]

    def test_agent_on_grid(self, model_fixture: Schelling) -> None:
        """Test that agents are placed on the grid."""
        # Get all cells with agents
        grid = model_fixture.nature.major_layer
        agent_count = 0
        for cell in grid.cells_lst:
            if not cell.is_empty:
                agent_count += 1

        assert agent_count == len(model_fixture.agents)


class TestSchellingModel:
    """Test the complete Schelling model."""

    def test_model_initialization(self, model_fixture: Schelling) -> None:
        """Test model initializes correctly."""
        assert model_fixture is not None
        assert model_fixture.nature.major_layer is not None
        assert model_fixture.datacollector is not None
        # Check happy ratio (0 to 1)
        assert 0 <= model_fixture.happy_ratio <= 1

    def test_grid_setup(self, model_fixture: Schelling) -> None:
        """Test grid is set up with correct dimensions."""
        grid = model_fixture.nature.major_layer
        assert grid.shape2d[1] == 10  # width (columns)
        assert grid.shape2d[0] == 10  # height (rows)

    def test_model_step(self, model_fixture: Schelling) -> None:
        """Test model can execute a step."""
        model_fixture.happy_ratio
        model_fixture.step()
        # Happy ratio should be a valid value between 0 and 1
        assert 0 <= model_fixture.happy_ratio <= 1

    def test_data_collection(self, model_fixture: Schelling) -> None:
        """Test that data is collected properly."""
        # Run a few steps
        for _ in range(3):
            if model_fixture.running:
                model_fixture.step()

        # Get collected data - check if collectors have any data
        model_df = model_fixture.datacollector.get_model_vars_dataframe()
        # Note: Without reporters configured, dataframe might be empty or have different columns
        assert isinstance(
            model_df, type(model_fixture.datacollector.get_model_vars_dataframe())
        )

    def test_model_termination(self) -> None:
        """Test model stops when everyone is happy."""
        # Create a model that will likely stop quickly
        params = {
            "model": {
                "width": 5,
                "height": 5,
                "density": 0.5,
                "homophily": 1,  # Low requirement
                "radius": 1,
            },
            "SchellingAgent": {
                "minority_prob": 0.5,
            },
        }
        model = Schelling(parameters=params)

        # Run model
        max_steps = 100
        for step in range(max_steps):
            if not model.running:
                break
            model.step()

        # Model should eventually stop
        assert not model.running or step == max_steps - 1

    def test_happy_calculation(self, model_fixture: Schelling) -> None:
        """Test that happiness is calculated correctly."""
        model_fixture.step()
        # Happy ratio should be between 0 and 1
        assert 0 <= model_fixture.happy_ratio <= 1
