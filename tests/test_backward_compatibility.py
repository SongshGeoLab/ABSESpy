#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""Test backward compatibility with ABSESpy < 0.8.x projects.

This test module ensures that projects using older ABSESpy versions
can still work with the new version without breaking changes.
"""

from typing import TYPE_CHECKING

import pytest
from omegaconf import DictConfig, OmegaConf

from abses import MainModel
from abses.utils.args import merge_parameters

if TYPE_CHECKING:
    pass


def test_merge_parameters_with_new_keys() -> None:
    """Test that merge_parameters allows adding new keys not in original config.

    This is essential for backward compatibility with projects that pass
    additional parameters like 'nature_cls' or 'human_cls' to the model.
    """
    # Create a structured config (simulating Hydra-loaded config)
    base_config = OmegaConf.create({"model": {"name": "test"}})
    OmegaConf.set_struct(base_config, True)

    # This should not raise an error even though 'nature_cls' is not in base_config
    merged = merge_parameters(
        base_config, nature_cls="CustomNature", human_cls="CustomHuman"
    )

    assert merged.nature_cls == "CustomNature"
    assert merged.human_cls == "CustomHuman"
    assert merged.model.name == "test"


def test_merge_parameters_preserves_struct_disabled() -> None:
    """Test that merged config keeps struct mode disabled.

    This ensures that further modifications to the config are possible,
    which is important for dynamic model configuration.
    """
    base_config = OmegaConf.create({"param1": "value1"})
    OmegaConf.set_struct(base_config, True)

    merged = merge_parameters(base_config, param2="value2")

    # Should be able to add new keys directly
    merged.param3 = "value3"
    assert merged.param3 == "value3"


def test_model_initialization_with_extra_kwargs() -> None:
    """Test that MainModel can be initialized with extra kwargs.

    This simulates the common pattern in older projects where users
    pass custom parameters to the model constructor.
    """
    config = DictConfig({"model": {"name": "test_model"}, "time": {"end": 10}})

    # This should not raise an error
    model = MainModel(parameters=config, custom_param="custom_value", another_param=123)

    # Extra kwargs should be merged into settings
    assert model.settings.custom_param == "custom_value"
    assert model.settings.another_param == 123


def test_config_without_exp_section() -> None:
    """Test that config without 'exp' section doesn't break.

    Older projects might not have the 'exp' section in their config,
    so the default.yaml should handle this gracefully with oc.select.
    """
    # Create a config without 'exp' section, testing only the oc.select resolver
    config = OmegaConf.create(
        {
            "hydra": {
                "job": {"name": "${oc.select:exp.name,ABSESpy}"},
                "run": {
                    # Use a simpler path without 'now' resolver which requires Hydra context
                    "dir": "${oc.select:exp.outdir,out}/${oc.select:exp.name,ABSESpy}"
                },
            }
        }
    )

    # This should resolve to default values without error
    resolved = OmegaConf.to_container(config, resolve=True)
    assert isinstance(resolved, dict)
    assert resolved["hydra"]["job"]["name"] == "ABSESpy"
    assert resolved["hydra"]["run"]["dir"] == "out/ABSESpy"


def test_config_with_partial_exp_section() -> None:
    """Test that config with partial 'exp' section works correctly.

    Some projects might have 'exp.name' but not 'exp.outdir', or vice versa.
    """
    config = OmegaConf.create(
        {
            "exp": {
                "name": "MyProject"
                # Note: outdir is missing
            },
            "hydra": {
                "job": {"name": "${oc.select:exp.name,ABSESpy}"},
                "run": {
                    "dir": "${oc.select:exp.outdir,out}/${oc.select:exp.name,ABSESpy}"
                },
            },
        }
    )

    resolved = OmegaConf.to_container(config, resolve=True)
    assert isinstance(resolved, dict)
    # Should use custom name but default outdir
    assert resolved["hydra"]["job"]["name"] == "MyProject"
    assert resolved["hydra"]["run"]["dir"] == "out/MyProject"


def test_struct_mode_disabled_in_loaded_config() -> None:
    """Test that struct mode is properly disabled when config is loaded.

    This ensures that the Experiment class properly handles struct mode
    for backward compatibility.
    """
    from abses.core.experiment import Experiment

    # Create a structured config
    config = OmegaConf.create({"model": {"name": "test"}})
    OmegaConf.set_struct(config, True)

    # Create experiment with this config
    exp = Experiment(model_cls=MainModel, cfg=config)

    # The experiment's config should have struct mode disabled
    # so we can add new keys
    exp.cfg.new_key = "new_value"
    assert exp.cfg.new_key == "new_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
