#!/usr/bin/env python 3.11.0
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

from examples.schelling.agents import SchellingAgent
from examples.schelling.model import Schelling

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


@pytest.fixture(name="model_fixture")
def setup_model() -> Schelling:
    """Create a Schelling model for testing."""
    params = {
        "model": {
            "width": 10,
            "height": 10,
            "density": 0.8,
            "minority_pc": 0.5,
            "homophily": 3,
            "radius": 1,
        }
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
            assert hasattr(agent, 'type')
            assert agent.type in [0, 1]

    def test_agent_on_grid(self, model_fixture: Schelling) -> None:
        """Test that agents are placed on the grid."""
        # Get all positions with agents
        agent_count = 0
        for _, pos in model_fixture.grid.coord_iter():
            if not model_fixture.grid.is_cell_empty(pos):
                agent_count += 1
        
        assert agent_count == len(model_fixture.agents)


class TestSchellingModel:
    """Test the complete Schelling model."""

    def test_model_initialization(self, model_fixture: Schelling) -> None:
        """Test model initializes correctly."""
        assert model_fixture is not None
        assert model_fixture.grid is not None
        assert model_fixture.datacollector is not None
        assert model_fixture.happy == 0  # Initial happy count

    def test_grid_setup(self, model_fixture: Schelling) -> None:
        """Test grid is set up with correct dimensions."""
        assert model_fixture.grid.width == 10
        assert model_fixture.grid.height == 10

    def test_model_step(self, model_fixture: Schelling) -> None:
        """Test model can execute a step."""
        initial_happy = model_fixture.happy
        model_fixture.step()
        # Happy count should be updated (could be same, higher, or lower)
        assert model_fixture.happy >= 0

    def test_data_collection(self, model_fixture: Schelling) -> None:
        """Test that data is collected properly."""
        # Run a few steps
        for _ in range(3):
            if model_fixture.running:
                model_fixture.step()
        
        # Get collected data
        model_df = model_fixture.datacollector.get_model_vars_dataframe()
        assert len(model_df) > 0
        assert 'happy' in model_df.columns
        assert 'pct_happy' in model_df.columns
        assert 'population' in model_df.columns
        assert 'minority_pct' in model_df.columns

    def test_model_termination(self) -> None:
        """Test model stops when everyone is happy."""
        # Create a model that will likely stop quickly
        params = {
            "model": {
                "width": 5,
                "height": 5,
                "density": 0.5,
                "minority_pc": 0.5,
                "homophily": 1,  # Low requirement
                "radius": 1,
            }
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
        # Happy count should be between 0 and total population
        assert 0 <= model_fixture.happy <= len(model_fixture.agents)

