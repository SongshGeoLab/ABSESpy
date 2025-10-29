"""Basic functionality tests for ABSESpy core components.

These tests verify that the core classes can be created and perform basic operations.
They serve as a foundation for more complex tests.
"""

from omegaconf import DictConfig

from abses import Actor, BaseNature, MainModel, PatchCell


class TestBasicModelCreation:
    """Test basic model creation and initialization."""

    def test_model_creation_with_config(self) -> None:
        """Test that MainModel can be created with a configuration."""
        config = DictConfig({"model": {"name": "test_model"}})
        model = MainModel(parameters=config)

        # Model name defaults to class name if not explicitly set
        assert model.name == "MainModel"
        assert hasattr(model, "agents")
        assert hasattr(model, "nature")
        assert hasattr(model, "time")
        assert hasattr(model, "datacollector")

    def test_model_creation_without_config(self) -> None:
        """Test that MainModel can be created without configuration."""
        model = MainModel()

        assert hasattr(model, "agents")
        assert hasattr(model, "nature")
        assert hasattr(model, "time")
        assert hasattr(model, "datacollector")

    def test_model_has_required_properties(self) -> None:
        """Test that MainModel has all required properties."""
        model = MainModel()

        # Check core properties exist
        assert hasattr(model, "agents")
        assert hasattr(model, "nature")
        assert hasattr(model, "time")
        assert hasattr(model, "params")
        assert hasattr(model, "random")

        # Check that properties return expected types
        assert hasattr(model.nature, "create_module")
        assert hasattr(model.time, "tick")


class TestBasicActorCreation:
    """Test basic actor creation and properties."""

    def test_actor_creation(self) -> None:
        """Test that Actor can be created."""
        model = MainModel()
        actor = Actor(model=model)

        assert actor.model is model
        assert isinstance(actor.unique_id, int)
        assert actor.alive is True
        assert hasattr(actor, "pos")
        assert hasattr(actor, "move")

    def test_actor_has_required_properties(self) -> None:
        """Test that Actor has all required properties."""
        model = MainModel()
        actor = Actor(model=model)

        # Check core properties exist
        assert hasattr(actor, "unique_id")
        assert hasattr(actor, "alive")
        assert hasattr(actor, "pos")
        assert hasattr(actor, "move")
        assert hasattr(actor, "model")

        # Check that properties return expected types
        assert isinstance(actor.unique_id, int)
        assert isinstance(actor.alive, bool)


class TestBasicNatureCreation:
    """Test basic nature subsystem creation."""

    def test_nature_creation(self) -> None:
        """Test that BaseNature can be created."""
        model = MainModel()
        nature = BaseNature(model=model)

        assert nature.model is model
        assert hasattr(nature, "create_module")

    def test_nature_create_module(self) -> None:
        """Test that BaseNature can create a module."""
        model = MainModel()
        nature = BaseNature(model=model)

        module = nature.create_module(shape=(5, 5), resolution=1.0, cell_cls=PatchCell)

        assert module is not None
        assert hasattr(module, "array_cells")
        assert hasattr(module, "cells_lst")
        assert module.shape2d == (5, 5)


class TestBasicPatchCellCreation:
    """Test basic patch cell creation."""

    def test_patch_cell_creation(self) -> None:
        """Test that PatchCell can be created through module."""
        model = MainModel()
        nature = BaseNature(model=model)
        module = nature.create_module(shape=(3, 3), resolution=1.0, cell_cls=PatchCell)

        cell = module.array_cells[0, 0]

        assert cell is not None
        assert hasattr(cell, "neighboring")
        assert hasattr(cell, "agents")
        assert hasattr(cell, "pos")

    def test_patch_cell_neighboring(self) -> None:
        """Test that PatchCell neighboring works."""
        model = MainModel()
        nature = BaseNature(model=model)
        module = nature.create_module(shape=(3, 3), resolution=1.0, cell_cls=PatchCell)

        center_cell = module.array_cells[1, 1]  # Center of 3x3 grid
        neighbors = center_cell.neighboring(radius=1, moore=True, include_center=False)

        assert len(neighbors) == 8  # 8 neighbors in Moore neighborhood


class TestBasicAgentManagement:
    """Test basic agent management through the agents container."""

    def test_agent_creation_through_container(self) -> None:
        """Test that agents can be created through the container."""
        model = MainModel()

        # Create a custom actor class
        class TestActor(Actor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.test_value = 42

        # Create agent through container
        actor = model.agents.new(TestActor, num=1).item()

        assert isinstance(actor, TestActor)
        assert actor.test_value == 42
        assert actor.model is model

    def test_agent_selection_by_type(self) -> None:
        """Test that agents can be selected by type."""
        model = MainModel()

        class Farmer(Actor):
            pass

        class Hunter(Actor):
            pass

        # Create multiple agents
        model.agents.new(Farmer, num=3)
        model.agents.new(Hunter, num=2)

        # Select by type
        farmers = model.agents[Farmer]
        hunters = model.agents[Hunter]

        assert len(farmers) == 3
        assert len(hunters) == 2
        assert all(isinstance(f, Farmer) for f in farmers)
        assert all(isinstance(h, Hunter) for h in hunters)

    def test_agent_selection_with_filter(self) -> None:
        """Test that agents can be selected with filters."""
        model = MainModel()

        class TestActor(Actor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.value = kwargs.get("value", 0)

        # Create agents with different values
        model.agents.new(TestActor, num=5, value=10)
        model.agents.new(TestActor, num=3, value=20)

        # Select with filter
        high_value_agents = model.agents.select(lambda a: a.value == 20)

        assert len(high_value_agents) == 3
        assert all(a.value == 20 for a in high_value_agents)
