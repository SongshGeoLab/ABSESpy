# 运行模拟

用户运行模型仿真的完整流程。

## 场景描述

用户启动模型仿真，系统按时间步推进，在每个时间步中执行人类子系统、自然子系统的步骤，收集数据，直到达到结束条件。

## 时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant MainModel as MainModel
    participant TimeDriver as TimeDriver
    participant BaseHuman as BaseHuman
    participant BaseNature as BaseNature
    participant DataCollector as ABSESpyDataCollector
    participant HumanModule as HumanModule
    participant PatchModule as PatchModule
    participant ActorsList as ActorsList

    User->>MainModel: run_model(steps=100)
    MainModel->>MainModel: 初始化仿真状态
    MainModel->>MainModel: 设置结束条件

    loop 每个时间步 (steps=100)
        MainModel->>TimeDriver: go()
        TimeDriver->>TimeDriver: 推进时间
        TimeDriver->>TimeDriver: 更新 tick
        TimeDriver-->>MainModel: 时间更新完成

        MainModel->>BaseHuman: step()
        BaseHuman->>BaseHuman: _step()
        BaseHuman->>HumanModule: step()
        HumanModule->>HumanModule: 执行人类模块逻辑
        HumanModule->>ActorsList: 获取代理列表
        ActorsList->>ActorsList: 执行代理行为
        HumanModule-->>BaseHuman: 人类步骤完成
        BaseHuman-->>MainModel: 人类子系统完成

        MainModel->>BaseNature: step()
        BaseNature->>BaseNature: _step()
        BaseNature->>PatchModule: step()
        PatchModule->>PatchModule: 执行空间模块逻辑
        PatchModule->>PatchModule: 更新空间状态
        PatchModule-->>BaseNature: 空间步骤完成
        BaseNature-->>MainModel: 自然子系统完成

        MainModel->>DataCollector: collect(model)
        DataCollector->>DataCollector: 收集模型数据
        DataCollector->>DataCollector: 收集代理数据
        DataCollector->>DataCollector: 存储数据
        DataCollector-->>MainModel: 数据收集完成

        MainModel->>TimeDriver: is_end()
        TimeDriver->>TimeDriver: 检查结束条件
        TimeDriver-->>MainModel: 是否结束

        alt 如果达到结束条件
            MainModel->>MainModel: 结束仿真
            break
        end
    end

    MainModel->>MainModel: 仿真完成
    MainModel-->>User: 仿真结果

    Note over User, MainModel: 仿真完成，数据已收集
```

## 关键步骤说明

### 1. 仿真初始化
- 用户调用 `model.run_model(steps=100)`
- 系统初始化仿真状态和结束条件
- 准备数据收集和日志记录

### 2. 时间步循环
- 循环执行指定数量的时间步
- 每个时间步包含以下子步骤

### 3. 时间推进
- 调用 `time.go()` 推进时间
- 更新当前时间戳和步数计数器
- 检查是否达到结束时间

### 4. 人类子系统步骤
- 调用 `human.step()` 执行人类子系统
- 遍历所有人类模块执行步骤
- 代理执行行为逻辑和决策

### 5. 自然子系统步骤
- 调用 `nature.step()` 执行自然子系统
- 遍历所有空间模块执行步骤
- 更新空间状态和环境变化

### 6. 数据收集
- 调用 `datacollector.collect(model)` 收集数据
- 收集模型级别和代理级别的数据
- 存储到数据框架中

### 7. 结束条件检查
- 检查是否达到指定的步数
- 检查是否达到结束时间
- 检查是否满足其他结束条件

## 使用示例

### 基本仿真运行
```python
# 运行100个时间步
model.run_model(steps=100)

# 运行到指定时间
model.run_model(end_time="2025-12-31")

# 运行到指定步数
model.run_model(max_steps=1000)
```

### 自定义仿真逻辑
```python
class CustomModel(MainModel):
    def step(self):
        # 自定义步骤逻辑
        super().step()  # 调用父类步骤

        # 额外的仿真逻辑
        self.custom_environment_update()
        self.custom_agent_interactions()

    def custom_environment_update(self):
        # 环境更新逻辑
        for module in self.nature.modules.values():
            module.update_environment()

    def custom_agent_interactions(self):
        # 代理交互逻辑
        farmers = self.agents[Farmer]
        hunters = self.agents[Hunter]

        # 农民和猎人的交互
        for farmer in farmers:
            for hunter in hunters:
                if farmer.distance_to(hunter) < 5:
                    farmer.interact_with(hunter)
```

### 数据收集配置
```python
# 配置数据收集器
model.datacollector.add_model_reporter("tick", lambda m: m.time.tick)
model.datacollector.add_model_reporter("population", lambda m: len(m.agents))
model.datacollector.add_agent_reporter("energy", "energy")
model.datacollector.add_agent_reporter("wealth", "wealth")

# 运行仿真
model.run_model(steps=100)

# 获取收集的数据
model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
```

## 仿真控制

### 时间控制
```python
# 设置时间参数
config = {
    "time": {
        "start": "2020-01-01",
        "end": "2025-12-31",
        "freq": "1Y"  # 每年一个时间步
    }
}

model = MainModel(parameters=config)
model.run_model()  # 运行到结束时间
```

### 步数控制
```python
# 设置最大步数
model.run_model(max_steps=1000)

# 设置步数限制
model.run_model(steps=100)
```

### 条件控制
```python
class ConditionalModel(MainModel):
    def is_end(self):
        # 自定义结束条件
        if len(self.agents) == 0:
            return True  # 所有代理死亡时结束

        if self.time.tick >= 1000:
            return True  # 达到最大步数时结束

        return False
```

## 性能优化

### 并行处理
```python
# 启用并行处理
model.run_model(steps=100, parallel=True)
```

### 内存管理
```python
# 定期清理内存
model.run_model(steps=100, cleanup_interval=10)
```

### 数据收集优化
```python
# 减少数据收集频率
model.datacollector.set_collection_frequency(10)  # 每10步收集一次
```

## 仿真监控

### 进度显示
```python
# 启用进度条
model.run_model(steps=100, show_progress=True)
```

### 日志记录
```python
# 配置日志级别
import logging
logging.basicConfig(level=logging.INFO)

model.run_model(steps=100)
```

### 实时监控
```python
# 实时监控仿真状态
def monitor_simulation(model):
    print(f"Step: {model.time.tick}")
    print(f"Population: {len(model.agents)}")
    print(f"Time: {model.time.dt}")

model.run_model(steps=100, monitor=monitor_simulation)
```

## 相关文件

- `abses/core/model.py`: MainModel 主模型类
- `abses/core/time_driver.py`: TimeDriver 时间驱动
- `abses/human/human.py`: BaseHuman 人类子系统
- `abses/space/nature.py`: BaseNature 自然子系统
- `abses/utils/datacollector.py`: ABSESpyDataCollector 数据收集器
