# Wolf-Sheep Predation Model / 狼羊捕食模型

经典的捕食者-被捕食者Agent-Based Model，**重点展示ABSESpy的智能体建模功能**。

## 模型概述

该模型模拟狼和羊在草原上的动态交互：
- **羊** 吃草获得能量，消耗能量，繁殖
- **狼** 吃羊获得能量，消耗能量，繁殖
- **草** 被吃掉后需要时间重新生长

## 🎯 核心ABSESpy特性展示

本示例突出展示以下ABSESpy特有功能：

| 特性 | 描述 | 代码位置 |
|------|------|----------|
| **Actor** | 自主智能体基类，内置生命周期管理 | `Animal(Actor)` |
| **die()** | 自动清理和移除智能体 | `agent.die()` |
| **move.random()** | 随机移动到邻居cell | `self.move.random()` |
| **move.to()** | 移动到指定位置 | `agent.move.to("random", layer)` |
| **at** | 访问智能体当前所在cell | `self.at` |
| **at.agents.new()** | 在cell上创建新智能体 | `self.at.agents.new(Class)` |
| **at.agents.select()** | 筛选cell中的智能体 | `self.at.agents.select(agent_type=Sheep)` |
| **random.choice()** | 从列表中随机选择 | `agents.random.choice(when_empty=...)` |
| **agents.new()** | 批量创建智能体 | `self.agents.new(Wolf, num)` |
| **agents.has()** | 按类型统计智能体数量 | `self.agents.has(Sheep)` |
| **自动调度** | 智能体自动按顺序执行step() | 无需手动调度 |

## 运行方式

```bash
# 方式1: 直接运行（简单演示）
python model.py

# 方式2: 作为模块运行
python -m examples.wolf_sheep.model
```

## 关键特性详解

### 1. **Actor + 生命周期**: 智能体自动管理

```python
class Animal(Actor):  # ✨ ABSESpy特性: 智能体基类
    """能量驱动的智能体"""

    def update(self):
        self.energy -= 1
        if self.energy <= 0:
            self.die()  # ✨ ABSESpy特性: 自动清理

    def reproduce(self):
        # ✨ ABSESpy特性: 在当前cell创建offspring
        self.at.agents.new(self.__class__)
```

**为什么特别？**
- `Actor`: 内置位置、移动、感知等功能
- `die()`: 自动从模型、cell、可视化中移除
- `at.agents.new()`: 直接在当前位置创建新智能体
- 无需手动管理智能体列表的添加/删除

---

### 2. **move系统**: 声明式移动

```python
class Wolf(Animal):
    def step(self):
        # ✨ ABSESpy特性: 随机移动
        self.move.random()

# 初始化时的随机放置
# ✨ ABSESpy特性: move.to() 灵活放置
agent.move.to("random", layer=grassland)
```

**为什么特别？**
- `move.random()`: 自动移动到随机邻居cell
- `move.to("random")`: 字符串参数，无需计算坐标
- `move.to(cell)`: 也支持直接指定cell对象
- 自动处理边界、更新位置、触发事件

---

### 3. **at + agents.select()**: 智能体交互

```python
class Wolf(Animal):
    def eat_sheep(self):
        # ✨ ABSESpy特性: 访问当前cell
        # ✨ ABSESpy特性: 按类型筛选智能体
        sheep = self.at.agents.select(agent_type=Sheep)

        # ✨ ABSESpy特性: 随机选择+空值处理
        if a_sheep := sheep.random.choice(when_empty="return None"):
            a_sheep.die()  # ✨ ABSESpy特性: 自动清理
            self.energy += 2
```

**为什么特别？**
- `at`: 一个属性获取当前cell和所有相关信息
- `agents.select(agent_type=Class)`: 类型筛选，无需lambda
- `random.choice(when_empty=...)`: 优雅处理空列表
- `die()`: 一行代码完成清理

---

### 4. **agents.new() + agents.has()**: 批量管理

