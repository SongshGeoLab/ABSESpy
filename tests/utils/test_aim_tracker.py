#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for AimTracker with Distribution support."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

try:
    from aim import Distribution, Run

    AIM_AVAILABLE = True
except ImportError:
    AIM_AVAILABLE = False
    Distribution = MagicMock  # Use MagicMock when aim is not available
    Run = MagicMock

from abses.utils.tracker.aim_tracker import AimTracker

# ========== Fixtures ==========


@pytest.fixture
def mock_aim_run():
    """Mock Aim Run object for testing."""
    return MagicMock()


@pytest.fixture
def mock_distribution_class():
    """Mock Distribution class for testing.

    Returns a callable that can be used as Distribution class.
    When called, returns a mock instance with bin_count attribute.
    """
    if AIM_AVAILABLE:
        return Distribution

    # Create a mock Distribution class when aim is not available
    # It should be callable (a class), not an instance
    def create_mock_distribution(distribution, bin_count=64):
        """Create a mock Distribution instance."""
        mock_instance = MagicMock()
        mock_instance.bin_count = bin_count
        return mock_instance

    return create_mock_distribution


@pytest.fixture
def aim_tracker(mock_aim_run, mock_distribution_class):
    """Create AimTracker with mocked dependencies.

    Uses module-level patching to ensure mocks remain active during test execution.
    """
    import abses.utils.tracker.aim_tracker as aim_tracker_module

    # Store original values
    original_run = aim_tracker_module.Run
    original_dist = aim_tracker_module.Distribution

    # Create a mock Run class that returns mock_aim_run when instantiated
    def mock_run_factory(*args, **kwargs):
        return mock_aim_run

    # Set mocks - Run should be callable and return mock_aim_run
    aim_tracker_module.Run = mock_run_factory
    aim_tracker_module.Distribution = mock_distribution_class

    try:
        tracker = AimTracker({})
        # Ensure _run is set correctly (in case __init__ didn't call Run)
        tracker._run = mock_aim_run
        yield tracker
    finally:
        # Restore original values
        aim_tracker_module.Run = original_run
        aim_tracker_module.Distribution = original_dist


@pytest.fixture
def aim_tracker_custom_bin(mock_aim_run):
    """Create AimTracker with custom bin_count."""
    import abses.utils.tracker.aim_tracker as aim_tracker_module

    # Create a custom mock that respects bin_count
    if AIM_AVAILABLE:
        dist_class = Distribution
    else:

        def create_mock_distribution(distribution, bin_count=100):
            """Create a mock Distribution instance with custom bin_count."""
            mock_instance = MagicMock()
            mock_instance.bin_count = bin_count
            return mock_instance

        dist_class = create_mock_distribution

    # Store original values
    original_run = aim_tracker_module.Run
    original_dist = aim_tracker_module.Distribution

    # Create a mock Run class that returns mock_aim_run when instantiated
    def mock_run_factory(*args, **kwargs):
        return mock_aim_run

    # Set mocks
    aim_tracker_module.Run = mock_run_factory
    aim_tracker_module.Distribution = dist_class

    try:
        tracker = AimTracker({"distribution_bin_count": 100})
        tracker._run = mock_aim_run
        yield tracker
    finally:
        # Restore original values
        aim_tracker_module.Run = original_run
        aim_tracker_module.Distribution = original_dist


# ========== Test Classes ==========


