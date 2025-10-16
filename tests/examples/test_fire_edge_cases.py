#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
"""Edge case tests for fire_spread model."""

from typing import TYPE_CHECKING

from examples.fire_spread.model import Forest

if TYPE_CHECKING:
    pass


class TestFireEdgeCases:
    """Test edge cases for fire spread model."""

    def test_zero_density_no_division_error(self) -> None:
        """Test that density=0 doesn't cause ZeroDivisionError."""
        # Arrange
        forest = Forest(parameters={"model": {"density": 0, "shape": (10, 10)}})

        # Act
        forest.setup()
        burned_rate = forest.burned_rate

        # Assert
        assert burned_rate == 0.0, f"Expected 0.0, got {burned_rate}"
        assert forest.num_trees == 0, f"Expected 0 trees, got {forest.num_trees}"

    def test_full_density_setup(self) -> None:
        """Test that density=1 creates trees on all cells."""
        # Arrange
        forest = Forest(parameters={"model": {"density": 1, "shape": (5, 5)}})

        # Act
        forest.setup()

        # Assert
        assert forest.num_trees == 25, f"Expected 25 trees, got {forest.num_trees}"
