#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Tests for analysis utilities module.

This module tests the functionality of ResultAnalyzer and ExpAnalyzer
for analyzing Hydra multirun experiment results.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pytest
import yaml
from omegaconf import DictConfig

from abses.utils.analysis import ExpAnalyzer, ResultAnalyzer

if TYPE_CHECKING:
    pass


@pytest.fixture
def temp_multirun_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure simulating Hydra multirun output.

    Args:
        tmp_path: Temporary directory provided by pytest.

    Returns:
        Path to the multirun directory.
    """
    multirun_dir = tmp_path / "multirun_output"
    multirun_dir.mkdir()

    # Create multirun.yaml
    multirun_config = {
        "hydra": {
            "overrides": {
                "task": [
                    "model.density=0.5,0.7,0.9",
                    "model.n_agents=10,20",
                ]
            }
        }
    }
    with open(multirun_dir / "multirun.yaml", "w", encoding="utf-8") as f:
        yaml.dump(multirun_config, f)

    # Create subdirectories for each run
    runs = [
        ("0_model.density=0.5_model.n_agents=10", {"density": 0.5, "n_agents": 10}),
        ("1_model.density=0.7_model.n_agents=10", {"density": 0.7, "n_agents": 10}),
        ("2_model.density=0.9_model.n_agents=10", {"density": 0.9, "n_agents": 10}),
        ("3_model.density=0.5_model.n_agents=20", {"density": 0.5, "n_agents": 20}),
        ("4_model.density=0.7_model.n_agents=20", {"density": 0.7, "n_agents": 20}),
        ("5_model.density=0.9_model.n_agents=20", {"density": 0.9, "n_agents": 20}),
    ]

    for run_name, config_values in runs:
        run_dir = multirun_dir / run_name
        run_dir.mkdir()

        # Create .hydra directory
        hydra_dir = run_dir / ".hydra"
        hydra_dir.mkdir()

        # Create config.yaml
        run_config = {
            "model": {
                "density": config_values["density"],
                "n_agents": config_values["n_agents"],
            },
            "reports": {
                "model": {"population": "n_agents"},
                "agents": {"City": {"wealth": "wealth"}},
                "final": {"final_population": "n_agents"},
            },
        }
        with open(hydra_dir / "config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(run_config, f)

        # Create CSV data file
        data = pd.DataFrame(
            {
                "Time": ["2020-01-01", "2020-01-02", "2020-01-03"],
                "province": ["A", "A", "A"],
                "surface": [100.0, 110.0, 120.0],
                "ground": [50.0, 55.0, 60.0],
                "quota": [80.0, 85.0, 90.0],
            }
        )
        data.to_csv(run_dir / "cities.csv", index=True)

    return multirun_dir


@pytest.fixture
def temp_single_run_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure for a single run.

    Args:
        tmp_path: Temporary directory provided by pytest.

    Returns:
        Path to the single run directory.
    """
    run_dir = tmp_path / "single_run"
    run_dir.mkdir()

    # Create .hydra directory
    hydra_dir = run_dir / ".hydra"
    hydra_dir.mkdir()

    # Create config.yaml
    run_config = {
        "model": {"density": 0.7, "n_agents": 50},
        "reports": {
            "model": {"population": "n_agents"},
            "final": {"final_population": "n_agents"},
        },
    }
    with open(hydra_dir / "config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(run_config, f)

    # Create CSV data file
    data = pd.DataFrame(
        {
            "Time": ["2020-01-01", "2020-01-02"],
            "province": ["A", "B"],
            "surface": [100.0, 200.0],
            "ground": [50.0, 100.0],
        }
    )
    data.to_csv(run_dir / "cities.csv", index=True)

    return run_dir


class TestBaseAnalyzer:
    """Tests for _BaseAnalyzer base class."""

    def test_path_property(self, temp_single_run_dir: Path) -> None:
        """Test path property getter and setter."""
        from abses.utils.analysis import _BaseAnalyzer

        analyzer = _BaseAnalyzer(temp_single_run_dir)
        assert analyzer.path == temp_single_run_dir
        assert isinstance(analyzer.path, Path)

        # Test setter with string
        analyzer.path = str(temp_single_run_dir)
        assert analyzer.path == temp_single_run_dir

    def test_config_property(self, temp_single_run_dir: Path) -> None:
        """Test config property loading."""
        from abses.utils.analysis import _BaseAnalyzer

        analyzer = _BaseAnalyzer(temp_single_run_dir)
        config_path = temp_single_run_dir / ".hydra" / "config.yaml"
        analyzer.config = config_path

        assert analyzer.config is not None
        assert isinstance(analyzer.config, DictConfig)

    def test_select_method(self, temp_single_run_dir: Path) -> None:
        """Test select method for configuration values."""
        from abses.utils.analysis import _BaseAnalyzer

        analyzer = _BaseAnalyzer(temp_single_run_dir)
        config_path = temp_single_run_dir / ".hydra" / "config.yaml"
        analyzer.config = config_path

        density = analyzer.select("model.density")
        assert density == 0.7

    def test_subdir_property(self, temp_multirun_dir: Path) -> None:
        """Test subdir property."""
        from abses.utils.analysis import _BaseAnalyzer

        analyzer = _BaseAnalyzer(temp_multirun_dir)
        subdirs = analyzer.subdir

        assert len(subdirs) == 6
        assert all(isinstance(d, Path) for d in subdirs)


class TestResultAnalyzer:
    """Tests for ResultAnalyzer class."""

    def test_initialization(self, temp_single_run_dir: Path) -> None:
        """Test ResultAnalyzer initialization."""
        analyzer = ResultAnalyzer(temp_single_run_dir)

        assert analyzer.path == temp_single_run_dir
        assert analyzer.config is not None
        assert isinstance(analyzer.data, pd.DataFrame)

    def test_initialization_invalid_path(self, tmp_path: Path) -> None:
        """Test ResultAnalyzer initialization with invalid path."""
        invalid_path = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            ResultAnalyzer(invalid_path)

    def test_read_data(self, temp_single_run_dir: Path) -> None:
        """Test data reading from CSV."""
        analyzer = ResultAnalyzer(temp_single_run_dir)

        assert not analyzer.data.empty
        assert "Time" in analyzer.data.columns
        assert "province" in analyzer.data.columns

    def test_read_csv(self, temp_single_run_dir: Path) -> None:
        """Test CSV reading method."""
        analyzer = ResultAnalyzer(temp_single_run_dir)
        csv_path = temp_single_run_dir / "cities.csv"

        data = analyzer.read_csv(csv_path)
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

    def test_get_data(self, temp_single_run_dir: Path) -> None:
        """Test get_data method."""
        analyzer = ResultAnalyzer(temp_single_run_dir)

        data = analyzer.get_data()
        assert isinstance(data, pd.DataFrame)
        assert not data.empty

    def test_select_config(self, temp_single_run_dir: Path) -> None:
        """Test configuration selection."""
        analyzer = ResultAnalyzer(temp_single_run_dir)

        density = analyzer.select("model.density")
        assert density == 0.7

        n_agents = analyzer.select("model.n_agents")
        assert n_agents == 50

    def test_reporter_extraction(self, temp_single_run_dir: Path) -> None:
        """Test reporter information extraction."""
        analyzer = ResultAnalyzer(temp_single_run_dir)

        assert hasattr(analyzer, "model_reporter")
        assert hasattr(analyzer, "agent_reporter")
        assert hasattr(analyzer, "final_reporter")


class TestExpAnalyzer:
    """Tests for ExpAnalyzer class."""

    def test_initialization(self, temp_multirun_dir: Path) -> None:
        """Test ExpAnalyzer initialization."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        assert analyzer.path == temp_multirun_dir
        assert analyzer.config is not None

    def test_overrides_property(self, temp_multirun_dir: Path) -> None:
        """Test overrides property parsing."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        overrides = analyzer.overrides
        assert "model.density" in overrides
        assert "model.n_agents" in overrides
        assert len(overrides["model.density"]) == 3
        assert len(overrides["model.n_agents"]) == 2

    def test_results_generator(self, temp_multirun_dir: Path) -> None:
        """Test results generator."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        results = list(analyzer.results)
        assert len(results) == 6
        assert all(isinstance(r, ResultAnalyzer) for r in results)

    def test_diff_runs(self, temp_multirun_dir: Path) -> None:
        """Test diff_runs property."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        diff = analyzer.diff_runs
        assert isinstance(diff, pd.DataFrame)
        # Should have columns for each override parameter
        assert "model.density" in diff.columns or len(diff) == 0

    def test_agg_data(self, temp_multirun_dir: Path) -> None:
        """Test aggregated data property."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        agg = analyzer.agg_data
        assert isinstance(agg, pd.DataFrame)
        # Should have data from all runs
        assert len(agg) > 0
        # Should have override columns
        assert "model.density" in agg.columns or len(agg) == 0

    def test_apply_method(self, temp_multirun_dir: Path) -> None:
        """Test apply method for custom functions."""
        analyzer = ExpAnalyzer(temp_multirun_dir)

        def get_data_length(result: ResultAnalyzer) -> int:
            """Get the length of data in a result."""
            return len(result.data)

        results = analyzer.apply(get_data_length)
        assert isinstance(results, pd.Series)
        assert len(results) == 6
        assert all(r > 0 for r in results if r is not None)

    def test_empty_multirun_dir(self, tmp_path: Path) -> None:
        """Test ExpAnalyzer with empty multirun directory."""
        empty_dir = tmp_path / "empty_multirun"
        empty_dir.mkdir()

        analyzer = ExpAnalyzer(empty_dir)

        # Should not raise error, but overrides should be empty
        assert analyzer.overrides == {}
        assert len(list(analyzer.results)) == 0
