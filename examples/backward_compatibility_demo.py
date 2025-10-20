#!/usr/bin/env python3
# -*-coding:utf-8 -*-
"""
Demonstration of backward compatibility for Actor parameter extraction.

This script demonstrates that Actor can now access parameters using both:
- PascalCase keys (0.8.0+ style): 'Farmer'
- lowercase keys (0.7.x style): 'farmer'
"""

import warnings

from omegaconf import DictConfig

from abses import MainModel
from abses.agents import Actor


class Farmer(Actor):
    """Example farmer actor."""

    def setup(self) -> None:
        """Setup farmer with parameters from config."""
        self.capital = self.params.get("initial_capital", 0)
        self.risk_aversion = self.p.get("risk_aversion", 0.0)
        print(
            f"  Farmer {self.unique_id}: capital={self.capital}, risk={self.risk_aversion}"
        )


class Trader(Actor):
    """Example trader actor."""

    def setup(self) -> None:
        """Setup trader with parameters from config."""
        self.goods = self.params.get("initial_goods", 0)
        print(f"  Trader {self.unique_id}: goods={self.goods}")


def demo_pascalcase_style() -> None:
    """Demo using PascalCase (0.8.0+ style)."""
    print("\n" + "=" * 60)
    print("Demo 1: PascalCase Style (0.8.0+)")
    print("=" * 60)

    config = DictConfig(
        {
            "Farmer": {"initial_capital": 1000, "risk_aversion": 0.5},
            "Trader": {"initial_goods": 50},
        }
    )

    print("\nConfiguration:")
    print("Farmer:  # ← PascalCase")
    print("  initial_capital: 1000")
    print("  risk_aversion: 0.5")
    print("Trader:  # ← PascalCase")
    print("  initial_goods: 50")

    model = MainModel(parameters=config)

    print("\nCreating actors...")
    farmers = model.agents.new(Farmer, 2)
    traders = model.agents.new(Trader, 1)

    print(
        f"\n✅ Successfully created {len(farmers)} farmers and {len(traders)} traders"
    )
    print("   No deprecation warnings (using recommended style)")


def demo_lowercase_style() -> None:
    """Demo using lowercase (0.7.x style) - backward compatibility."""
    print("\n" + "=" * 60)
    print("Demo 2: Lowercase Style (0.7.x - Backward Compatible)")
    print("=" * 60)

    config = DictConfig(
        {
            "farmer": {  # lowercase!
                "initial_capital": 2000,
                "risk_aversion": 0.3,
            },
            "trader": {  # lowercase!
                "initial_goods": 100
            },
        }
    )

    print("\nConfiguration:")
    print("farmer:  # ← lowercase")
    print("  initial_capital: 2000")
    print("  risk_aversion: 0.3")
    print("trader:  # ← lowercase")
    print("  initial_goods: 100")

    print("\n⚠️  Capturing deprecation warnings...")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Ensure warnings are captured

        model = MainModel(parameters=config)

        print("\nCreating actors...")
        farmers = model.agents.new(Farmer, 2)
        traders = model.agents.new(Trader, 1)

        print(
            f"\n✅ Successfully created {len(farmers)} farmers and {len(traders)} traders"
        )
        print("   (Parameters loaded from lowercase keys for backward compatibility)")

        # Display captured warnings
        if w:
            print(f"\n⚠️  {len(w)} Deprecation Warning(s) issued:")
            for warning in w:
                if issubclass(warning.category, DeprecationWarning):
                    print(f"\n   {warning.message}")


def demo_priority() -> None:
    """Demo that PascalCase takes priority over lowercase."""
    print("\n" + "=" * 60)
    print("Demo 3: Priority Test (PascalCase > lowercase)")
    print("=" * 60)

    config = DictConfig(
        {
            "Farmer": {  # PascalCase
                "initial_capital": 1000,
                "risk_aversion": 0.5,
            },
            "farmer": {  # lowercase
                "initial_capital": 2000,  # This will be ignored
                "risk_aversion": 0.3,  # This will be ignored
            },
        }
    )

    print("\nConfiguration (both keys present):")
    print("Farmer:  # ← PascalCase (will be used)")
    print("  initial_capital: 1000")
    print("  risk_aversion: 0.5")
    print("farmer:  # ← lowercase (will be ignored)")
    print("  initial_capital: 2000")
    print("  risk_aversion: 0.3")

    model = MainModel(parameters=config)

    print("\nCreating actors...")
    farmers = model.agents.new(Farmer, 1)

    print("\n✅ PascalCase parameters took priority:")
    print(f"   capital={farmers[0].capital} (should be 1000, not 2000)")
    print(f"   risk={farmers[0].risk_aversion} (should be 0.5, not 0.3)")
    print("   No deprecation warnings (PascalCase is used)")


