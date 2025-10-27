# 代理容器管理

_ModelAgentsContainer 管理代理的完整流程。

## 流程描述

代理容器负责管理模型中的所有代理，提供代理的创建、选择、过滤、移除等功能，确保代理的一致性和高效访问。

## 时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Container as _ModelAgentsContainer
    participant ActorClass as ActorClass
    participant Actor as Actor
    participant MainModel as MainModel
    participant ActorsList as ActorsList
    participant Filter as 过滤器
    participant Selection as 选择器

    Note over User, Selection: 代理创建流程
    User->>Container: new(ActorClass, num=10)
    Container->>Container: 验证参数
    Container->>Container: 准备创建代理列表

    loop 创建 10 个代理
        Container->>ActorClass: __init__(model, **kwargs)
        ActorClass->>Actor: 调用父类初始化
        Actor->>MainModel: 注册到模型
        MainModel->>MainModel: 添加到代理集合
        Actor-->>Container: actor_instance
    end

    Container->>ActorsList: ActorsList(model, actors)
    ActorsList-->>Container: actors_list
    Container-->>User: ActorsList[10个代理]

    Note over User, Selection: 代理选择流程
    User->>Container: select(selection, agent_type)
    Container->>Filter: 应用选择条件
    Filter->>Filter: 过滤代理列表
    Filter-->>Container: filtered_actors

    Container->>Selection: 应用代理类型过滤
    Selection->>Selection: 按类型过滤
    Selection-->>Container: typed_actors

    Container->>ActorsList: ActorsList(model, typed_actors)
    ActorsList-->>Container: selected_list
    Container-->>User: ActorsList[选择的代理]

    Note over User, Selection: 代理移除流程
    User->>Container: remove(actor)
    Container->>Container: 验证代理存在
    Container->>MainModel: deregister_agent(actor)
    MainModel->>MainModel: 从代理集合移除
    MainModel-->>Container: 移除完成
    Container-->>User: 移除成功

    Note over User, Selection: 代理查询流程
    User->>Container: __getitem__(breed)
    Container->>Container: 按品种过滤
    Container->>ActorsList: ActorsList(model, breed_actors)
    ActorsList-->>Container: breed_list
    Container-->>User: ActorsList[指定品种的代理]
```

## 关键功能说明

### 1. 代理创建
- 用户指定代理类和数量
- 容器验证参数并创建代理实例
- 代理自动注册到主模型
- 返回 `ActorsList` 供后续操作

### 2. 代理选择
- 支持多种选择条件（函数、字典、字符串）
- 支持按代理类型过滤
- 返回符合条件的代理列表

### 3. 代理移除
- 从容器中移除指定代理
- 从主模型中注销代理
- 清理相关资源

### 4. 代理查询
- 按品种（breed）查询代理
- 支持多种查询方式
- 返回查询结果列表

## 代理容器实现

### _ModelAgentsContainer 核心方法
```python
class _ModelAgentsContainer:
    def __init__(self, model: MainModelProtocol, max_len: None | Number = None):
        self._model = model
        self._agents = model._all_agents
        self._max_length = max_len

    def new(self, breed: Type[ActorProtocol], num: int, **kwargs) -> ActorsList:
        """创建新代理"""
        if self.is_full:
            raise RuntimeError("Container is full")

        actors = []
        for _ in range(num):
            actor = breed(model=self._model, **kwargs)
            actors.append(actor)

        return ActorsList(self._model, actors)

    def select(self, selection: Callable | str | Dict[str, Any] | None = None,
               agent_type: Optional[Type[ActorProtocol] | str] = None,
               **kwargs: Any) -> ActorsList:
        """选择代理"""
        # 获取所有代理
        actors = list(self._agents)

        # 应用选择条件
        if selection is not None:
            actors = self._apply_selection(actors, selection)

        # 应用代理类型过滤
        if agent_type is not None:
            actors = self._filter_by_type(actors, agent_type)

        return ActorsList(self._model, actors)

    def remove(self, actor: ActorProtocol) -> None:
        """移除代理"""
        if actor in self._agents:
            self._agents.remove(actor)
            self._model.deregister_agent(actor)

    def __getitem__(self, breeds: Optional[Breeds]) -> ActorsList:
        """按品种获取代理"""
        if breeds is None:
            return ActorsList(self._model, list(self._agents))

        if isinstance(breeds, type):
            breeds = [breeds]

        actors = []
        for actor in self._agents:
            if actor.breed in breeds:
                actors.append(actor)

        return ActorsList(self._model, actors)
```

### 选择条件处理
```python
def _apply_selection(self, actors: List[ActorProtocol],
                    selection: Callable | str | Dict[str, Any]) -> List[ActorProtocol]:
    """应用选择条件"""
    if callable(selection):
        # 函数选择
        return [actor for actor in actors if selection(actor)]

    elif isinstance(selection, str):
        # 字符串选择
        if selection == "on_earth":
            return [actor for actor in actors if actor.on_earth]
        elif selection == "alive":
            return [actor for actor in actors if actor.alive]
        elif selection.startswith("ids="):
            # 按ID选择
            ids = selection.split("=")[1].split(",")
            return [actor for actor in actors if str(actor.unique_id) in ids]

    elif isinstance(selection, dict):
        # 字典选择
        filtered_actors = actors
        for key, value in selection.items():
            filtered_actors = [actor for actor in filtered_actors
                             if getattr(actor, key, None) == value]
        return filtered_actors

    return actors

