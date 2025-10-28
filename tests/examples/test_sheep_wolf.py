#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Test wolf-sheep model.
"""

from typing import TYPE_CHECKING

import pytest

from examples.wolf_sheep.model import Grass, Sheep, Wolf, WolfSheepModel

if TYPE_CHECKING:
    pass


@pytest.fixture(name="model_fixture")
def setup_model() -> WolfSheepModel:
    """Create a wolf-sheep model for testing."""
    params = {
        "model": {
            "shape": (10, 10),
            "n_wolves": 5,
            "n_sheep": 20,
            "rep_rate": 0.05,
        },
        "rep_rate": 0.05,  # Also at root level for actor access
    }
    model = WolfSheepModel(parameters=params)
    model.setup()
    return model


class TestGrass:
    """Test Grass (PatchCell) functionality."""

    @pytest.fixture(name="grass_fixture")
    def setup_grass(self, model_fixture: WolfSheepModel) -> Grass:
        """Get a grass cell from the model."""
        return model_fixture.nature.array_cells[0, 0]

    def test_initialization(self, grass_fixture: Grass) -> None:
        """Test grass cell initializes correctly."""
        assert grass_fixture is not None
        assert grass_fixture.empty is False
        assert grass_fixture._countdown == 5

    def test_grow_mechanism(self, grass_fixture: Grass) -> None:
        """Test grass growing mechanism."""
        # Make grass empty
        grass_fixture._empty = True
        grass_fixture._countdown = 1

        # Grow should countdown
        grass_fixture.grow()
        assert grass_fixture._countdown == 0
        assert grass_fixture.empty is True

        # Next grow should restore grass
        grass_fixture.grow()
        assert grass_fixture.empty is False
        assert grass_fixture._countdown == 5

    def test_raster_attribute(self, model_fixture: WolfSheepModel) -> None:
        """Test that empty is accessible as raster attribute."""
        # Get raster data
        nature = model_fixture.nature
        # Should be able to get empty attribute across all cells
        assert hasattr(nature, "array_cells")


class TestAnimal:
    """Test Animal base class functionality."""

    def test_wolf_initialization(self, model_fixture: WolfSheepModel) -> None:
        """Test wolf initializes with correct energy."""
        wolves = model_fixture.agents.select(agent_type=Wolf)
        assert len(wolves) == 5
        for wolf in wolves:
            assert wolf.energy == 50  # Model uses initial energy of 50

    def test_sheep_initialization(self, model_fixture: WolfSheepModel) -> None:
        """Test sheep initializes with correct energy."""
        sheep = model_fixture.agents.select(agent_type=Sheep)
        assert len(sheep) == 20
        for s in sheep:
            assert s.energy == 50  # Model uses initial energy of 50

    def test_energy_consumption(self, model_fixture: WolfSheepModel) -> None:
        """Test that animals consume energy."""
        wolf = model_fixture.agents.select(agent_type=Wolf)[0]
        initial_energy = wolf.energy
        wolf.update()
        assert wolf.energy == initial_energy - 1

    def test_death_on_no_energy(self, model_fixture: WolfSheepModel) -> None:
        """Test that animals die when energy reaches 0."""
        wolf = model_fixture.agents.select(agent_type=Wolf)[0]
        wolf.energy = 1
        initial_count = len(model_fixture.agents)
        wolf.update()
        # Wolf should have died
        assert len(model_fixture.agents) < initial_count


class TestWolf:
    """Test Wolf-specific behavior."""

    def test_wolf_can_eat_sheep(self, model_fixture: WolfSheepModel) -> None:
        """Test that wolf eat_sheep method works."""
        wolf = model_fixture.agents.select(agent_type=Wolf)[0]
        initial_energy = wolf.energy

        # Call eat_sheep (it may or may not find a sheep depending on position)
        wolf.eat_sheep()

        # Energy should either stay the same or increase by 10 (eating sheep)
        assert wolf.energy == initial_energy or wolf.energy == initial_energy + 10


class TestSheep:
    """Test Sheep-specific behavior."""

    def test_sheep_can_eat_grass(self, model_fixture: WolfSheepModel) -> None:
        """Test that sheep eat_grass method works."""
        sheep = model_fixture.agents.select(agent_type=Sheep)[0]

        # Ensure grass is available at sheep's location
        cell = sheep.at
        if hasattr(cell, "_empty"):
            cell._empty = False

        initial_energy = sheep.energy
        sheep.eat_grass()

        # Energy should increase since we ensured grass is available
        assert sheep.energy >= initial_energy


class TestWolfSheepModel:
    """Test the complete Wolf-Sheep model."""

    def test_model_setup(self, model_fixture: WolfSheepModel) -> None:
        """Test model sets up correctly."""
        assert model_fixture is not None
        assert hasattr(model_fixture.nature, "array_cells")
        assert len(model_fixture.agents.select(agent_type=Wolf)) == 5
        assert len(model_fixture.agents.select(agent_type=Sheep)) == 20

    def test_model_step(self, model_fixture: WolfSheepModel) -> None:
        """Test model can execute a step."""
        _initial_tick = model_fixture.time.tick  # noqa: F841
        model_fixture.step()
        # Time should not advance here (step doesn't call time.go)
        # But the step should execute without error
        assert model_fixture is not None

    def test_check_end_no_sheep(self, model_fixture: WolfSheepModel) -> None:
        """Test model stops when no sheep remain."""
        # Remove all sheep
        sheep_list = list(model_fixture.agents.select(agent_type=Sheep))
        for sheep in sheep_list:
            sheep.die()

        model_fixture.check_end()
        assert model_fixture.running is False

    def test_check_end_no_wolves(self, model_fixture: WolfSheepModel) -> None:
        """Test model stops when no wolves remain."""
        # Remove all wolves
        wolves_list = list(model_fixture.agents.select(agent_type=Wolf))
        for wolf in wolves_list:
            wolf.die()

        model_fixture.check_end()
        assert model_fixture.running is False

    def test_check_end_too_many_sheep(self, model_fixture: WolfSheepModel) -> None:
        """Test model stops when sheep population explodes."""
        # Add many sheep
        model_fixture.agents.new(Sheep, 400)

        model_fixture.check_end()
        assert model_fixture.running is False

    def test_full_simulation(self) -> None:
        """Test running the complete model for several steps."""
        params = {
            "model": {
                "shape": (10, 10),
                "n_wolves": 3,
                "n_sheep": 15,
                "rep_rate": 0.03,
            },
            "rep_rate": 0.03,  # Also at root level for actor access
        }
        model = WolfSheepModel(parameters=params)
        model.setup()

        # Run for a few steps
        for _ in range(5):
            if model.running:
                model.agents.do("step")
                model.step()

        # Model should still have some agents
        assert len(model.agents) > 0
