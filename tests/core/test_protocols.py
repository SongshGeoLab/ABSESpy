#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
Tests for Protocol conformance.

This module ensures that all concrete implementations correctly
satisfy their Protocol contracts.
"""

from abses import Actor, MainModel
from abses.core.base import BaseModule
from abses.core.protocols import (
    ActorProtocol,
    ModuleProtocol,
)


class TestProtocolConformance:
    """Test that concrete classes satisfy their Protocol contracts.

    Note: We test structural conformance (duck typing) rather than
    isinstance checks since we removed @runtime_checkable for performance.
    """

    def test_mainmodel_satisfies_protocol(self):
        """Verify MainModel implements MainModelProtocol interface."""
        model = MainModel()

        # Check required attributes exist and have correct types
        assert hasattr(model, "name") and isinstance(model.name, str)
        assert hasattr(model, "settings")
        assert hasattr(model, "params")
        assert hasattr(model, "agents")
        assert hasattr(model, "human")
        assert hasattr(model, "nature")
        assert hasattr(model, "time")
        assert hasattr(model, "steps") and isinstance(model.steps, int)
        assert hasattr(model, "running") and isinstance(model.running, bool)

        # Check required methods exist and are callable
        assert callable(getattr(model, "run_model", None))
        assert callable(getattr(model, "setup", None))
        assert callable(getattr(model, "step", None))
        assert callable(getattr(model, "end", None))
        assert callable(getattr(model, "add_name", None))

    def test_actor_satisfies_protocol(self):
        """Verify Actor implements ActorProtocol."""
        model = MainModel()
        actor = Actor(model)
        assert isinstance(actor, ActorProtocol)

        # Check required attributes
        assert hasattr(actor, "unique_id")
        assert hasattr(actor, "pos")
        assert hasattr(actor, "alive")
        assert hasattr(actor, "model")
        assert hasattr(actor, "move")

        # Check required methods
        assert callable(actor.die)
        assert callable(actor.step)
        assert callable(actor.initialize)

    def test_subsystem_satisfies_protocol(self):
        """Verify BaseHuman and BaseNature implement SubSystemProtocol interface."""
        model = MainModel()

        # Test Human subsystem structure
        assert hasattr(model.human, "modules")
        assert isinstance(model.human.modules, dict)
        assert hasattr(model.human, "state")
        assert hasattr(model.human, "opening")
        assert callable(getattr(model.human, "create_module", None))

        # Test Nature subsystem structure
        assert hasattr(model.nature, "modules")
        assert isinstance(model.nature.modules, dict)
        assert hasattr(model.nature, "state")
        assert hasattr(model.nature, "opening")
        assert callable(getattr(model.nature, "create_module", None))

    def test_agents_container_satisfies_protocol(self):
        """Verify agents container implements AgentsContainerProtocol interface."""
        model = MainModel()
        container = model.agents

        # Check container structure
        assert hasattr(container, "model")
        assert hasattr(container, "__iter__")
        assert hasattr(container, "__len__")
        assert hasattr(container, "__getitem__")

        # Check required methods exist and are callable
        assert callable(getattr(container, "add", None))
        assert callable(getattr(container, "remove", None))
        assert callable(getattr(container, "select", None))


class TestProtocolTypeHints:
    """Test that Protocol type hints work correctly."""

    def test_module_protocol_return_types(self):
        """Test ModuleProtocol return types."""
        model = MainModel()
        module = BaseModule(model, name="test")

        # These should have correct types
        state = module.state
        assert hasattr(state, "value")  # IntEnum

        opening: bool = module.opening
        assert isinstance(opening, bool)

    def test_dynamic_variable_generic_support(self):
        """Test that DynamicVariableProtocol supports generics."""
        from abses.core.base_variable import BaseDynamicVariable
        from abses.core.protocols import DynamicVariableProtocol

        model = MainModel()
        element = BaseModule(model, name="test")

        # Create a dynamic variable
        var = BaseDynamicVariable(
            name="test_var",
            obj=element,
            data=42,
            function=lambda data: data * 2,
        )

        # Should satisfy protocol
        assert isinstance(var, DynamicVariableProtocol)

        # Test caching
        value1 = var.now()
        value2 = var.cache
        assert value1 == value2 == 84


class TestProtocolCompatibility:
    """Test backward compatibility with Protocol changes."""

    def test_modules_dict_compatibility(self):
        """Verify modules dict works with iteration patterns."""
        model = MainModel()

        # Should be able to iterate over values
        for module in model.nature.modules.values():
            assert isinstance(module, ModuleProtocol)

        # Should be able to access by name
        if model.nature.modules:
            first_name = next(iter(model.nature.modules.keys()))
            module = model.nature.modules[first_name]
            assert isinstance(module, ModuleProtocol)

    def test_deprecated_movement_protocol_alias(self):
        """Verify _MovementsProtocol alias still works."""
        from abses.core.protocols import MovementProtocol, _MovementsProtocol

        assert _MovementsProtocol is MovementProtocol
