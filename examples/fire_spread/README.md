# Forest Fire Spread Model / 森林火灾传播模型

经典的森林火灾传播模型，**重点展示ABSESpy特有的空间建模功能**。

## 模型概述

模拟森林火灾的传播过程：
- 树木初始随机分布在网格上
- 最左列的树木被点燃
- 火势向相邻（非对角）树木蔓延
- 燃烧后的树木变为焦土，无法再次燃烧

## 🎯 核心ABSESpy特性展示

本示例突出展示以下ABSESpy特有功能：

| 特性 | 描述 | 代码位置 |
|------|------|----------|
| **PatchCell** | 空间网格单元基类，支持状态管理 | `Tree(PatchCell)` |
| **@raster_attribute** | 装饰器：将cell属性转为可提取的栅格数据 | `@raster_attribute def state()` |
| **neighboring()** | 获取邻居cells（支持Moore/Von Neumann） | `self.neighboring(moore=False)` |
| **select()** | 灵活筛选cells（支持字典/函数/字符串） | `neighbors.select({"state": 1})` |
| **trigger()** | 批量调用方法 | `cells.trigger("ignite")` |
| **ActorsList** | 增强的智能体列表，支持批量操作 | `ActorsList(self, cells)` |
| **nature.create_module()** | 创建空间模块（栅格/矢量） | `self.nature.create_module()` |
| **get_raster() / get_xarray()** | 提取栅格数据（numpy/xarray） | `self.nature.get_raster("state")` |
| **Experiment** | 批量实验管理（重复运行/参数扫描） | `Experiment(Forest, cfg)` |
| **Hydra集成** | YAML配置管理与参数覆盖 | `@hydra.main()` |

## 运行方式

```bash
# 直接运行（使用配置文件）
cd examples/fire_spread
python model.py

# 作为模块运行
python -m examples.fire_spread.model

# 批量运行（11次重复实验）
python model.py
```

## 关键特性详解

### 1. **PatchCell + @raster_attribute**: 空间状态管理

```python
class Tree(PatchCell):  # ✨ ABSESpy特性: 空间单元基类
    """树木有4个状态：0=空, 1=有树, 2=燃烧中, 3=已烧毁"""

    @raster_attribute  # ✨ ABSESpy特性: 属性可提取为栅格
    def state(self) -> int:
        """状态可被提取为栅格数据"""
        return self._state
```

**为什么特别？**
- `@raster_attribute`：自动将cell属性转换为空间栅格数据
- 无需手动构建数组，直接通过`module.get_raster('state')`提取
- 支持xarray格式，保留空间坐标信息

---

### 2. **neighboring() + select()**: 空间邻居交互

```python
def step(self):
    if self._state == 2:  # 如果正在燃烧
        # ✨ ABSESpy特性: 获取邻居cells
        neighbors = self.neighboring(moore=False, radius=1)
        # ✨ ABSESpy特性: 字典语法筛选cells
        neighbors.select({"state": 1}).trigger("ignite")
        self._state = 3
```

**为什么特别？**
- `neighboring()`: 一行代码获取邻居（支持Moore/Von Neumann）
- `select({"state": 1})`: 字典语法筛选，比lambda更简洁
- `trigger()`: 批量调用方法，避免手动循环

---

### 3. **ActorsList + trigger()**: 批量操作

```python
# ✨ ABSESpy特性: ActorsList批量操作
chosen_patches = grid.random.choice(self.num_trees, replace=False)
chosen_patches.trigger("grow")  # 批量调用grow方法

# 对leftmost column批量点燃
ActorsList(self, grid.array_cells[:, 0]).trigger("ignite")
```

**为什么特别？**
- `ActorsList`: 增强的智能体列表，支持链式操作
- `trigger()`: 批量方法调用，无需显式循环
- `random.choice()`: 与numpy随机数生成器集成

---

### 4. **get_raster() / get_xarray()**: 栅格数据提取