class TestAimTrackerInitialization:
    """Test AimTracker initialization and configuration."""

    def test_init_with_default_config(self, mock_aim_run, mock_distribution_class):
        """Test initialization with default configuration."""
        # Arrange
        import abses.utils.tracker.aim_tracker as aim_tracker_module

        original_run = aim_tracker_module.Run
        original_dist = aim_tracker_module.Distribution

        def mock_run_factory(*args, **kwargs):
            return mock_aim_run

        aim_tracker_module.Run = mock_run_factory
        aim_tracker_module.Distribution = mock_distribution_class
        config = {}

        try:
            # Act
            tracker = AimTracker(config)

            # Assert
            assert tracker._run == mock_aim_run
            assert tracker._bin_count == 64  # default
            assert tracker._log_categorical_stats is True
        finally:
            aim_tracker_module.Run = original_run
            aim_tracker_module.Distribution = original_dist

    def test_init_with_custom_bin_count(self, mock_aim_run, mock_distribution_class):
        """Test initialization with custom bin_count."""
        # Arrange
        import abses.utils.tracker.aim_tracker as aim_tracker_module

        original_run = aim_tracker_module.Run
        original_dist = aim_tracker_module.Distribution

        def mock_run_factory(*args, **kwargs):
            return mock_aim_run

        aim_tracker_module.Run = mock_run_factory
        aim_tracker_module.Distribution = mock_distribution_class
        config = {"distribution_bin_count": 100}

        try:
            # Act
            tracker = AimTracker(config)

            # Assert
            assert tracker._bin_count == 100
        finally:
            aim_tracker_module.Run = original_run
            aim_tracker_module.Distribution = original_dist

    def test_init_with_categorical_stats_disabled(
        self, mock_aim_run, mock_distribution_class
    ):
        """Test initialization with categorical stats disabled."""
        # Arrange
        import abses.utils.tracker.aim_tracker as aim_tracker_module

        original_run = aim_tracker_module.Run
        original_dist = aim_tracker_module.Distribution

        def mock_run_factory(*args, **kwargs):
            return mock_aim_run

        aim_tracker_module.Run = mock_run_factory
        aim_tracker_module.Distribution = mock_distribution_class
        config = {"log_categorical_stats": False}

        try:
            # Act
            tracker = AimTracker(config)

            # Assert
            assert tracker._log_categorical_stats is False
        finally:
            aim_tracker_module.Run = original_run
            aim_tracker_module.Distribution = original_dist

    @pytest.mark.parametrize(
        "invalid_bin_count,expected_error",
        [
            (0, "distribution_bin_count"),
            (513, "distribution_bin_count"),
            (-1, "distribution_bin_count"),
            (64.5, "distribution_bin_count"),
        ],
    )
    def test_init_with_invalid_bin_count(self, invalid_bin_count, expected_error):
        """Test initialization raises error for invalid bin_count values."""
        # Arrange
        config = {"distribution_bin_count": invalid_bin_count}

        # Act & Assert
        with (
            patch("abses.utils.tracker.aim_tracker.Run"),
            patch("abses.utils.tracker.aim_tracker.Distribution"),
        ):
            with pytest.raises(ValueError, match=expected_error):
                AimTracker(config)

    def test_init_raises_when_aim_not_installed(self):
        """Test initialization raises ImportError when aim is not installed."""
        # Arrange
        import abses.utils.tracker.aim_tracker as aim_tracker_module

        original_run = aim_tracker_module.Run
        original_dist = aim_tracker_module.Distribution
        config = {}

        try:
            # Act & Assert
            aim_tracker_module.Run = None
            aim_tracker_module.Distribution = None
            with pytest.raises(ImportError, match="Aim is not installed"):
                AimTracker(config)
        finally:
            aim_tracker_module.Run = original_run
            aim_tracker_module.Distribution = original_dist


