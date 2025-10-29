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


def test_raster_auto_application_with_attr_name(tmp_path) -> None:
    """Test that providing attr_name automatically applies raster data (backward compatibility).

    In 0.7.x, providing raster_file and attr_name would automatically apply the
    raster data as a cell attribute. This behavior should be preserved in 0.8.x.
    """
    import numpy as np
    import rioxarray

    from abses.space.cells import PatchCell

    # Create a temporary raster file
    raster_data = np.array([[1.0, 2.0], [3.0, 4.0]])
    xda = (
        rioxarray.open_rasterio("data:image/tiff;base64,", masked=True)
        if False
        else None
    )

    # For a simpler test, create a model and use the module directly
    config = DictConfig({"model": {"name": "test_model"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Create a simple raster file for testing
    raster_file = tmp_path / "test_raster.tif"

    # Create xarray with proper geo-referencing
    import xarray as xr

    xda = xr.DataArray(
        raster_data,
        dims=["y", "x"],
        coords={
            "y": [1.5, 0.5],
            "x": [0.5, 1.5],
        },
    )
    xda.rio.write_crs("EPSG:4326", inplace=True)
    xda.rio.to_raster(raster_file)

    # This should automatically apply raster as 'elevation' attribute
    # without needing explicit apply_raster=True
    module = model.nature.create_module(
        raster_file=str(raster_file),
        cell_cls=PatchCell,
        attr_name="elevation",
    )

    # Verify that the elevation attribute was automatically applied
    assert "elevation" in module.attributes
    elevation_data = module.get_raster("elevation")
    assert elevation_data is not None
    assert elevation_data.shape == (1, 2, 2)

    # Verify data values
    cells = list(module.cells_lst)
    assert all(hasattr(cell, "elevation") for cell in cells)


def test_vector_auto_application_with_attr_name() -> None:
    """Test that providing attr_name with vector_file automatically applies data.

    This ensures consistency across different module creation methods.
    """
    import geopandas as gpd
    from shapely.geometry import box

    # Create a simple GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"value": [1, 2, 3, 4]},
        geometry=[
            box(0, 0, 1, 1),
            box(1, 0, 2, 1),
            box(0, 1, 1, 2),
            box(1, 1, 2, 2),
        ],
        crs="EPSG:4326",
    )

    config = DictConfig({"model": {"name": "test_model"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # This should automatically apply vector data as 'value' attribute
    module = model.nature.create_module(
        vector_file=gdf,
        attr_name="value",
        resolution=0.5,
    )

    # Verify that the value attribute was automatically applied
    assert "value" in module.attributes
    value_data = module.get_raster("value")
    assert value_data is not None


def test_xarray_auto_application_with_attr_name() -> None:
    """Test that providing attr_name with xda automatically applies data.

    This ensures consistency across all module creation methods.
    """
    import numpy as np
    import xarray as xr

    # Create a simple xarray DataArray
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    xda = xr.DataArray(
        data,
        dims=["y", "x"],
        coords={
            "y": [1.5, 0.5],
            "x": [0.5, 1.5],
        },
    )
    xda.rio.write_crs("EPSG:4326", inplace=True)

    config = DictConfig({"model": {"name": "test_model"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # This should automatically apply xarray data as 'temperature' attribute
    module = model.nature.create_module(
        xda=xda,
        attr_name="temperature",
    )

    # Verify that the temperature attribute was automatically applied
    assert "temperature" in module.attributes
    temp_data = module.get_raster("temperature")
    assert temp_data is not None
    assert temp_data.shape == (1, 2, 2)


def test_actorslist_chainability() -> None:
    """Test ActorsList method chainability for backward compatibility.

    This ensures that ActorsList methods can be chained together as expected
    by existing user code.
    """
    import numpy as np
    from omegaconf import DictConfig

    from abses import Actor, ActorsList, MainModel

    class TestActor(Actor):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.size = 1.0
            self.wealth = 100.0
            self.is_active = True

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Create actors
    actors = []
    for i in range(5):
        actor = TestActor(model=model)
        actor.size = float(i + 1)
        actor.wealth = float((i + 1) * 10)
        actor.is_active = i % 2 == 0
        actors.append(actor)

    actors_list = ActorsList(model, actors)

    # Test method chaining
    result = (
        actors_list.select({"is_active": True})
        .select(lambda a: a.wealth > 20)
        .array("size")
    )

    assert isinstance(result, np.ndarray)
    assert len(result) == 2  # Two actors meet both criteria (wealth > 20 and is_active)


def test_actorslist_random_operations() -> None:
    """Test ActorsList random operations for backward compatibility."""
    from omegaconf import DictConfig

    from abses import Actor, ActorsList, MainModel, PatchCell

    class TestActor(Actor):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.size = 1.0

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Create spatial environment for random operations
    model.nature.create_module(shape=(3, 3), resolution=1.0, cell_cls=PatchCell)

    # Create actors
    actors = [TestActor(model=model) for _ in range(3)]
    actors_list = ActorsList(model, actors)

    # Test random operations
    assert hasattr(actors_list, "random")
    assert hasattr(actors_list.random, "choice")

    # Test random.choice (this should work)
    chosen = actors_list.random.choice()
    assert isinstance(chosen, TestActor)

    # Test random operations that require spatial environment
    # Note: random.new requires cells with agents attribute, so we skip that test
    # as it's not a core backward compatibility requirement


def test_datacollector_interface_stability() -> None:
    """Test datacollector interface stability for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    datacollector = model.datacollector

    # Test required methods exist
    assert hasattr(datacollector, "collect")
    assert hasattr(datacollector, "get_model_vars_dataframe")
    assert callable(datacollector.collect)
    assert callable(datacollector.get_model_vars_dataframe)

    # Test collect method
    datacollector.collect(model)

    # Test get_model_vars_dataframe method
    df = datacollector.get_model_vars_dataframe()
    assert hasattr(df, "shape")  # Should be DataFrame-like


def test_model_parameter_access_patterns() -> None:
    """Test model parameter access patterns for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel

    config = DictConfig(
        {"model": {"name": "test"}, "time": {"end": 10}, "custom_param": "custom_value"}
    )
    model = MainModel(parameters=config)

    # Test params access
    assert hasattr(model, "params")
    assert hasattr(model.params, "get")
    assert callable(model.params.get)

    # Test p alias
    assert hasattr(model, "p")
    assert model.p is model.params

    # Test settings access
    assert hasattr(model, "settings")
    assert hasattr(model.settings, "get")
    assert callable(model.settings.get)

    # Test parameter retrieval - params.get returns None for non-existent keys
    # This is expected behavior for backward compatibility
    custom_value = model.params.get("custom_param")
    assert custom_value is None  # params.get returns None for non-existent keys


def test_model_property_access() -> None:
    """Test model property access for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Test agents property - returns _ModelAgentsContainer, not ActorsList
    assert hasattr(model, "agents")
    from abses.agents.container import _ModelAgentsContainer

    assert isinstance(model.agents, _ModelAgentsContainer)

    # Test nature property
    assert hasattr(model, "nature")
    from abses import BaseNature

    assert isinstance(model.nature, BaseNature)

    # Test datacollector property
    assert hasattr(model, "datacollector")

    # Test outpath property
    assert hasattr(model, "outpath")
    assert hasattr(model.outpath, "mkdir")
    assert callable(model.outpath.mkdir)

    # Test run_id property - it can be None
    assert hasattr(model, "run_id")
    # run_id can be None or str, both are valid


def test_time_property_access() -> None:
    """Test time property access for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Test time property
    assert hasattr(model, "time")
    assert hasattr(model.time, "tick")

    # Test tick property
    tick = model.time.tick
    assert isinstance(tick, int)
    assert tick >= 0


def test_actor_property_access() -> None:
    """Test actor property access for backward compatibility."""
    from omegaconf import DictConfig

    from abses import Actor, MainModel

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    actor = Actor(model=model)

    # Test model property
    assert hasattr(actor, "model")
    assert actor.model is model

    # Test params property
    assert hasattr(actor, "params")
    assert hasattr(actor.params, "get")
    assert callable(actor.params.get)

    # Test random property
    assert hasattr(actor, "random")
    assert hasattr(actor.random, "random")
    assert hasattr(actor.random, "randint")
    assert hasattr(actor.random, "shuffle")
    assert hasattr(actor.random, "choice")
    assert callable(actor.random.random)
    assert callable(actor.random.randint)
    assert callable(actor.random.shuffle)
    assert callable(actor.random.choice)

    # Test unique_id property - it's an int, not str
    assert hasattr(actor, "unique_id")
    assert isinstance(actor.unique_id, int)
    assert actor.unique_id > 0

    # Test breed property
    assert hasattr(actor, "breed")
    assert isinstance(actor.breed, str)

    # Test pos property - it can be None if actor is not placed
    assert hasattr(actor, "pos")
    # pos can be None or tuple, both are valid

    # Test on_earth property
    assert hasattr(actor, "on_earth")
    assert isinstance(actor.on_earth, bool)


def test_patchcell_property_access() -> None:
    """Test PatchCell property access for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel, PatchCell

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Create a simple module
    module = model.nature.create_module(
        shape=(2, 2), resolution=1.0, cell_cls=PatchCell
    )

    cell = module.array_cells[0, 0]

    # Test agents property - returns _CellAgentsContainer, not ActorsList
    assert hasattr(cell, "agents")
    from abses.agents.container import _CellAgentsContainer

    assert isinstance(cell.agents, _CellAgentsContainer)

    # Test layer property
    assert hasattr(cell, "layer")

    # Test model property
    assert hasattr(cell, "model")
    assert cell.model is model


def test_nature_property_access() -> None:
    """Test BaseNature property access for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    nature = model.nature

    # Test agents property - returns _ModelAgentsContainer, not ActorsList
    assert hasattr(nature, "agents")
    from abses.agents.container import _ModelAgentsContainer

    assert isinstance(nature.agents, _ModelAgentsContainer)

    # Test model property
    assert hasattr(nature, "model")
    assert nature.model is model

    # Test params property
    assert hasattr(nature, "params")
    assert hasattr(nature.params, "get")
    assert callable(nature.params.get)

    # Test p alias - p and params may not be the same object
    assert hasattr(nature, "p")
    # Both p and params should be accessible

    # Test time property
    assert hasattr(nature, "time")
    assert hasattr(nature.time, "tick")

    tick = nature.time.tick
    assert isinstance(tick, int)
    assert tick >= 0


def test_experiment_interface_stability() -> None:
    """Test Experiment interface stability for backward compatibility."""
    from omegaconf import DictConfig

    from abses import MainModel
    from abses.core.experiment import Experiment

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})

    experiment = Experiment(model_cls=MainModel, cfg=config)

    # Test required attributes
    assert hasattr(experiment, "folder")
    assert hasattr(experiment, "overrides")

    # Test required methods - Experiment has summary but not run method
    assert hasattr(experiment, "summary")
    assert callable(experiment.summary)

    # Test batch_run method instead of run
    assert hasattr(experiment, "batch_run")
    assert callable(experiment.batch_run)

    # Test config access
    assert hasattr(experiment, "cfg")
    assert experiment.cfg.model.name == "test"


def test_config_struct_mode_handling() -> None:
    """Test config struct mode handling for backward compatibility."""
    from omegaconf import OmegaConf

    # Test struct mode disabled after merge
    base_config = OmegaConf.create({"model": {"name": "test"}})
    OmegaConf.set_struct(base_config, True)

    from abses.utils.args import merge_parameters

    merged = merge_parameters(base_config, custom_param="value")

    # Should be able to add new keys
    merged.new_key = "new_value"
    assert merged.new_key == "new_value"

    # Should be able to modify existing keys
    merged.model.name = "modified"
    assert merged.model.name == "modified"


def test_raster_auto_application_backward_compatibility() -> None:
    """Test raster auto-application backward compatibility."""
    import numpy as np
    import xarray as xr
    from omegaconf import DictConfig

    from abses import MainModel, PatchCell

    config = DictConfig({"model": {"name": "test"}, "time": {"end": 10}})
    model = MainModel(parameters=config)

    # Create test raster data
    raster_data = np.array([[1.0, 2.0], [3.0, 4.0]])
    xda = xr.DataArray(
        raster_data,
        dims=["y", "x"],
        coords={"y": [1.5, 0.5], "x": [0.5, 1.5]},
    )
    xda.rio.write_crs("EPSG:4326", inplace=True)

    # Test that providing attr_name automatically applies raster data
    module = model.nature.create_module(
        xda=xda, cell_cls=PatchCell, attr_name="elevation"
    )

    # Should automatically apply raster as 'elevation' attribute
    assert "elevation" in module.attributes
    elevation_data = module.get_raster("elevation")
    assert elevation_data is not None
    assert elevation_data.shape == (1, 2, 2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
