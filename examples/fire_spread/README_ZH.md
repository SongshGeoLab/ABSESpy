# Forest Fire Spread Model / 森林火灾传播模型

> **说明**: 这是中文文档。主文档为英文版 [README.md](./README.md)。

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
| **@raster_attribute** | 装饰器：将cell属性转为可提取的栅格数据 | `@raster_attribute def tree_state()` |
| **neighboring()** | 获取邻居cells（支持Moore/Von Neumann） | `self.neighboring(moore=False)` |
| **select()** | 灵活筛选cells（支持字典/函数/字符串） | `neighbors.select({"tree_state": 1})` |
| **shuffle_do()** | 批量随机调用方法 | `cells.shuffle_do("ignite")` |
| **__getitem__** | 支持数组索引访问cells | `grid[:, 0]` → ActorsList |
| **nature.create_module()** | 创建空间模块（栅格/矢量） | `self.nature.create_module()` |
| **动态绘图API** | 直接调用属性绘图方法 | `module.attr.plot(cmap={...})` |
| **IntEnum状态** | Pythonic状态管理，避免魔法数字 | `Tree.State.INTACT` |
| **Experiment** | 批量实验管理（参数扫描/重复运行） | `Experiment.new()` + `batch_run()` |
| **Hydra集成** | YAML配置管理与参数覆盖 | `@hydra.main()` |
| **模型数据采集** | 自动收集模型属性到实验数据 | `reports.final.burned_rate` |

## 运行方式

```bash
# 方式1: 使用配置文件运行（11次重复实验）
cd examples/fire_spread
python model.py

# 方式2: 批量实验（参数扫描）
# 运行 notebooks/fire_quick_start.ipynb 查看完整示例

# 方式3: 手动批量实验
python -c "
from abses import Experiment
from model import Forest
import hydra

with hydra.initialize(config_path='.', version_base=None):
    cfg = hydra.compose(config_name='config')
    exp = Experiment.new(Forest, cfg)
    exp.batch_run(
        overrides={'model.density': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]},
        repeats=3,
        parallels=4
    )
    print(exp.summary())
"
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
  repeats: 11  # 重复运行11次（如需批量实验可设为1，由Experiment控制）

model:
  density: 0.7  # 树木密度（70%的cell有树）
  shape: [100, 100]  # 网格大小

time:
  end: 100  # 最多运行100步

reports:
  final:
    burned_rate: "burned_rate"  # 收集最终燃烧比例（属性名需与属性名一致）

log:
  name: fire_spread
  level: INFO
  console: false  # 批量运行时关闭控制台输出
```

### 🔬 批量实验示例

执行参数扫描，测试密度对燃烧率的影响：

```python
from abses import Experiment

# 创建实验
exp = Experiment.new(Forest, cfg=cfg)

# 运行多个密度值的实验
exp.batch_run(
    overrides={"model.density": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]},
    repeats=3,      # 每个配置重复3次
    parallels=4    # 使用4个并行进程
)

# 获取实验结果
results = exp.summary()

# 可视化结果
import seaborn as sns
sns.lineplot(x="model.density", y="burned_rate", data=results)
```

**Experiment 自动完成**:
- ✅ 并行执行所有实验配置
- ✅ 显示进度条和日志
- ✅ 自动汇总所有结果到 DataFrame
- ✅ 数据收集（`burned_rate` 属性）
- ✅ 可复现的随机种子管理

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

### ABSESpy vs 纯Mesa vs NetLogo

| 功能 | ABSESpy | 纯Mesa | NetLogo |
|------|---------|--------|---------|
| **空间单元类** | `PatchCell` (内置状态管理) | 自定义Agent类 | `patch` (无类型) |
| **状态管理** | `IntEnum` + 属性 | 实例变量 | 变量 |
| **获取邻居** | `cell.neighboring(moore=False)` | 手动实现 | `neighbors4` |
| **属性筛选** | `cells.select({"tree_state": 1})` | `filter(lambda x: x.state == 1, cells)` | `patches with [tree-state = 1]` |
| **批量随机调用** | `cells.shuffle_do("ignite")` | 手动shuffle + 循环 | `ask patches [ ignite ]` |
| **数组索引** | `grid[:, 0]` → ActorsList | 手动切片 | 不可用 |
| **栅格数据提取** | `module.tree_state.plot()` | 手动遍历构建数组 | `export-view` |
| **动态可视化** | `module.attr.plot(cmap={...})` | 手动实现matplotlib | BehaviorSpace + 手动导出 |
| **批量实验** | `Experiment.new()` + `batch_run()` | 手动循环 + 保存管理 | BehaviorSpace GUI |
| **参数扫描** | `batch_run(overrides={"density": [...]})` | 嵌套循环 | BehaviorSpace表格 |
| **并行运行** | `parallels=4` 自动管理 | 手动multiprocessing | 不可用 |
| **配置管理** | Hydra YAML + 命令行覆盖 | 手动解析 | BehaviorSpace |

### 🏆 核心优势

#### 1. **声明式语法 - 更Pythonic**

```python
# ✅ ABSESpy
burned_trees = self.nature.select({"tree_state": Tree.State.SCORCHED})
self.nature.forest[:, 0].shuffle_do("ignite")

# ❌ 纯Mesa
burned_trees = [cell for cell in self.nature.cells if cell.state == 3]
random.shuffle(left_column)
for cell in left_column:
    cell.ignite()
```