```python
# ✨ ABSESpy特性: 提取为numpy数组
state_array = self.nature.get_raster("state")
# shape: (1, 100, 100)

# ✨ ABSESpy特性: 提取为xarray (带坐标)
state_xr = self.nature.get_xarray("state")
# 可直接用于可视化和空间分析
state_xr.plot(cmap=cmap)
```

**为什么特别？**
- 自动从所有cells收集属性并构建栅格
- `get_xarray()`: 保留空间坐标，支持地理空间分析
- 与rasterio/xarray生态系统无缝集成

---

### 5. **Experiment + Hydra**: 批量实验管理

```python
# ✨ ABSESpy特性: Hydra配置管理
@hydra.main(version_base=None, config_path="", config_name="config")
def main(cfg: Optional[DictConfig] = None):
    # ✨ ABSESpy特性: Experiment批量运行
    exp = Experiment(Forest, cfg=cfg)
    exp.batch_run()  # 运行11次重复实验
```

**为什么特别？**
- Hydra集成：YAML配置管理，支持命令行覆盖
- `Experiment`: 自动处理重复运行、参数扫描
- 输出管理：自动创建时间戳目录，保存日志和数据

## 配置文件 (`config.yaml`)

```yaml
defaults:
  - default
  - _self_

exp:
  name: fire_spread
  outdir: out  # 输出目录
  repeats: 11  # 重复运行11次

model:
  density: 0.4  # 树木密度（40%的cell有树）
  shape: [100, 100]  # 网格大小

time:
  end: 25  # 最多运行25步

reports:
  final:
    burned: "burned_rate"  # 收集最终燃烧比例
```

## 测试

```bash
# 运行完整测试套件
pytest tests/examples/test_fire.py -v

# 测试覆盖:
# - Tree cell功能 (2个测试)
# - Forest模型 (4个测试，参数化)
```

**测试结果**: ✅ 6/6 全部通过

## 输出结果

运行后会在`out/fire_spread/YYYY-MM-DD/HH-MM-SS/`生成：
- `fire_spread.log`: 运行日志
- 数据收集结果（如果配置了数据收集）

## 性能指标

```python
@property
def burned_rate(self) -> float:
    """计算燃烧比例"""
    state = self.nature.get_raster("state")
    return np.squeeze(state == 3).sum() / self.num_trees
```

## 🎓 学习要点

### ABSESpy vs 纯Mesa/NetLogo

| 功能 | ABSESpy | 纯Mesa | NetLogo |
|------|---------|--------|---------|
| **获取邻居** | `cell.neighboring(moore=False)` | 手动实现 | `neighbors4` |
| **属性筛选** | `cells.select({"state": 1})` | 手动循环filter | `with [state = 1]` |
| **批量调用** | `cells.trigger("ignite")` | 手动循环 | `ask patches [ ignite ]` |
| **栅格提取** | `module.get_raster("state")` | 手动构建数组 | `export-view` |
| **配置管理** | Hydra YAML | 手动解析 | BehaviorSpace |
| **批量实验** | `Experiment.batch_run()` | 手动循环 | BehaviorSpace |

### 关键优势
1. **声明式语法**: `select({"state": 1})` 比 `filter(lambda x: x.state == 1)` 更清晰
2. **自动栅格化**: `@raster_attribute` 免去手动数组构建
3. **空间操作**: `neighboring()` 封装了常见邻居模式
4. **批量实验**: `Experiment` 自动管理输出和日志
5. **地理集成**: 原生支持xarray/rasterio/geopandas

## 扩展建议

可以尝试：
- 修改树木密度，观察火灾传播率变化
- 添加风向影响（某个方向传播更快）
- 实现不同树种（燃烧概率不同）
- 添加灭火agent
- 收集更多指标（传播速度、面积等）

## 理论背景

该模型展示了：
- **渗透理论**: 临界密度下的连通性
- **空间扩散**: 局部交互导致的全局模式
- **简单规则复杂现象**: 简单的燃烧规则产生复杂的传播模式

---

*此模型是学习ABSESpy的理想起点，代码简洁但功能完整。*

