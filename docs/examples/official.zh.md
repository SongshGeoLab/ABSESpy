# 官方示例

展示 ABSESpy 基于智能体建模功能的内置示例。

## 关于这些示例

这些示例通过经典 ABM 模型展示 ABSESpy 的核心功能。
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
  
  Mesa 框架集成和社会动态建模。
  
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

## 框架优势

这些示例展示 ABSESpy 如何减少开发成本：

- **简化空间建模**: 内置网格、栅格属性、邻居查询
- **智能体生命周期管理**: 自动处理出生/死亡、移动
- **Mesa 兼容性**: 最小修改即可使用现有 Mesa 模型
- **类型安全**: 完整类型提示，更好的 IDE 支持
- **测试支持**: 全面的测试工具