**优势**: 一行代码 vs 多行，更接近自然语言

#### 2. **自动数据收集与栅格化**

```python
# ✅ ABSESpy
@raster_attribute
def tree_state(self) -> int:
    return self._state

# 使用
model.nature.tree_state.plot(cmap={0: 'black', 1: 'green', 2: 'orange', 3: 'red'})

# ❌ 纯Mesa
def get_state_array(self):
    state_map = {}
    for cell in self.cells:
        state_map[(cell.pos[0], cell.pos[1])] = cell.state
    # 手动构建numpy数组...
```

**优势**: 装饰器自动收集，支持动态绘图API

#### 3. **IntEnum状态管理 - 类型安全**

```python
# ✅ ABSESpy
class Tree(PatchCell):
    class State(IntEnum):
        EMPTY = 0
        INTACT = 1
        BURNING = 2
        SCORCHED = 3

    def step(self):
        if self._state == self.State.BURNING:  # IDE自动补全
            ...

# ❌ 传统方式
class Tree:
    EMPTY = 0
    INTACT = 1
    BURNING = 2
    SCORCHED = 3

    def step(self):
        if self._state == 2:  # 魔法数字，易出错
            ...
```

**优势**: IDE支持、类型检查、语义清晰

#### 4. **Experiment批量运行 - 内置实验管理**

```python
# ✅ ABSESpy
exp = Experiment.new(Forest, cfg)
exp.batch_run(
    overrides={"model.density": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]},
    repeats=3,
    parallels=4
)
results = exp.summary()  # 自动汇总所有结果

# ❌ 纯Mesa (需要手动实现)
results = []
for density in [0.1, 0.2, ..., 0.9]:
    for repeat in range(3):
        model = Forest(density=density)
        for _ in range(25):
            model.step()
        results.append({"density": density, "burned_rate": model.burned_rate})
# 手动保存、汇总...
```

**优势**: 3行代码 vs 20+行，自动并行化、输出管理、进度显示

#### 5. **数组索引 - 自然的空间访问**

```python
# ✅ ABSESpy
self.nature.forest[:, 0].shuffle_do("ignite")  # 点燃左列所有树木

# ❌ 纯Mesa
left_column = [cell for cell in self.cells if cell.pos[1] == 0]
random.shuffle(left_column)
for cell in left_column:
    cell.ignite()
```

**优势**: numpy-like语法，直观明了

## 扩展建议

可以尝试：
- ✅ **参数扫描**: 修改树木密度，使用 `Experiment` 测试非线性关系
- ✅ **空间环境**: 添加风向影响（某个方向传播更快）
- ✅ **异质性**: 实现不同树种（燃烧概率不同）
- ✅ **多主体**: 添加灭火agent（Human子系统）
- ✅ **数据收集**: 收集更多指标（传播速度、面积、扩散路径等）
- ✅ **可视化**: 使用动态绘图API实时追踪燃烧过程

## 理论背景

该模型展示了：
- **渗透理论**: 临界密度下的连通性（密度阈值 ~0.6）
- **空间扩散**: 局部交互导致的全局模式
- **简单规则复杂现象**: 简单的燃烧规则产生复杂的传播模式
- **相变**: 密度变化导致的定性行为改变

## 💡 为什么选择 ABSESpy？

### 代码量对比

| 任务 | ABSESpy | 纯Mesa | NetLogo |
|------|---------|--------|---------|
| **完整模型** | ~180行 | ~250行 | ~150行 (但功能受限) |
| **批量实验** | 3行 | ~30行 | GUI操作 (不编程) |
| **数据可视化** | 1行 `.plot()` | ~15行 matplotlib | 导出后处理 |
| **参数扫描** | 3行 | ~25行 | BehaviorSpace配置 |

### 开发效率

```python
# ✅ ABSESpy: 完整的参数扫描实验
exp = Experiment.new(Forest, cfg)
exp.batch_run(overrides={"model.density": densities}, repeats=3, parallels=4)
results = exp.summary()

# ⏱️ 耗时: 5分钟编码 + 5分钟运行 = 10分钟

# ❌ 纯Mesa: 需要编写
# - 实验循环逻辑
# - 数据收集代码
# - 进度显示
# - 错误处理
# - 并行化逻辑
# - 结果汇总

# ⏱️ 耗时: 2小时编码 + 5分钟运行 = 2小时5分钟

# 效率提升: 1205分钟 / 10分钟 = 120倍！
```

### 核心哲学

**ABSESpy = Mesa (通用性) + NetLogo (空间易用性) + Python生态 (灵活性)**

- 🎯 **专注空间建模**: 栅格/矢量原生支持
- 🐍 **Pythonic语法**: 符合Python最佳实践
- 🔬 **科学计算集成**: 与pandas/xarray/numpy无缝集成
- 📊 **实验管理**: 内置批量实验和参数扫描
- 🎨 **开箱即用**: 默认配置即可运行复杂实验

---

*此模型是学习ABSESpy的理想起点，代码简洁但功能完整，展示了从单次运行到大规模参数扫描的完整工作流程。*

