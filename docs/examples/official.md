# Official Examples

Built-in examples showcasing ABSESpy features for agent-based modeling.

=== "English"

    ## About These Examples

    These examples demonstrate core ABSESpy features through classic ABM models.
    Each includes complete source code, documentation, and tests.

    ## Available Examples

    <div class="grid cards" markdown>

    - :fire: __Fire Spread__

      ---

      Demonstrates spatial modeling, raster attributes, and visualization.

      **Features**: `@raster_attribute`, `neighboring()`, `trigger()`

      [:octicons-arrow-right-24: Tutorial](../tutorial/completing/fire_tutorial.ipynb) |
      [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/fire_spread)

    - :wolf: __Wolf-Sheep Predation__

      ---

      Agent lifecycle, movement, and ecological interactions.

      **Features**: `move.random()`, `at.agents`, `die()`, reproduction

      [:octicons-arrow-right-24: Tutorial](../tutorial/beginner/predation_tutorial.ipynb) |
      [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/wolf_sheep)

    - :cityscape: __Schelling Segregation__

      ---

      Mesa framework integration and social dynamics modeling.

      **Features**: `shuffle_do()`, `self.p`, Mesa compatibility

      [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/schelling) |
      [:octicons-book-24: README](https://github.com/SongshGeo/ABSESpy/blob/master/examples/schelling/README.md)

    - :chart_with_upwards_trend: __Hotelling's Law__

      ---

      Decision-making framework and spatial competition.

      **Features**: Links between Actors and PatchCells

      [:octicons-arrow-right-24: Tutorial](../tutorial/beginner/hotelling_tutorial.ipynb) |
      [:octicons-code-24: Source](https://github.com/SongshGeo/ABSESpy/tree/master/examples/hotelling_law)

    </div>

=== "中文"

    ## 关于这些示例

    这些示例通过经典ABM模型展示ABSESpy的核心功能。
    每个示例都包含完整的源代码、文档和测试。

    ## 可用示例

    <div class="grid cards" markdown>

    - :fire: __火灾传播__

      ---

      演示空间建模、栅格属性和可视化。

      **特性**: `@raster_attribute`, `neighboring()`, `trigger()`

      [:octicons-arrow-right-24: 教程](../tutorial/completing/fire_tutorial.ipynb) |
      [:octicons-code-24: 源码](https://github.com/SongshGeo/ABSESpy/tree/master/examples/fire_spread)

    - :wolf: __狼羊捕食__

      ---

      智能体生命周期、移动和生态互动。

      **特性**: `move.random()`, `at.agents`, `die()`, 繁殖

      [:octicons-arrow-right-24: 教程](../tutorial/beginner/predation_tutorial.ipynb) |
      [:octicons-code-24: 源码](https://github.com/SongshGeo/ABSESpy/tree/master/examples/wolf_sheep)

    - :cityscape: __Schelling隔离__

      ---

      Mesa框架集成和社会动态建模。

      **特性**: `shuffle_do()`, `self.p`, Mesa兼容

      [:octicons-code-24: 源码](https://github.com/SongshGeo/ABSESpy/tree/master/examples/schelling) |
      [:octicons-book-24: 说明](https://github.com/SongshGeo/ABSESpy/blob/master/examples/schelling/README.md)

    - :chart_with_upwards_trend: __Hotelling定律__

      ---

      决策框架和空间竞争。

      **特性**: Actors与PatchCells的连接

      [:octicons-arrow-right-24: 教程](../tutorial/beginner/hotelling_tutorial.ipynb) |
      [:octicons-code-24: 源码](https://github.com/SongshGeo/ABSESpy/tree/master/examples/hotelling_law)

    </div>

## Framework Advantages / 框架优势

=== "English"

    These examples highlight how ABSESpy reduces development effort:

    - **Spatial modeling made easy**: Built-in grid, raster attributes, neighbor queries
    - **Agent lifecycle management**: Automatic handling of birth/death, movement
    - **Mesa compatibility**: Use existing Mesa models with minimal changes
    - **Type safety**: Full type hints for better IDE support
    - **Testing support**: Comprehensive test utilities

=== "中文"

    这些示例展示ABSESpy如何减少开发成本：

    - **简化空间建模**: 内置网格、栅格属性、邻居查询
    - **智能体生命周期管理**: 自动处理出生/死亡、移动
    - **Mesa兼容性**: 最小修改即可使用现有Mesa模型
    - **类型安全**: 完整类型提示，更好的IDE支持
    - **测试支持**: 全面的测试工具

[^1]:
    Heuristic models are streamlined strategies used to tackle complex issues when precise formulas or solutions aren't feasible. These models rely on heuristic methods, practical tactics that may not always yield the best solution but offer a satisfactory one within an acceptable time limit.
