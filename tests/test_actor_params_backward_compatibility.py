#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Test backward compatibility for Actor parameter extraction.

Tests that Actor can access parameters using both PascalCase (0.8.0+ style)
and lowercase (0.7.x style) configuration keys.
"""

import warnings

import pytest
from omegaconf import DictConfig

from abses import MainModel
from abses.agents import Actor


class Farmer(Actor):
    """Test actor for parameter extraction."""

    def setup(self) -> None:
        """Setup actor with parameters from config."""
        self.capital = self.params.get("initial_capital", 0)
        self.risk = self.p.get("risk_aversion", 0.0)


class Trader(Actor):
    """Test actor for parameter extraction."""

    def setup(self) -> None:
        """Setup actor with parameters from config."""
        self.goods = self.params.get("initial_goods", 0)


def test_actor_params_pascalcase_style() -> None:
    """Test Actor parameter extraction with PascalCase (0.8.0+ style).

    This is the new style where parameters use the class name as key.
    """
    config = DictConfig(
        {
            "Farmer": {"initial_capital": 1000, "risk_aversion": 0.5},
            "Trader": {"initial_goods": 50},
        }
    )

    model = MainModel(parameters=config)

    # Create actors
    farmers = model.agents.new(Farmer, 2)
    traders = model.agents.new(Trader, 1)

    # Verify parameters are correctly loaded
    assert farmers[0].capital == 1000
    assert farmers[0].risk == 0.5
    assert farmers[1].capital == 1000
    assert traders[0].goods == 50


def test_actor_params_lowercase_style() -> None:
    """Test Actor parameter extraction with lowercase (0.7.x style).

    This is the old style where parameters use lowercase class name as key.
    Should work for backward compatibility.
    """
    config = DictConfig(
        {
            "farmer": {"initial_capital": 2000, "risk_aversion": 0.3},
            "trader": {"initial_goods": 100},
        }
    )

    model = MainModel(parameters=config)

    # Create actors
    farmers = model.agents.new(Farmer, 2)
    traders = model.agents.new(Trader, 1)

    # Verify parameters are correctly loaded from lowercase keys
    assert farmers[0].capital == 2000
    assert farmers[0].risk == 0.3
    assert farmers[1].capital == 2000
    assert traders[0].goods == 100


def test_actor_params_priority_pascalcase_over_lowercase() -> None:
    """Test that PascalCase takes priority over lowercase when both exist.

    If both 'Farmer' and 'farmer' exist in config, 'Farmer' should be used.
    """
    config = DictConfig(
        {
            "Farmer": {"initial_capital": 1000, "risk_aversion": 0.5},
            "farmer": {"initial_capital": 2000, "risk_aversion": 0.3},
        }
    )

    model = MainModel(parameters=config)
    farmers = model.agents.new(Farmer, 1)

    # Should use PascalCase values (1000, 0.5), not lowercase values (2000, 0.3)
    assert farmers[0].capital == 1000
    assert farmers[0].risk == 0.5


def test_actor_params_empty_pascalcase_falls_back_to_lowercase() -> None:
    """Test that empty PascalCase config falls back to lowercase.

    If 'Farmer' exists but is empty, should try 'farmer'.
    """
    config = DictConfig(
        {
            "Farmer": {},  # Empty
            "farmer": {"initial_capital": 3000, "risk_aversion": 0.7},
        }
    )

    model = MainModel(parameters=config)
    farmers = model.agents.new(Farmer, 1)

    # Should fall back to lowercase values
    assert farmers[0].capital == 3000
    assert farmers[0].risk == 0.7


def test_actor_params_no_config() -> None:
    """Test Actor parameter extraction when no config exists.

    Should return empty DictConfig and use default values.
    """
    config = DictConfig({})  # No actor parameters

    model = MainModel(parameters=config)
    farmers = model.agents.new(Farmer, 1)

    # Should use default values from setup method
    assert farmers[0].capital == 0
    assert farmers[0].risk == 0.0


def test_actor_params_alias_p() -> None:
    """Test that the 'p' alias works for params."""
    config = DictConfig({"TestFarmer": {"initial_capital": 5000, "risk_aversion": 0.9}})

    model = MainModel(parameters=config)

    class TestFarmer(Actor):
        """Test actor using p alias."""

        def setup(self) -> None:
            """Setup using p alias."""
            self.capital = self.p.get("initial_capital", 0)

    farmers = model.agents.new(TestFarmer, 1)
    assert farmers[0].capital == 5000


def test_mixed_actor_types_with_different_styles() -> None:
    """Test multiple actor types using different parameter styles.

    Some actors can use PascalCase while others use lowercase.
    """
    config = DictConfig(
        {
            "Farmer": {"initial_capital": 1000},  # PascalCase
            "trader": {"initial_goods": 50},  # lowercase
        }
    )

    model = MainModel(parameters=config)

    farmers = model.agents.new(Farmer, 1)
    traders = model.agents.new(Trader, 1)

    # Both should work
    assert farmers[0].capital == 1000
    assert traders[0].goods == 50


def test_actor_params_with_nested_config() -> None:
    """Test Actor parameters with nested configuration."""
    config = DictConfig(
        {
            "AdvancedFarmer": {
                "initial_capital": 1000,
                "risk_aversion": 0.5,
                "preferences": {"crop_type": "wheat", "tech_level": 2},
            }
        }
    )

    model = MainModel(parameters=config)

    class AdvancedFarmer(Actor):
        """Test actor with nested config."""

        def setup(self) -> None:
            """Setup with nested config."""
            self.capital = self.params.initial_capital
            self.crop = self.params.preferences.crop_type
            self.tech = self.params.preferences.tech_level

    farmers = model.agents.new(AdvancedFarmer, 1)

    assert farmers[0].capital == 1000
    assert farmers[0].crop == "wheat"
    assert farmers[0].tech == 2


def test_actor_params_inheritance() -> None:
    """Test that parameter extraction works with Actor inheritance."""

    class BaseFarmer(Actor):
        """Base farmer actor."""

        def setup(self) -> None:
            """Setup base farmer."""
            self.capital = self.params.get("initial_capital", 100)

    class OrganicFarmer(BaseFarmer):
        """Organic farmer inheriting from BaseFarmer."""

        def setup(self) -> None:
            """Setup organic farmer."""
            super().setup()
            self.organic_cert = self.params.get("organic_certified", False)

    # Test with PascalCase
    config = DictConfig(
        {"OrganicFarmer": {"initial_capital": 2000, "organic_certified": True}}
    )

    model = MainModel(parameters=config)
    farmers = model.agents.new(OrganicFarmer, 1)

    assert farmers[0].capital == 2000
    assert farmers[0].organic_cert is True

    # Test with lowercase for backward compatibility
    config2 = DictConfig(
        {"organicfarmer": {"initial_capital": 3000, "organic_certified": False}}
    )

    model2 = MainModel(parameters=config2)
    farmers2 = model2.agents.new(OrganicFarmer, 1)

    assert farmers2[0].capital == 3000
    assert farmers2[0].organic_cert is False


def test_deprecation_warning_for_lowercase() -> None:
    """Test that using lowercase parameters triggers a DeprecationWarning."""
    config = DictConfig({"farmer": {"initial_capital": 2000, "risk_aversion": 0.3}})

    model = MainModel(parameters=config)

    # Should trigger a DeprecationWarning when accessing params
    with pytest.warns(
        DeprecationWarning, match="Using lowercase parameter key 'farmer'"
    ):
        farmers = model.agents.new(Farmer, 1)

    # But parameters should still work
    assert farmers[0].capital == 2000
    assert farmers[0].risk == 0.3


def test_no_warning_for_pascalcase() -> None:
    """Test that using PascalCase does not trigger warnings."""
    config = DictConfig({"Farmer": {"initial_capital": 1000, "risk_aversion": 0.5}})

    model = MainModel(parameters=config)

    # Should not trigger any warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # Turn warnings into errors
        farmers = model.agents.new(Farmer, 1)

    # Parameters should work normally
    assert farmers[0].capital == 1000
    assert farmers[0].risk == 0.5


def test_warning_message_content() -> None:
    """Test that the deprecation warning contains helpful information."""
    config = DictConfig({"farmer": {"initial_capital": 2000}})

    model = MainModel(parameters=config)

    with pytest.warns(DeprecationWarning) as warning_info:
        _ = model.agents.new(Farmer, 1)

    # Check warning message contains key information
    warning_message = str(warning_info[0].message)
    assert "lowercase parameter key 'farmer'" in warning_message
    assert "component 'Farmer'" in warning_message
    assert "deprecated" in warning_message
    assert "removed in a future version" in warning_message
    assert "rename 'farmer' to 'Farmer'" in warning_message
