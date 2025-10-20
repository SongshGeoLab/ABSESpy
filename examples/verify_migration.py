#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Verification script for ABSESpy 0.7.x to 0.8.x migration.

This script tests common patterns from 0.7.x projects to ensure they work
correctly in 0.8.x. Run this script to verify your migration will be smooth.

Usage:
    python examples/verify_migration.py
"""

from omegaconf import DictConfig, OmegaConf

from abses import MainModel
from abses.core.experiment import Experiment


def test_basic_model_initialization() -> bool:
    """Test basic model initialization with minimal config.

    Returns:
        True if test passes, False otherwise.
    """
    print("✓ Testing basic model initialization...")
    try:
        config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
        model = MainModel(parameters=config)
        # Model name comes from settings, not from model.name
        assert model.settings.get("model", {}).get("name") == "test"
        print("  ✓ Basic initialization works!")
        return True
    except Exception as e:
        import traceback

        print(f"  ✗ Basic initialization failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False


def test_model_with_extra_params() -> bool:
    """Test model initialization with extra parameters (common 0.7.x pattern).

    Returns:
        True if test passes, False otherwise.
    """
    print("✓ Testing model with extra parameters...")
    try:
        config = DictConfig({"model": {"name": "test"}})
        model = MainModel(
            parameters=config,
            custom_param="custom_value",
            another_param=123,
        )
        assert model.settings.custom_param == "custom_value"
        assert model.settings.another_param == 123
        print("  ✓ Extra parameters work!")
        return True
    except Exception as e:
        print(f"  ✗ Extra parameters failed: {e}")
        return False


def test_structured_config_modification() -> bool:
    """Test that structured configs can be modified (0.7.x behavior).

    Returns:
        True if test passes, False otherwise.
    """
    print("✓ Testing structured config modification...")
    try:
        config = OmegaConf.create({"model": {"name": "test"}})
        OmegaConf.set_struct(config, True)  # Make it structured

        # Create experiment - should disable struct mode automatically
        exp = Experiment(model_cls=MainModel, cfg=config)

        # Should be able to add new keys
        exp.cfg.new_key = "new_value"
        assert exp.cfg.new_key == "new_value"
        print("  ✓ Structured config modification works!")
        return True
    except Exception as e:
        print(f"  ✗ Structured config modification failed: {e}")
        return False


def test_missing_config_sections() -> bool:
    """Test that missing config sections don't break (uses defaults).

    Returns:
        True if test passes, False otherwise.
    """
    print("✓ Testing missing config sections...")
    try:
        # Config without 'exp' section
        config = OmegaConf.create(
            {
                "hydra": {
                    "job": {"name": "${oc.select:exp.name,ABSESpy}"},
                    "run": {
                        "dir": "${oc.select:exp.outdir,out}/${oc.select:exp.name,ABSESpy}"
                    },
                }
            }
        )

        # Should resolve to default values
        resolved = OmegaConf.to_container(config, resolve=True)
        assert resolved["hydra"]["job"]["name"] == "ABSESpy"
        assert resolved["hydra"]["run"]["dir"] == "out/ABSESpy"
        print("  ✓ Missing config sections handled correctly!")
        return True
    except Exception as e:
        print(f"  ✗ Missing config sections failed: {e}")
        return False


def test_partial_config_sections() -> bool:
    """Test that partial config sections work correctly.

    Returns:
        True if test passes, False otherwise.
    """
    print("✓ Testing partial config sections...")
    try:
        # Config with only exp.name but not exp.outdir
        config = OmegaConf.create(
            {
                "exp": {"name": "MyProject"},
                "hydra": {
                    "run": {
                        "dir": "${oc.select:exp.outdir,out}/${oc.select:exp.name,ABSESpy}"
                    }
                },
            }
        )

        resolved = OmegaConf.to_container(config, resolve=True)
        assert resolved["hydra"]["run"]["dir"] == "out/MyProject"
        print("  ✓ Partial config sections handled correctly!")
        return True
    except Exception as e:
        print(f"  ✗ Partial config sections failed: {e}")
        return False


def main() -> None:
    """Run all migration verification tests.

    Prints a summary of test results and indicates if migration will be smooth.
    """
    print("\n" + "=" * 60)
    print("ABSESpy 0.7.x to 0.8.x Migration Verification")
    print("=" * 60 + "\n")

    tests = [
        test_basic_model_initialization,
        test_model_with_extra_params,
        test_structured_config_modification,
        test_missing_config_sections,
        test_partial_config_sections,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60 + "\n")

    if all(results):
        print("✅ All tests passed! Your migration should be smooth.")
        print("   Your 0.7.x project should work with 0.8.x without changes.\n")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   You may need to update your configuration or code.\n")
        print("   Please report any issues at:")
        print("   https://github.com/ABSESpy/ABSESpy/issues\n")


if __name__ == "__main__":
    main()
