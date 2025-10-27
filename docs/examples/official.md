# Official Examples

Built-in examples showcasing ABSESpy features for agent-based modeling.

## About These Examples

These examples demonstrate core ABSESpy features through classic ABM models.
Each includes complete source code, documentation, and tests.

## Available Examples

<div class="grid cards" markdown>

-   :fire: __Fire Spread__

    ---

    Demonstrates spatial modeling, raster attributes, and visualization.

    **Features**: `@raster_attribute`, `neighboring()`, `trigger()`

    [:octicons-arrow-right-24: Tutorial](../tutorial/completing/fire_tutorial.ipynb) ·
    [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/fire_spread)

-   :wolf: __Wolf-Sheep Predation__

    ---

    Agent lifecycle, movement, and ecological interactions.

    **Features**: `move.random()`, `at.agents`, `die()`, reproduction

    [:octicons-arrow-right-24: Tutorial](../tutorial/beginner/predation_tutorial.ipynb) ·
    [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/wolf_sheep)

-   :cityscape: __Schelling Segregation__

    ---

    Mesa framework integration and social dynamics modeling.

    **Features**: `shuffle_do()`, `self.p`, Mesa compatibility

    [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/schelling) ·
    [:octicons-book-24: README](https://github.com/SongshGeo/ABSESpy/blob/master/examples/schelling/README.md)

-   :chart_with_upwards_trend: __Hotelling's Law__

    ---

    Decision-making framework and spatial competition.

    **Features**: Links between Actors and PatchCells

    [:octicons-arrow-right-24: Tutorial](../tutorial/beginner/hotelling_tutorial.ipynb) ·
    [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/hotelling_law)

</div>

## Framework Advantages

These examples highlight how ABSESpy reduces development effort:

- **Spatial modeling made easy**: Built-in grid, raster attributes, neighbor queries
- **Agent lifecycle management**: Automatic handling of birth/death, movement
- **Mesa compatibility**: Use existing Mesa models with minimal changes
- **Type safety**: Full type hints for better IDE support
- **Testing support**: Comprehensive test utilities
