# Schelling Segregation Model / 谢林隔离模型

经典的社会隔离Agent-Based Model，**展示ABSESpy与Mesa的无缝集成**。

## 模型概述

谢林隔离模型展示了即使个体只有轻微的偏好，也能导致显著的宏观隔离现象：
- 智能体分为两种类型（蓝色和橙色）
- 每个智能体希望至少一定比例的邻居与自己同类
- 不满意的智能体会移动到空cell
- 最终形成高度隔离的空间格局

**关键洞察**：即使个体只需要40%的同类邻居就满意（即接受60%的异类邻居），最终仍会产生高度隔离。

## 🎯 核心ABSESpy特性展示

本示例突出展示以下ABSESpy特有功能：

| 特性 | 描述 | 代码位置 |
|------|------|----------|
| **MainModel** | 模拟框架基类，内置智能体管理 | `Schelling(MainModel)` |
| **Mesa Agent兼容** | 直接使用Mesa的Agent类 | `SchellingAgent(Agent)` |
| **agents.shuffle_do()** | 随机顺序激活智能体 | `self.agents.shuffle_do("step")` |
| **self.random** | 统一的随机数生成器 | `self.random.random()` |
| **self.p** | 便捷的参数访问 | `self.p.height`, `self.p.homophily` |
| **Mesa Grid集成** | 直接使用Mesa的Grid系统 | `SingleGrid`, `grid.place_agent()` |
| **Mesa DataCollector** | 使用Mesa的数据收集 | `DataCollector` |
| **自动调度** | 内置智能体调度机制 | 无需手动管理 |

## 依赖说明

**重要**：此示例需要额外的Mesa依赖（ABSESpy核心不强制依赖Mesa）：

```bash
# 使用pip安装
pip install mesa solara

# 或使用 uv（推荐）
uv sync
```

## 运行方式

### 交互式可视化

```bash
# 1. 确保安装了依赖
pip install mesa solara

# 2. 启动Solara可视化界面
cd examples/schelling
solara run app.py

# 3. 在浏览器打开: http://127.0.0.1:8765/
```

**注意**：如果遇到Solara环境问题（如`KeyError: 'load_extensions'`），可以：
1. 尝试重新安装：`pip install --upgrade solara jupyter`
2. 或使用下面的程序化运行方式

### 程序化运行

**方式1：使用提供的脚本**

```bash
cd examples/schelling
python run_simple.py
```

这个脚本会运行模型并打印详细的进度信息。

**方式2：自定义代码**

```python
from examples.schelling.model import Schelling

# 创建模型（ABSESpy参数格式）
params = {
    "model": {
        "width": 20,
        "height": 20,
        "density": 0.8,
        "minority_pc": 0.5,
        "homophily": 0.4,  # 40% similar neighbors needed
        "radius": 1
    }
}
model = Schelling(parameters=params, seed=42)

# 运行模拟直到收敛
step = 0
while model.running and step < 100:
    model.step()
    step += 1
    if step % 10 == 0:
        pct = model.happy / len(model.agents) * 100
        print(f"Step {step}: {model.happy}/{len(model.agents)} happy ({pct:.1f}%)")

print(f"✓ Converged after {step} steps")
print(f"✓ Final: {model.happy}/{len(model.agents)} happy")
```

## 关键特性详解

### 1. **MainModel + agents.shuffle_do()**: 智能体调度

```python
class Schelling(MainModel):  # ✨ ABSESpy特性: 模拟框架
    def step(self):
        self.happy = 0
        # ✨ ABSESpy特性: 随机顺序激活智能体
        self.agents.shuffle_do("step")
        # 终止条件：所有智能体都满意
        self.running = self.happy < len(self.agents)
```

**为什么特别？**
- `agents.shuffle_do("step")`: 自动随机激活所有智能体
- 无需手动：`random.shuffle(agents); for a in agents: a.step()`
- 内置调度器：自动管理智能体顺序
- 一行代码实现随机激活模式

---

### 2. **self.random**: 统一随机数生成

```python
def __init__(self, seed=None, **kwargs):
    super().__init__(seed=seed, **kwargs)

    # ✨ ABSESpy特性: 统一的随机数生成器
    for _, pos in self.grid.coord_iter():
        if self.random.random() < self.p.density:
            agent_type = 1 if self.random.random() < self.p.minority_pc else 0
```

**为什么特别？**
- `self.random`: 所有组件共享的RNG
- seed控制：一次设置，全局生效
- 可重现性：相同seed产生相同结果
- 无需手动传递random对象

---

### 3. **self.p**: 便捷参数访问

```python
class Schelling(MainModel):
    def __init__(self, seed=None, **kwargs):
        super().__init__(seed=seed, **kwargs)
        # ✨ ABSESpy特性: 参数自动存储在self.p
        height, width = int(self.p.height), int(self.p.width)

class SchellingAgent(Actor):
    def step(self):
        # ✨ ABSESpy特性: 智能体也能访问模型参数
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.p.radius
        )
```

