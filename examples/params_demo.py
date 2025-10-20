#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Demonstration of parameter extraction mechanism in ABSESpy.

This example shows how different components access their parameters.
"""

from omegaconf import DictConfig

from abses import MainModel
from abses.agents import Actor
from abses.human import BaseHuman, HumanModule
from abses.space import BaseNature, PatchModule


def create_demo_config() -> DictConfig:
    """Create a demo configuration.

    Returns:
        Demo configuration with parameters for all components.
    """
    return DictConfig(
        {
            # Model global parameters
            "model": {"name": "params_demo", "timeout": 100, "max_steps": 50},
            # Datasets configuration
            "ds": {
                "population": "data/population.csv",
                "landuse": "data/landuse.tif",
            },
            # Nature subsystem parameters
            "nature": {"crs": "EPSG:4326", "resolution": 100},
            # Human subsystem parameters
            "human": {"population": 1000, "initial_wealth": 100},
            # PatchModule (layer) parameters
            "farmland": {
                "nodata": -9999,
                "resolution": 30,
                "crop_types": ["wheat", "corn", "rice"],
            },
            # HumanModule parameters
            "farmers_group": {"skill_level": 5, "experience": 10},
            # Actor type parameters (0.8.0+ style - PascalCase)
            "Farmer": {
                "initial_capital": 1000,
                "risk_aversion": 0.5,
                "max_farm_size": 100,
            },
            # Also supports lowercase for backward compatibility (0.7.x style)
            # "farmer": { ... }  # This would also work!
        }
    )


class DemoNature(BaseNature):
    """Demo nature subsystem to show parameter access."""

    def setup(self) -> None:
        """Setup nature subsystem and show parameter access."""
        print("\n=== Nature Subsystem Parameters ===")
        print(f"Nature CRS: {self.params.crs}")
        print(f"Nature resolution: {self.p.resolution}")

        # Access model parameters from subsystem
        print(f"Model timeout (from nature): {self.model.params.timeout}")

        # Access datasets
        print(f"Landuse dataset: {self.datasets.landuse}")


class DemoHuman(BaseHuman):
    """Demo human subsystem to show parameter access."""

    def setup(self) -> None:
        """Setup human subsystem and show parameter access."""
        print("\n=== Human Subsystem Parameters ===")
        print(f"Human population: {self.params.population}")
        print(f"Human initial wealth: {self.p.initial_wealth}")

        # Access model parameters
        print(f"Model max steps (from human): {self.model.params.max_steps}")


class DemoPatchModule(PatchModule):
    """Demo patch module to show parameter access."""

    def setup(self) -> None:
        """Setup patch module and show parameter access."""
        print("\n=== PatchModule Parameters ===")
        print(f"Layer nodata: {self.params.nodata}")
        print(f"Layer resolution: {self.p.resolution}")
        print(f"Crop types: {self.params.crop_types}")

        # Access parent subsystem parameters
        print(f"Nature CRS (from layer): {self.model.nature.params.crs}")


class DemoHumanModule(HumanModule):
    """Demo human module to show parameter access."""

    def setup(self) -> None:
        """Setup human module and show parameter access."""
        print("\n=== HumanModule Parameters ===")
        print(f"Module skill level: {self.params.skill_level}")
        print(f"Module experience: {self.p.experience}")

        # Access parent subsystem parameters
        print(f"Human population (from module): {self.model.human.params.population}")


class Farmer(Actor):
    """Demo actor to show parameter access."""

    def setup(self) -> None:
        """Setup actor and show parameter access."""
        # Access actor type parameters
        self.capital = self.params.initial_capital
        self.risk_aversion = self.p.risk_aversion
        self.max_farm_size = self.params.max_farm_size


def demo_parameter_access() -> None:
    """Demonstrate parameter access in different components."""
    print("=" * 60)
    print("ABSESpy Parameter Extraction Mechanism Demo")
    print("=" * 60)

    # Create configuration
    config = create_demo_config()

    # Create model with additional kwargs (will be merged)
    model = MainModel(
        parameters=config,
        human_class=DemoHuman,
        nature_class=DemoNature,
        **{"model.runtime_param": "added_at_runtime"},
    )

    print("\n=== Model Level Parameters ===")
    print(f"Model name: {model.name}")
    print(f"Model timeout: {model.params.timeout}")
    print(f"Model max steps: {model.p.max_steps}")
    print(f"Runtime param: {model.params.runtime_param}")  # From kwargs

    print("\n=== Dataset Access ===")
    print(f"Population dataset: {model.datasets.population}")
    print(f"Landuse dataset: {model.ds.landuse}")  # Using alias

    print("\n=== Direct Subsystem Access ===")
    print(f"Nature CRS: {model.nature.params.crs}")
    print(f"Human population: {model.human.p.population}")

    # Create a layer (PatchModule)
    print("\n" + "=" * 60)
    print("Creating PatchModule...")
    print("=" * 60)
    farmland = model.nature.create_module(name="farmland", module_cls=DemoPatchModule)

    # Create a human module
    print("\n" + "=" * 60)
    print("Creating HumanModule...")
    print("=" * 60)
    _farmers_group = model.human.create_module(
        name="farmers_group", module_cls=DemoHumanModule
    )

    # Create actors
    print("\n" + "=" * 60)
    print("Creating Actors...")
    print("=" * 60)
    farmers = model.agents.new(Farmer, 3)

    print("\n=== Actor Parameters ===")
    for i, farmer in enumerate(farmers):
        print(f"\nFarmer {i}:")
        print(f"  Capital: {farmer.capital}")
        print(f"  Risk aversion: {farmer.risk_aversion}")
        print(f"  Max farm size: {farmer.max_farm_size}")

    # Demonstrate parameter access patterns
    print("\n" + "=" * 60)
    print("Parameter Access Patterns Summary")
    print("=" * 60)

    print("\n1. Component accesses own parameters:")
    print(f"   model.params.timeout = {model.params.timeout}")
    print(f"   nature.params.crs = {model.nature.params.crs}")
    print(f"   farmland.params.nodata = {farmland.params.nodata}")

    print("\n2. Component accesses parent parameters:")
    print(f"   farmland.model.params.timeout = {farmland.model.params.timeout}")
    print(f"   farmer.model.nature.params.crs = {farmers[0].model.nature.params.crs}")

    print("\n3. Using aliases (p for params, ds for datasets):")
    print(f"   model.p.max_steps = {model.p.max_steps}")
    print(f"   nature.p.resolution = {model.nature.p.resolution}")
    print(f"   model.ds.population = {model.ds.population}")

    print("\n4. All components share the same settings tree:")
    print(f"   model.settings.nature.crs = {model.settings.nature.crs}")
    print(
        f"   nature.model.settings.nature.crs = {model.nature.model.settings.nature.crs}"
    )
    print("   (They are the same object)")

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    demo_parameter_access()
