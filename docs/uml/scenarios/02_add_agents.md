# 添加代理

用户创建和添加 Actor 到模型的完整流程。

## 场景描述

用户通过模型代理容器创建指定数量的 Actor，系统自动初始化代理属性、注册到模型、并返回代理列表供后续操作使用。

## 时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant AgentsContainer as _ModelAgentsContainer
    participant ActorClass as ActorClass
    participant Actor as Actor
    participant MainModel as MainModel
    participant ActorsList as ActorsList
    participant LinkNode as _LinkNodeActor
    participant LinkProxy as _LinkProxy
    participant Movements as _Movements

    User->>AgentsContainer: new(ActorClass, num=10)
    AgentsContainer->>AgentsContainer: 验证参数
    AgentsContainer->>AgentsContainer: 创建代理列表

    loop 创建 10 个代理
        AgentsContainer->>ActorClass: __init__(model, **kwargs)
        ActorClass->>Actor: 调用父类初始化
        Actor->>MainModel: 注册到模型
        MainModel->>MainModel: 添加到代理集合

        Actor->>LinkNode: 初始化链接节点
        LinkNode->>LinkProxy: 创建链接代理
        LinkProxy-->>LinkNode: link_proxy

        Actor->>Movements: 初始化移动管理
        Movements-->>Actor: movements

        Actor->>Actor: 设置代理属性
        Actor->>Actor: 初始化代理状态
        Actor-->>ActorClass: actor_instance
        ActorClass-->>AgentsContainer: actor
    end

    AgentsContainer->>ActorsList: ActorsList(model, actors)
    ActorsList->>ActorsList: 初始化代理列表
    ActorsList-->>AgentsContainer: actors_list

    AgentsContainer-->>User: ActorsList[10个代理]

    Note over User, ActorsList: 代理创建完成，已注册到模型并返回列表
```

## 关键步骤说明

### 1. 代理容器处理
- 用户调用 `model.agents.new(ActorClass, num=10)`
- `_ModelAgentsContainer` 验证参数和代理类
- 准备创建指定数量的代理实例

### 2. 代理实例化
- 循环创建 10 个代理实例
- 每个代理调用 `ActorClass.__init__(model, **kwargs)`
- 代理类继承自 `Actor` 基类

### 3. 代理初始化
- **模型注册**: 代理自动注册到 `MainModel`
- **链接节点**: 初始化 `_LinkNodeActor` 功能
- **链接代理**: 创建 `_LinkProxy` 用于网络操作
- **移动管理**: 初始化 `_Movements` 用于空间移动
- **属性设置**: 设置代理的基本属性和状态

### 4. 代理列表创建
- 所有代理创建完成后，封装为 `ActorsList`
- `ActorsList` 提供批量操作功能
- 返回给用户进行后续操作

## 使用示例

```python
# 定义自定义代理类
class Farmer(Actor):
    def __init__(self, model, energy=100, skill=0.5, **kwargs):
        super().__init__(model, **kwargs)
        self.energy = energy
        self.skill = skill
        self.breed = "Farmer"

    def harvest(self):
        if self.energy > 0:
            self.energy -= 10
            return self.skill * 10
        return 0

class Hunter(Actor):
    def __init__(self, model, strength=80, **kwargs):
        super().__init__(model, **kwargs)
        self.strength = strength
        self.breed = "Hunter"

    def hunt(self):
        if self.strength > 0:
            self.strength -= 5
            return self.strength * 0.1
        return 0

# 创建代理
farmers = model.agents.new(Farmer, num=20, energy=100, skill=0.7)
hunters = model.agents.new(Hunter, num=10, strength=90)

print(f"创建了 {len(farmers)} 个农民")
print(f"创建了 {len(hunters)} 个猎人")
```

## 代理属性初始化

每个代理创建后包含以下核心属性：

- `unique_id`: 唯一标识符
- `model`: 对主模型的引用
- `breed`: 代理类型标识
- `alive`: 存活状态
- `on_earth`: 是否在地球上（在单元格中）
- `pos`: 空间位置
- `link`: 网络链接代理
- `move`: 移动管理对象

## 批量操作支持

创建的 `ActorsList` 支持以下批量操作：

```python
# 批量更新属性
farmers.update("energy", 100)

# 批量执行方法
farmers.shuffle_do("harvest")

# 批量选择
active_farmers = farmers.select(lambda f: f.energy > 50)

# 获取属性数组
energy_array = farmers.array("energy")

# 随机操作
random_farmer = farmers.random.choice()
```

## 代理生命周期

代理创建后的生命周期管理：

1. **创建**: 通过 `model.agents.new()` 创建
2. **注册**: 自动注册到模型代理集合
3. **初始化**: 设置初始属性和状态
4. **操作**: 执行各种代理行为
5. **移除**: 通过 `die()` 或 `deregister_agent()` 移除

## 相关文件

- `abses/agents/container.py`: _ModelAgentsContainer 代理容器
- `abses/agents/actor.py`: Actor 代理基类
- `abses/agents/sequences.py`: ActorsList 代理列表
- `abses/human/links.py`: 网络链接功能
- `abses/space/move.py`: 移动管理功能