**为什么特别？**
- `self.p.*`: 统一的参数访问接口
- 自动存储：kwargs自动转为p对象
- 类型安全：支持嵌套参数和默认值
- 智能体可访问：`model.p.homophily`

---

### 4. **Mesa集成**: 最佳兼容性

```python
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from abses import MainModel, Actor

class Schelling(MainModel):  # ✨ ABSESpy: MainModel基类
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ✨ Mesa组件无缝集成
        self.grid = SingleGrid(width, height, torus=True)
        self.datacollector = DataCollector(...)
```

**为什么特别？**
- **完全兼容Mesa组件**：Grid、Space、DataCollector
- **继承Mesa.Model**：ABSESpy的MainModel继承自Mesa.Model
- **混合使用**：可以用ABSESpy的特性+Mesa的组件
- **渐进迁移**：已有Mesa模型可逐步采用ABSESpy特性

---

### 5. **Mesa Agent兼容**: 完全互通

```python
from mesa import Agent  # 直接使用Mesa的Agent

class SchellingAgent(Agent):
    """使用Mesa原生Agent类"""

    def __init__(self, model, agent_type: int):
        super().__init__(model)  # Mesa Agent初始化
        self.type = agent_type

# ABSESpy MainModel可以直接管理Mesa Agent
model.agents.shuffle_do("step")  # ✨ ABSESpy特性作用于Mesa Agent
```

**为什么特别？**
- **完全兼容**: ABSESpy MainModel可直接管理Mesa的Agent
- **无需修改**: 已有Mesa Agent代码无需改动
- **混合使用**: 可在同一模型中使用Mesa Agent和ABSESpy Actor
- **渐进升级**: 先用MainModel增强，后续可选择性升级为Actor

## 配置参数

| 参数 | 描述 | 默认值 | 范围 |
|------|------|--------|------|
| width | 网格宽度 | 20 | >0 |
| height | 网格高度 | 20 | >0 |
| density | 初始占用密度 | 0.8 | 0-1 |
| minority_pc | 少数群体比例 | 0.5 | 0-1 |
| homophily | 同类邻居需求比例 | 0.4 | 0-1 |
| radius | 邻居搜索半径 | 1 | ≥1 |

## 测试

```bash
# 运行Schelling模型的所有测试
pytest tests/examples/test_schelling.py -v

# 测试覆盖:
# - SchellingAgent (2个测试)
# - Schelling模型 (6个测试)
```

**测试结果**: ✅ 8/8 全部通过（需安装mesa）

## 🎓 学习要点

### ABSESpy MainModel vs 纯Mesa Model

| 功能 | ABSESpy MainModel + Mesa Agent | 纯Mesa Model + Agent |
|------|-------------------------------|---------------------|
| **随机激活** | `agents.shuffle_do("step")` | `random.shuffle(agents); for a in agents: a.step()` |
| **参数访问** | `self.p.height` | `self.height` (手动存储) |
| **随机数** | `self.random` (统一) | 手动传递random对象 |
| **Agent类型** | Mesa `Agent` 或 ABSESpy `Actor` | Mesa `Agent` |
| **Grid/Space** | ✅ 完全兼容Mesa组件 | ✅ 原生 |
| **DataCollector** | ✅ 完全兼容 | ✅ 原生 |

### 关键优势

1. **shuffle_do()**: 一行代码实现随机激活（作用于Mesa Agent！）
2. **统一RNG**: seed控制所有随机行为
3. **参数管理**: self.p提供统一访问接口
4. **完全兼容Mesa**: 可直接使用Mesa的Agent、Grid、DataCollector
5. **渐进迁移**: 只需将`mesa.Model`改为`abses.MainModel`即可获得增强功能
6. **混合使用**: 同一模型可包含Mesa Agent和ABSESpy Actor

### 模型动力学

- **微观偏好**: 个体只需40%同类邻居
- **宏观结果**: 产生接近100%的同质性社区
- **自组织**: 没有中央控制，仅通过个体决策
- **涌现现象**: 整体行为不能由个体行为简单相加得出

## 相关文件

- `model.py`: Schelling模型类
- `agents.py`: SchellingAgent智能体类
- `app.py`: Solara可视化界面
- `analysis.ipynb`: 参数扫描和分析示例
- `tests/examples/test_schelling.py`: 完整测试套件

## 扩展建议

可以尝试：
- 增加第三种智能体类型
- 实现不同的邻居定义（曼哈顿距离）
- 添加移动成本（限制移动频率）
- 收集隔离程度的时间序列数据
- 参数扫描：homophily vs 最终隔离度

## 理论背景

该模型基于：

**原始论文**:
[Schelling, Thomas C. "Dynamic Models of Segregation." Journal of Mathematical Sociology, 1971.](https://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf)

**互动演示**:
[Parable of the Polygons](http://ncase.me/polygons/) by Vi Hart and Nicky Case

---

*此模型展示了ABSESpy如何与Mesa生态系统无缝集成，既保留Mesa的强大功能，又增加了便利特性。*