def demo_mixed_styles() -> None:
    """Demo mixed styles in the same config."""
    print("\n" + "=" * 60)
    print("Demo 4: Mixed Styles (for migration scenarios)")
    print("=" * 60)

    config = DictConfig(
        {
            "Farmer": {  # PascalCase for Farmer
                "initial_capital": 1000,
                "risk_aversion": 0.5,
            },
            "trader": {  # lowercase for Trader
                "initial_goods": 50
            },
        }
    )

    print("\nConfiguration (mixed styles):")
    print("Farmer:  # ← PascalCase")
    print("  initial_capital: 1000")
    print("  risk_aversion: 0.5")
    print("trader:  # ← lowercase")
    print("  initial_goods: 50")

    print("\n⚠️  Capturing deprecation warnings...")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        model = MainModel(parameters=config)

        print("\nCreating actors...")
        _farmers = model.agents.new(Farmer, 1)
        _traders = model.agents.new(Trader, 1)

        print("\n✅ Both styles work together:")
        print("   Farmer uses PascalCase config (no warning)")
        print("   Trader uses lowercase config (with warning)")

        # Display warnings for trader only
        if w:
            print(f"\n⚠️  {len(w)} Deprecation Warning(s) for lowercase usage:")
            for warning in w:
                if issubclass(warning.category, DeprecationWarning):
                    print(f"   {warning.message}")


def demo_empty_fallback() -> None:
    """Demo fallback when PascalCase config is empty."""
    print("\n" + "=" * 60)
    print("Demo 5: Empty PascalCase Falls Back to Lowercase")
    print("=" * 60)

    config = DictConfig(
        {
            "Farmer": {},  # Empty!
            "farmer": {  # Has values
                "initial_capital": 3000,
                "risk_aversion": 0.7,
            },
        }
    )

    print("\nConfiguration:")
    print("Farmer: {}  # ← Empty PascalCase")
    print("farmer:     # ← Has values")
    print("  initial_capital: 3000")
    print("  risk_aversion: 0.7")

    print("\n⚠️  Capturing deprecation warnings...")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        model = MainModel(parameters=config)

        print("\nCreating actors...")
        farmers = model.agents.new(Farmer, 1)

        print("\n✅ Fell back to lowercase config:")
        print(f"   capital={farmers[0].capital} (should be 3000)")
        print(f"   risk={farmers[0].risk_aversion} (should be 0.7)")

        if w:
            print("\n⚠️  Deprecation warning issued for fallback:")
            for warning in w:
                if issubclass(warning.category, DeprecationWarning):
                    print(f"   {warning.message}")


def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 60)
    print("ABSESpy 0.8.0: Actor Parameter Backward Compatibility")
    print("=" * 60)
    print("\nThis demo shows that Actor parameters now support:")
    print("  • PascalCase keys (e.g., 'Farmer') - NEW in 0.8.0")
    print("  • lowercase keys (e.g., 'farmer') - Compatible with 0.7.x")
    print("\nYou can use either style, or mix them during migration!")

    try:
        demo_pascalcase_style()
        demo_lowercase_style()
        demo_priority()
        demo_mixed_styles()
        demo_empty_fallback()

        print("\n" + "=" * 60)
        print("All demos completed successfully! ✅")
        print("=" * 60)
        print("\n📝 Summary:")
        print("  1. PascalCase (e.g., 'Farmer') is the recommended style for 0.8.0+")
        print("  2. lowercase (e.g., 'farmer') still works for backward compatibility")
        print("  3. Using lowercase triggers a DeprecationWarning")
        print("  4. If both exist, PascalCase takes priority")
        print("  5. You can mix styles during code migration")
        print("\n⚠️  Recommendation:")
        print("  • New projects: Use PascalCase")
        print("  • Existing projects: Migrate to PascalCase before v1.0.0")
        print("  • The lowercase support will be removed in a future version")
        print("\n🚀 Your existing 0.7.x configs will continue to work!")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