def _filter_by_type(self, actors: List[ActorProtocol],
                   agent_type: Type[ActorProtocol] | str) -> List[ActorProtocol]:
    """按类型过滤代理"""
    if isinstance(agent_type, type):
        return [actor for actor in actors if isinstance(actor, agent_type)]
    elif isinstance(agent_type, str):
        return [actor for actor in actors if actor.breed == agent_type]

    return actors
```

## 使用示例

### 基本代理管理
```python
# 创建代理
farmers = model.agents.new(Farmer, num=20, energy=100)
hunters = model.agents.new(Hunter, num=10, strength=80)

# 选择代理
all_actors = model.agents.select()
alive_actors = model.agents.select("alive")
on_earth_actors = model.agents.select("on_earth")

# 按类型选择
farmer_actors = model.agents.select(agent_type=Farmer)
hunter_actors = model.agents.select(agent_type="Hunter")

# 按属性选择
high_energy_farmers = model.agents.select(
    selection=lambda a: a.breed == "Farmer" and a.energy > 80
)
```

### 高级选择条件
```python
# 字典选择
selected_actors = model.agents.select({
    "breed": "Farmer",
    "energy": 100,
    "alive": True
})

# 复合选择
active_farmers = model.agents.select(
    selection={"breed": "Farmer", "alive": True},
    agent_type=Farmer
)

# 按ID选择
specific_actors = model.agents.select("ids=1,2,3,4,5")

# 自定义函数选择
def select_productive_actors(actor):
    return (actor.breed == "Farmer" and
            actor.energy > 50 and
            actor.skill > 0.7)

productive_actors = model.agents.select(select_productive_actors)
```

### 批量操作
```python
# 批量更新属性
farmers = model.agents[Farmer]
farmers.update("energy", 100)
farmers.update("skill", 0.8)

# 批量执行方法
farmers.shuffle_do("harvest")
hunters.shuffle_do("hunt")

# 批量选择
active_farmers = farmers.select(lambda f: f.energy > 50)
active_farmers.shuffle_do("work")
```

### 代理移除
```python
# 移除单个代理
actor = model.agents.select("ids=1").item()
model.agents.remove(actor)

# 批量移除
dead_actors = model.agents.select(lambda a: not a.alive)
for actor in dead_actors:
    model.agents.remove(actor)

# 按条件移除
low_energy_farmers = model.agents.select(
    selection=lambda a: a.breed == "Farmer" and a.energy < 10
)
for farmer in low_energy_farmers:
    farmer.die()  # 这会自动从容器中移除
```

## 性能优化

### 索引优化
```python
class OptimizedAgentsContainer(_ModelAgentsContainer):
    def __init__(self, model, max_len=None):
        super().__init__(model, max_len)
        self._breed_index = {}
        self._attribute_index = {}

    def _update_indexes(self, actor):
        """更新索引"""
        # 更新品种索引
        breed = actor.breed
        if breed not in self._breed_index:
            self._breed_index[breed] = []
        self._breed_index[breed].append(actor)

        # 更新属性索引
        for attr in ["alive", "on_earth"]:
            if attr not in self._attribute_index:
                self._attribute_index[attr] = {"True": [], "False": []}
            self._attribute_index[attr][str(getattr(actor, attr))].append(actor)

    def select(self, selection=None, agent_type=None, **kwargs):
        """优化的选择方法"""
        if isinstance(selection, str) and selection in self._attribute_index:
            # 使用索引快速选择
            actors = self._attribute_index[selection]["True"]
        else:
            actors = list(self._agents)

        return super().select(selection, agent_type, **kwargs)
```

### 缓存机制
```python
class CachedAgentsContainer(_ModelAgentsContainer):
    def __init__(self, model, max_len=None):
        super().__init__(model, max_len)
        self._selection_cache = {}
        self._cache_ttl = 10  # 缓存生存时间

    def select(self, selection=None, agent_type=None, **kwargs):
        """带缓存的选择方法"""
        cache_key = (str(selection), str(agent_type), str(kwargs))

        if cache_key in self._selection_cache:
            cached_result, timestamp = self._selection_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_result

        result = super().select(selection, agent_type, **kwargs)
        self._selection_cache[cache_key] = (result, time.time())

        return result
```

## 相关文件

- `abses/agents/container.py`: _ModelAgentsContainer 代理容器
- `abses/agents/sequences.py`: ActorsList 代理列表
- `abses/agents/actor.py`: Actor 代理基类
- `abses/core/model.py`: MainModel 主模型
- `abses/core/protocols.py`: 协议接口定义