```python
def setup(self):
    # ✨ ABSESpy特性: 批量创建
    self.agents.new(Wolf, self.params.n_wolves)  # 创建50只狼
    self.agents.new(Sheep, self.params.n_sheep)  # 创建100只羊

def check_end(self):
    # ✨ ABSESpy特性: 按类型统计
    if not self.agents.has(Sheep):  # 羊灭绝?
        self.running = False
    elif self.agents.has(Sheep) >= 400:  # 羊过多?
        self.running = False
```

**为什么特别？**
- `agents.new(Class, num)`: 批量创建，返回列表
- `agents.has(Class)`: 按类型统计，不需要手动count
- 自动分配唯一ID、注册到调度器
- 支持单例模式：`agents.new(Class, singleton=True)`

---

### 5. **自动调度**: 无需手动循环

```python
class WolfSheepModel(MainModel):
    def step(self):
        # 只需要处理环境更新
        for cell in self.nature.array_cells.flatten():
            cell.grow()
        # ✨ ABSESpy特性: 智能体自动执行step()
        # 无需手动调用 wolf.step(), sheep.step()
```

**为什么特别？**
- ABSESpy自动调度所有智能体的`step()`方法
- 按创建顺序执行（可自定义）
- 死亡的智能体自动跳过
- 新创建的智能体下一轮加入

## 配置参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| shape | 网格大小 (height, width) | (50, 50) |
| n_wolves | 初始狼数量 | 50 |
| n_sheep | 初始羊数量 | 100 |
| rep_rate | 繁殖概率 | 0.04 |

## 测试

```bash
# 运行wolf_sheep模型的所有测试
pytest tests/examples/test_sheep_wolf.py -v

# 测试覆盖:
# - Grass cell功能 (3个测试)
# - Animal基类 (4个测试)
# - Wolf特定行为 (1个测试)
# - Sheep特定行为 (1个测试)
# - 完整模型 (6个测试)
```

## 🎓 学习要点

### ABSESpy vs 纯Mesa/NetLogo

| 功能 | ABSESpy | 纯Mesa | NetLogo |
|------|---------|--------|---------|
| **创建智能体** | `agents.new(Wolf, 50)` | 手动循环+add | `create-wolves 50` |
| **移动** | `agent.move.random()` | 手动计算邻居+移动 | `move-to one-of neighbors` |
| **位置访问** | `agent.at` | 手动查询grid | `patch-here` |
| **cell上创建** | `cell.agents.new(Class)` | 手动设置位置 | `hatch` |
| **按类型筛选** | `agents.select(agent_type=Sheep)` | `[a for a in ... if isinstance()]` | `sheep-here` |
| **统计数量** | `agents.has(Sheep)` | 手动count | `count sheep` |
| **生命周期** | `agent.die()` 自动清理 | 手动remove+cleanup | `die` |

### 关键优势

1. **声明式移动**: `move.random()`比手动计算邻居更简洁
2. **自动生命周期**: `die()`自动处理所有清理工作
3. **类型安全筛选**: `select(agent_type=Class)`比isinstance循环更清晰
4. **位置感知**: `at`属性提供cell和agents的统一访问
5. **批量操作**: `agents.new()`支持批量创建

### 模型动力学

1. **能量管理**: 每个动物都有能量，移动和行动消耗能量
2. **捕食关系**: 狼吃羊，羊吃草
3. **繁殖机制**: 能量充足时有概率繁殖
4. **终止条件**: 当某一方灭绝或羊过多时模型停止

## 扩展建议

可以尝试：
- 添加草的再生速度参数
- 实现不同种类的捕食者
- 添加空间异质性（不同区域草生长速度不同）
- 收集和分析种群动态数据

## 相关文件

- `model.py`: 模型实现
- `tests/examples/test_sheep_wolf.py`: 完整测试套件（15个测试）

---

*此模型展示了ABSESpy在经典ABM实现中的简洁性和强大功能。*

