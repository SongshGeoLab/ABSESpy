# 代理移动

Actor 在空间环境中移动的完整流程。

## 场景描述

Actor 从当前位置移动到目标位置，系统自动处理空间位置更新、单元格切换、代理容器管理等操作，确保空间一致性。

## 时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Actor as Actor
    participant Movements as _Movements
    participant OldCell as 旧单元格
    participant NewCell as 新单元格
    participant OldAgentsContainer as 旧代理容器
    participant NewAgentsContainer as 新代理容器
    participant PatchModule as PatchModule
    participant MainModel as MainModel

    User->>Actor: move.to(target_cell)
    Actor->>Movements: move.to(target_cell)
    Movements->>Movements: 验证目标位置
    Movements->>Movements: 检查移动条件

    alt 如果代理在地球上
        Movements->>OldCell: 获取当前单元格
        OldCell-->>Movements: current_cell
        Movements->>OldAgentsContainer: 从旧单元格移除代理
        OldAgentsContainer->>OldAgentsContainer: remove(actor)
        OldAgentsContainer->>MainModel: deregister_agent(actor)
        MainModel->>MainModel: 从模型代理集合移除
        OldAgentsContainer-->>Movements: 移除完成
    end

    Movements->>Actor: moving(cell=target_cell)
    Actor->>Actor: 执行移动前逻辑
    Actor-->>Movements: keep_moving

    alt 如果允许移动
        Movements->>NewCell: 获取目标单元格
        NewCell-->>Movements: target_cell
        Movements->>NewAgentsContainer: 添加到新单元格
        NewAgentsContainer->>MainModel: 注册代理到模型
        MainModel->>MainModel: 添加到模型代理集合
        NewAgentsContainer->>NewAgentsContainer: add(actor)
        NewAgentsContainer-->>Movements: 添加完成

        Movements->>Actor: 更新位置属性
        Actor->>Actor: at = target_cell
        Actor->>Actor: pos = target_cell.pos
        Actor->>Actor: geometry = target_cell.geometry
        Actor->>Actor: on_earth = True

        Movements-->>Actor: 移动完成
    else 如果不允许移动
        Movements-->>Actor: 移动取消
    end

    Actor-->>User: 移动结果

    Note over User, MainModel: 代理移动完成，空间位置已更新
```

## 关键步骤说明

### 1. 移动请求
- 用户调用 `actor.move.to(target_cell)`
- `_Movements` 对象处理移动逻辑
- 验证目标位置的有效性

### 2. 当前位置处理
- 如果代理当前在地球上（`on_earth=True`）
- 从旧单元格的代理容器中移除代理
- 从主模型的代理集合中注销代理

### 3. 移动前检查
- 调用 `actor.moving(cell=target_cell)` 方法
- 代理可以执行移动前的逻辑（如资源消耗、条件检查等）
- 代理返回 `keep_moving` 决定是否继续移动

### 4. 目标位置处理
- 如果允许移动，获取目标单元格
- 将代理添加到新单元格的代理容器
- 重新注册代理到主模型

### 5. 位置属性更新
- 更新代理的位置属性：
  - `at`: 当前单元格引用
  - `pos`: 空间坐标
  - `geometry`: 几何对象
  - `on_earth`: 是否在地球上

## 使用示例

### 基本移动
```python
# 移动到指定单元格
actor.move.to(target_cell)

# 随机移动
actor.move.random()

# 按方向移动
actor.move.by("up")
actor.move.by("down")
actor.move.by("left")
actor.move.by("right")
```

### 高级移动
```python
# 向目标移动
actor.move.towards(target_cell)

# 远离目标移动
actor.move.away_from(threat_cell)

# 在范围内移动
actor.move.within(radius=5)
```

### 自定义移动逻辑
```python
class SmartActor(Actor):
    def moving(self, cell):
        # 检查目标单元格是否适合
        if cell.fertility < 0.3:
            return False  # 拒绝移动到贫瘠土地

        # 消耗移动能量
        if self.energy < 10:
            return False  # 能量不足，拒绝移动

        self.energy -= 10
        return True  # 允许移动

    def move_to_best_location(self):
        # 找到最适合的位置
        best_cells = self.model.nature.major_layer.get_cells(
            lambda c: c.fertility > 0.7 and not c.is_full
        )

        if best_cells:
            best_cell = best_cells.random.choice()
            self.move.to(best_cell)
```

## 移动条件检查

系统在移动过程中会检查以下条件：

### 1. 目标单元格有效性
- 目标单元格必须存在
- 目标单元格必须在有效的空间模块中

### 2. 容量限制
- 检查目标单元格是否已满（`max_agents` 限制）
- 如果已满，移动可能被拒绝

### 3. 代理状态
- 代理必须存活（`alive=True`）
- 代理必须有足够的资源进行移动

## 批量移动操作

支持批量移动操作：

```python
# 批量移动代理
farmers = model.agents[Farmer]
farmers.shuffle_do("move_to_best_location")

# 随机移动所有代理
all_actors = model.agents.select("on_earth")
all_actors.shuffle_do("move", how="random")
```

## 移动事件处理

移动过程中会触发相关事件：

```python
class MovingActor(Actor):
    def moving(self, cell):
        # 移动前事件
        self.model.notify("before_move", {
            "actor": self,
            "target_cell": cell,
            "old_cell": self.at
        })

        # 执行移动逻辑
        result = super().moving(cell)

        if result:
            # 移动后事件
            self.model.notify("after_move", {
                "actor": self,
                "new_cell": cell,
                "old_cell": self.at
            })

        return result
```

## 空间一致性保证

移动操作确保空间一致性：

1. **原子性**: 移动操作是原子的，要么完全成功，要么完全失败
2. **一致性**: 代理在任一时刻只能在一个单元格中
3. **完整性**: 所有相关的空间属性都会同步更新

## 性能优化

移动操作经过优化以提高性能：

1. **批量操作**: 支持批量移动以减少系统调用
2. **缓存机制**: 缓存常用的空间查询结果
3. **延迟更新**: 批量更新空间属性以提高效率

## 相关文件

- `abses/space/move.py`: _Movements 移动管理
- `abses/agents/actor.py`: Actor 代理基类
- `abses/space/cells.py`: PatchCell 栅格单元
- `abses/agents/container.py`: 代理容器管理
- `abses/space/patch.py`: PatchModule 栅格模块