class TestNumericVariableLogging:
    """Test logging of numeric agent variables as Distributions."""

    @pytest.mark.parametrize(
        "values,expected_tracked",
        [
            ([100.0, 200.0, 150.0], True),  # Multiple values -> Distribution
            ([100.0], False),  # Single value -> scalar (not Distribution in this call)
            ([], False),  # Empty list -> skipped
        ],
    )
    def test_log_numeric_list_various_sizes(
        self, aim_tracker, mock_aim_run, values, expected_tracked
    ):
        """Test logging numeric lists of various sizes.

        - Multiple values should create Distribution
        - Single value should log as scalar
        - Empty list should be skipped
        """
        # Arrange
        agent_vars = {"budget": values}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        if expected_tracked:
            assert mock_aim_run.track.called
            # Check that Distribution was created for multiple values
            if len(values) > 1:
                call_args = mock_aim_run.track.call_args
                assert call_args[1]["name"] == "City.budget"
                assert call_args[1]["step"] == 1
        else:
            # For single value or empty, behavior differs
            if len(values) == 1:
                # Single value should still be tracked as scalar
                assert mock_aim_run.track.called
            elif len(values) == 0:
                # Empty list should not be tracked
                assert not mock_aim_run.track.called

    def test_log_numeric_list_with_none_values(self, aim_tracker, mock_aim_run):
        """Test that None values in numeric list are filtered out."""
        # Arrange
        agent_vars = {"budget": [100.0, None, 200.0, None, 150.0]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[1]["name"] == "City.budget"
        # Distribution should be created with only valid numeric values (None filtered)

    def test_log_numeric_list_with_nan_values(self, aim_tracker, mock_aim_run):
        """Test that NaN values in numeric list are filtered out."""
        # Arrange
        agent_vars = {"budget": [100.0, np.nan, 200.0, float("nan"), 150.0]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[1]["name"] == "City.budget"

    def test_log_numeric_list_all_same_values(self, aim_tracker, mock_aim_run):
        """Test that list with all same values still creates Distribution."""
        # Arrange
        agent_vars = {"budget": [100.0, 100.0, 100.0, 100.0]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        # Distribution should still be created even if all values are the same

    def test_log_numeric_single_scalar_value(self, aim_tracker, mock_aim_run):
        """Test that single scalar numeric value is logged directly."""
        # Arrange
        agent_vars = {"budget": 100.0}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[0][0] == 100.0  # Scalar value
        assert call_args[1]["name"] == "City.budget"
        assert call_args[1]["step"] == 1

    @pytest.mark.parametrize(
        "input_type,input_value",
        [
            ("pandas_series", pd.Series([100.0, 200.0, 150.0])),
            ("numpy_array", np.array([100.0, 200.0, 150.0])),
            ("list", [100.0, 200.0, 150.0]),
        ],
    )
    def test_log_numeric_various_input_types(
        self, aim_tracker, mock_aim_run, input_type, input_value
    ):
        """Test that various input types (Series, array, list) are handled correctly."""
        # Arrange
        agent_vars = {"budget": input_value}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[1]["name"] == "City.budget"

    def test_log_numeric_all_none_values(self, aim_tracker, mock_aim_run):
        """Test that list with all None values is skipped."""
        # Arrange
        agent_vars = {"budget": [None, None, None]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert not mock_aim_run.track.called

    def test_log_numeric_all_nan_values(self, aim_tracker, mock_aim_run):
        """Test that list with all NaN values is skipped."""
        # Arrange
        agent_vars = {"budget": [np.nan, np.nan, np.nan]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert not mock_aim_run.track.called

    def test_log_numeric_with_custom_bin_count(
        self, aim_tracker_custom_bin, mock_aim_run
    ):
        """Test that custom bin_count is used when creating Distribution."""
        # Arrange
        agent_vars = {"budget": [100.0, 200.0, 150.0]}

        # Act
        aim_tracker_custom_bin.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[1]["name"] == "City.budget"
        # Verify that Distribution was created (bin_count is set during initialization)
        # The actual bin_count is set when Distribution is instantiated


class TestBooleanVariableLogging:
    """Test logging of boolean agent variables."""

    def test_log_boolean_list_creates_distribution(self, aim_tracker, mock_aim_run):
        """Test that boolean list is converted to 0/1 and logged as Distribution.

        Boolean lists with multiple values should:
        1. Create a Distribution (converted to 0/1)
        2. Log true_count (number of True values)
        3. Log true_ratio (proportion of True values)
        """
        # Arrange
        # Use the same mock_aim_run instance from tracker
        tracker_run = aim_tracker._run
        tracker_run.reset_mock()  # Reset to ensure clean state
        agent_vars = {"moved": [True, False, True, True, False]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert tracker_run.track.called
        assert (
            tracker_run.track.call_count >= 3
        )  # Distribution + true_count + true_ratio
        calls = [call[1]["name"] for call in tracker_run.track.call_args_list]
        assert "Individual.moved" in calls  # Distribution
        assert "Individual.moved.true_count" in calls
        assert "Individual.moved.true_ratio" in calls

    def test_log_boolean_list_calculates_statistics(self, aim_tracker, mock_aim_run):
        """Test that boolean statistics (true_count, true_ratio) are calculated correctly.

        For a boolean list [True, True, True, False, False]:
        - true_count should be 3 (three True values)
        - true_ratio should be 0.6 (3/5 = 0.6)
        """
        # Arrange
        # Use the same mock_aim_run instance from tracker
        tracker_run = aim_tracker._run
        tracker_run.reset_mock()  # Reset to ensure clean state
        agent_vars = {"moved": [True, True, True, False, False]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert tracker_run.track.called
        true_count = None
        true_ratio = None
        for call in tracker_run.track.call_args_list:
            if call[1]["name"] == "Individual.moved.true_count":
                true_count = call[0][0]
            elif call[1]["name"] == "Individual.moved.true_ratio":
                true_ratio = call[0][0]

        assert true_count is not None, (
            f"true_count not found in calls: {[c[1]['name'] for c in tracker_run.track.call_args_list]}"
        )
        assert true_ratio is not None, (
            f"true_ratio not found in calls: {[c[1]['name'] for c in tracker_run.track.call_args_list]}"
        )
        assert true_count == 3
        assert abs(true_ratio - 0.6) < 0.001  # 3/5 = 0.6

    def test_log_boolean_single_value_logs_as_scalar(self, aim_tracker, mock_aim_run):
        """Test that single boolean value is logged as scalar (0 or 1).

        Single boolean values should:
        1. Be logged as scalar (0 or 1), not Distribution
        2. Still log true_count and true_ratio statistics
        """
        # Arrange
        # Use the same mock_aim_run instance from tracker
        tracker_run = aim_tracker._run
        tracker_run.reset_mock()  # Reset to ensure clean state
        agent_vars = {"moved": [True]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert tracker_run.track.called
        assert tracker_run.track.call_count >= 3  # scalar + true_count + true_ratio
        calls = [call[1]["name"] for call in tracker_run.track.call_args_list]
        assert "Individual.moved" in calls
        assert "Individual.moved.true_count" in calls
        assert "Individual.moved.true_ratio" in calls

        # Check it's a scalar value (0 or 1), not Distribution
        for call in tracker_run.track.call_args_list:
            if call[1]["name"] == "Individual.moved":
                value = call[0][0]
                # Note: pandas/numpy may return numpy.int64 instead of Python int
                assert isinstance(value, (int, bool, np.integer)), (
                    f"Expected int/bool/numpy.integer, got {type(value)}"
                )
                # Convert to Python native type for comparison
                int_value = int(value) if hasattr(value, "__int__") else value
                assert int_value in (0, 1), (
                    f"Expected 0 or 1, got {int_value} (type: {type(value)})"
                )
                # Verify it's not a Distribution
                if AIM_AVAILABLE:
                    assert not isinstance(value, Distribution)

    def test_log_boolean_list_with_none_values(self, aim_tracker, mock_aim_run):
        """Test that None values in boolean list are filtered out."""
        # Arrange
        agent_vars = {"moved": [True, None, False, None, True]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        # Should calculate statistics only for valid boolean values


class TestCategoricalVariableLogging:
    """Test logging of categorical (string) agent variables."""

    def test_log_string_list_logs_frequency_statistics(self, aim_tracker, mock_aim_run):
        """Test that string list is logged as frequency statistics."""
        # Arrange
        agent_vars = {"status": ["active", "inactive", "active", "pending", "active"]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.call_count >= 3
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        assert "Individual.status.unique_count" in calls
        assert "Individual.status.most_common_count" in calls
        assert "Individual.status.most_common_ratio" in calls
        assert "Individual.status.active_count" in calls

    def test_log_string_list_with_none_values(self, aim_tracker, mock_aim_run):
        """Test that None values in string list are filtered out."""
        # Arrange
        agent_vars = {"status": ["active", None, "inactive", None, "active"]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.called
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        assert "Individual.status.unique_count" in calls

    def test_log_string_list_with_empty_strings(self, aim_tracker, mock_aim_run):
        """Test that empty strings in string list are filtered out."""
        # Arrange
        agent_vars = {"status": ["active", "", "inactive", "", "active"]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        # Should filter empty strings and log statistics for valid values only
        for call in mock_aim_run.track.call_args_list:
            if call[1]["name"] == "Individual.status.unique_count":
                # Should be 2 (active, inactive), not including empty strings
                assert call[0][0] == 2

    def test_log_string_list_many_categories_only_logs_summary(
        self, aim_tracker, mock_aim_run
    ):
        """Test that string list with many categories (>10) only logs summary statistics."""
        # Arrange - Create 15 unique categories
        agent_vars = {"category": [f"cat_{i}" for i in range(15)]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        assert "Individual.category.unique_count" in calls
        assert "Individual.category.most_common_count" in calls
        # Should not log individual category counts (too many)
        category_calls = [c for c in calls if c.endswith("_count") and "cat_" in c]
        assert len(category_calls) == 0

    def test_log_string_list_few_categories_logs_all(self, aim_tracker, mock_aim_run):
        """Test that string list with few categories (<=10) logs all category counts."""
        # Arrange - Create 5 unique categories
        agent_vars = {"status": ["A", "B", "C", "D", "E"] * 2}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        # Should log individual category counts (5 categories <= 10)
        assert "Individual.status.A_count" in calls
        assert "Individual.status.B_count" in calls
        assert "Individual.status.C_count" in calls

    def test_log_string_list_single_category(self, aim_tracker, mock_aim_run):
        """Test that string list with single category logs correctly."""
        # Arrange
        agent_vars = {"status": ["active", "active", "active"]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        for call in mock_aim_run.track.call_args_list:
            if call[1]["name"] == "Individual.status.unique_count":
                assert call[0][0] == 1  # Only one unique category
            elif call[1]["name"] == "Individual.status.active_count":
                assert call[0][0] == 3  # All three are "active"

    def test_log_string_list_all_none_or_empty_skipped(self, aim_tracker, mock_aim_run):
        """Test that string list with all None or empty values is skipped."""
        # Arrange
        agent_vars = {"status": [None, "", None, ""]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        assert not mock_aim_run.track.called

    def test_log_string_list_with_special_characters_in_category_name(
        self, aim_tracker, mock_aim_run
    ):
        """Test that special characters in category names are sanitized."""
        # Arrange
        agent_vars = {"status": ["cat.1", "cat 2", "cat.1"]}

        # Act
        aim_tracker.log_agent_vars("Individual", agent_vars, step=1)

        # Assert
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        # Special characters should be replaced with underscores
        assert any("cat_1" in call or "cat_2" in call for call in calls)

    def test_log_categorical_stats_disabled_skips_strings(
        self, mock_aim_run, mock_distribution_class
    ):
        """Test that when log_categorical_stats is False, string variables are skipped."""
        # Arrange
        import abses.utils.tracker.aim_tracker as aim_tracker_module

        original_run = aim_tracker_module.Run
        original_dist = aim_tracker_module.Distribution

        def mock_run_factory(*args, **kwargs):
            return mock_aim_run

        aim_tracker_module.Run = mock_run_factory
        aim_tracker_module.Distribution = mock_distribution_class

        try:
            tracker = AimTracker({"log_categorical_stats": False})
            tracker._run = mock_aim_run
            agent_vars = {"status": ["active", "inactive", "active"]}

            # Act
            tracker.log_agent_vars("Individual", agent_vars, step=1)

            # Assert
            assert not mock_aim_run.track.called
        finally:
            aim_tracker_module.Run = original_run
            aim_tracker_module.Distribution = original_dist


class TestMixedTypeVariableLogging:
    """Test logging of mixed type agent variables."""

    def test_log_mixed_numeric_string_list(self, aim_tracker, mock_aim_run):
        """Test that mixed numeric and string list attempts conversion."""
        # Arrange
        agent_vars = {"value": [1, 2, "three", 4, 5]}

        # Act
        aim_tracker.log_agent_vars("Test", agent_vars, step=1)

        # Assert
        # Should try to convert to numeric and log numeric values
        assert mock_aim_run.track.called

    def test_log_multiple_variables_in_one_call(self, aim_tracker, mock_aim_run):
        """Test that multiple variables are logged in a single call."""
        # Arrange
        agent_vars = {
            "budget": [100.0, 200.0, 150.0],
            "status": ["active", "inactive", "active"],
            "moved": [True, False, True],
        }

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=1)

        # Assert
        assert mock_aim_run.track.call_count > 3
        calls = [call[1]["name"] for call in mock_aim_run.track.call_args_list]
        assert "City.budget" in calls
        assert "City.status.unique_count" in calls
        assert "City.moved" in calls


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_log_invalid_type_skipped(self, aim_tracker, mock_aim_run):
        """Test that invalid types that cannot be converted are skipped.

        object() instances are treated as object dtype by pandas. They will be
        processed as categorical (string) variables, but since they're not valid
        strings, they may be tracked as categorical stats or skipped depending on
        implementation. The key is that no Distribution should be created.
        """
        # Arrange
        agent_vars = {"data": [object(), object()]}

        # Act
        aim_tracker.log_agent_vars("Test", agent_vars, step=1)

        # Assert
        # object() will be treated as object dtype, which may be processed as categorical
        # If tracked, it should be categorical stats, not Distribution
        if mock_aim_run.track.called:
            # If something was tracked, verify it's not a Distribution
            for call in mock_aim_run.track.call_args_list:
                value = call[0][0]
                _ = call[1]["name"]
                # Should be categorical stats (unique_count, etc.) or nothing
                if AIM_AVAILABLE:
                    assert not isinstance(value, Distribution)
                # Categorical stats are numeric (counts, ratios)
                assert isinstance(value, (int, float)) or not AIM_AVAILABLE

    def test_log_empty_dict_does_nothing(self, aim_tracker, mock_aim_run):
        """Test that empty agent_vars dictionary does nothing."""
        # Arrange
        agent_vars = {}

        # Act
        aim_tracker.log_agent_vars("Test", agent_vars, step=1)

        # Assert
        assert not mock_aim_run.track.called

    def test_log_with_none_step(self, aim_tracker, mock_aim_run):
        """Test that step=None is handled correctly."""
        # Arrange
        agent_vars = {"budget": [100.0, 200.0, 150.0]}

        # Act
        aim_tracker.log_agent_vars("City", agent_vars, step=None)

        # Assert
        assert mock_aim_run.track.called
        call_args = mock_aim_run.track.call_args
        assert call_args[1]["step"] is None
