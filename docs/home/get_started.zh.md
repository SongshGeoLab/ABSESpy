---
title: 快速开始
authors: Shuang Song
date: 2024-03-10
---

## 简介

`ABSESpy` 被设计为一个灵活且易于使用的社会生态系统（SES）基于智能体建模（ABM）框架。它构建在流行的 Python ABM 框架 [Mesa] 之上。`ABSESpy` 提供了一套工具和实用程序，帮助用户构建、运行和分析 SES 的 ABM 模型。

本快速入门教程将帮助您使用 `ABSESpy` 框架运行最简单的工作流程。如果您有智能体建模经验并希望通过示例学习 `ABSESpy`，可以查看[官方示例]。

下图展示了 `ABSESpy` API 的基本结构。放轻松，在入门阶段您不必熟悉所有功能。您可以随时访问 [API 文档]页面查找特定功能。

![abses_API](https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/abses_API.png)

## 运行 `ABSESpy` 模型

假设您已经成功安装了 `ABSESpy` 及其所有依赖项，并正确配置了环境以将模块导入到您的工作空间。运行第一个不执行任何操作的空白模型很简单 - 只需导入、初始化和运行...

```python title='model.py'
from abses import MainModel

model = MainModel()
model.run_model(steps=3)  # 运行多少步
```

!!! warning "警告"

    如果不提供 `steps` 参数，`.run_model` 将无限期运行，除非手动停止。除非在配置中可以找到结束条件。

## 自定义基本模块

正如"社会生态系统"这个名称所暗示的，它通常包括两个基本子系统：社会子系统和生态子系统。
每个子系统都有多个过程，特定模型只关心其中一些过程（根据设置）。

`ABSESpy` 将这种结构转换为两个模块：人类（human）和自然（nature）。
这两个模块中的每一个都可以附加一组子模块，用于模拟特定过程（这通常需要根据实际问题和专业知识来包含）。

!!! info "信息"

    === "ABSESpy 图示"

        <figure markdown>
        ![model_diagram](https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/model_diragram.png){ width="300" }
        <figcaption>
            ABSESpy 如何模拟 SES 的示意图
            </figcaption>
        </figure>

    === "SES 图示"

        <figure markdown>
        ![SES](https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/ses.png){ width="300" }
        <figcaption>
            社会生态系统示意图
            </figcaption>
        </figure>

        `ABSESpy` 的结构模仿了社会生态系统（SES）的基本结构 (1)。
        { .annotate }

        1.  有关 SES 的更多信息可以在 [wiki 页面](../wiki/about.md) 中了解。

因此，`ABSESpy` 提供的默认模型 `MainModel` 将 `BaseNature` 和 `BaseHuman` 作为两个基本模块。可以通过属性 `human` 和 `nature` 访问它们。

!!! Example "示例"

    === "human"

        ```python
        model = MainModel()
        type(model.human)

        # 输出
        >>> abses.human.BaseHuman
        ```

    === "nature"

        ```python
        model = MainModel()
        type(model.nature)

        # 输出
        >>> abses.nature.BaseNature
        ```

用户可以通过继承这三个基本组件 `BaseNature`、`BaseHuman` 和 `MainModel` 来自定义模块 (1)。
{ .annotate }

1. `ABSESpy` 使用术语"组件"（Component）来表示模块，不仅包括 `BaseNature` 和 `BaseHuman`，还包括附加到它们的子模块。

!!! example "示例"

    === "model.py"

        ```python title='model.py'
        from abses import MainModel
        # 导入自定义模块
        from human import CustomHuman
        from nature import CustomNature

        model = MainModel(human_class=Human, nature_class=Nature)
        model.run_model(steps=3)  # 运行多少步

        # 输出
        >>> Setup the nature module.
        >>> Setup the human module.
        >>> Nature in the step 0.
        >>> Human in the step 0.
        >>> Nature in the step 1.
        >>> Human in the step 1.
        >>> Nature in the step 2.
        >>> Human in the step 2.
        >>> End of the nature module.
        >>> End of the human module.
        ```

    === "human.py"

        ```python title='human.py'
        from abses import BaseHuman

        class CustomHuman(BaseHuman):
            """自定义的人类模块。
            """

            def initialize(self):
                print("初始化人类模块。")

            def setup(self):
                print("设置人类模块。")

            def step(self):
                print(f"第 {self.time.tick} 步的人类。")

            def end(self):
                print("人类模块结束。")
        ```

    === "nature.py"

        ```python title='nature.py'
        from abses import BaseNature

        class CustomNature(BaseNature):
            """自定义的自然模块。
            """

            def initialize(self):
                print("初始化自然模块。")

            def setup(self):
                print("设置自然模块。")

            def step(self):
                print(f"第 {self.time.tick} 步的自然。")

            def end(self):
                print("自然模块结束。")
        ```

    === "文件树"

        ```shell
        root
        └── src
            ├── human.py
            ├── model.py
            └── nature.py
        ```

        推荐的项目结构：

        1. `root` 是项目目录。
        2. `src` 包含所有源代码。
        3. `model.py` 是您的模型。
        4. 在 `human.py` 中，自定义社会子系统的逻辑。
        5. 在 `nature.py` 中，自定义生态子系统的逻辑。

在上面的示例中，我们自定义了两个组件 `Nature` 和 `Human`，然后从源代码导入它们作为模型的参数使用。
我们为每个组件编写了四种不同的方法：

- `initialize`: 模型初始化时调用。
- `setup`: 模型即将开始运行时调用。
- `step`: 模型的每个时间步调用。
- `end`: 模型运行结束时调用。

## 创建和管理智能体

基于智能体的模型意味着人工 SES 中将包含一些角色（actors）。`ABSESpy` 提供了一个 `AgentsContainer` 来存储和管理智能体，可以通过属性 `model.agents` 访问。在 SES 的背景下，智能体有时也被称为社会 `Actor`（1）。要创建这样的角色，我们需要导入 `Actor` 类，它也可以通过继承进行自定义。
{ .annotate }

1. 社会角色（social actor）- 不仅受系统影响，而且具有主动性，可以做出改变系统的决策

```python
from abses import Actor, MainModel


class MyActor(Actor):
    """自定义的智能体"""

    def say_hi(self) -> str:
        print(f"你好，世界！我是一个新的 {self.breed}！")


model = MainModel()
actors = model.agents.new(Actor, 5)
my_actor = model.agents.new(MyActor, singleton=True)

my_actor.say_hi()
print(model.agents)

# 输出
>>> "你好，世界！我是一个新的 MyActor！"
>>> "<AgentsContainer: (5)Actor; (1)MyActor>"
```

在上面的示例中，我们自定义了新品种（1）的智能体 - `MyActor`。
然后，我们创建了五个默认的 `Actor` 实例和一个 `MyActor` 实例。所有实例都存储在 `AgentsContainer` 中并附加到模型，以便用户可以随时通过 `AgentsContainer` 访问、添加、删除、查询和更改智能体。
{ .annotate }

1. 默认情况下，智能体的品种（breed）就是其类名。用户可以通过覆盖 `breed` 类属性来更改此行为。

## 模型配置

正如您所预期的，对真实世界 SES 的建模远比上面的示例代码复杂。幸运的是，`ABSESpy` 的理念之一是将配置与模型逻辑分离。只要我们按如下方式配置，您就会发现 ABSESpy 框架适用于任何复杂度的建模：

```python title='main.py'
from abses import MainModel, Actor

class MyModel(MainModel):
    """自定义模型。"""

    def setup(self):
        n_agents = self.params.get('init_agents')
        self.agents.new(Actor, n_agents)

    def step(self):
        n_agents = self.params.get('n_agents')
        self.agents.new(Actor, n_agents)

    def end(self):
        n_agents = len(self.agents)
        print(f"在 {self.time} 时，有 {n_agents} 个智能体。")

# 嵌套的参数字典
parameters = {
    'time': {'start': '2000-01-01', 'end': '2003-03-21', 'months': 8, 'years': 2},
    'model': {'init_agents': 5, 'n_agents': 1}
}

# 初始化模型并运行
model = MyModel(parameters=parameters)
model.run_model()
```

不要被这些参数吓到，事情很简单：

1. `MainModel` 接受嵌套字典作为参数。
2. 在参数中，`time` 描述了时间开始/步长/结束规则，而 `model` 提供了两个可被模型解析的参数。
3. 在 `time` 部分，`start = '2000-01-01'` 表示模型开始运行时，它模拟2000年1月1日。同样，`end = '2003-03-21'` 表示模型时间到达2003年3月21日时结束。每个时间步模拟两年八个月，因为有两个参数：`months = 8` 和 `years = 2`。
4. 根据自定义函数 `setup`，模型将根据提供的参数 `init_agents` 添加一些初始角色。同样，在自定义函数 `step` 中，模型将在每一步根据参数 `n_agents` 添加一些角色。
5. 好！初等数学时间！运行的模型应该在什么时候结束？结束时会有多少智能体？

```python
# 输出
>>> "在 <TimeDriver: 2005-05-01 00:00:00> 时，有 7 个智能体。"
```

!!! tip "提示"

    在实践中，您不必担心为参数编写长长的嵌套字典。`ABSESpy` 允许用户通过[使用配置文件]轻松管理复杂参数。

## 下一步做什么

恭喜！到目前为止，您已经熟悉了 `ABSESpy` 框架的主要概念，并知道如何运行模型。

我们鼓励您返回[指南检查清单]，找出最吸引您的功能或示例模型。

一旦您决定使用 `ABSESpy` 开发自己的 ABM，我们组织良好的 [API 文档]应该是一个很好的参考。我们还为不同级别的用户提供了[详细教程]，祝编码愉快！

<!-- Links -->
  [指南检查清单]: guide_checklist.md
  [详细教程]: ../tutorial/tutorial.md
  [使用配置文件]: ../tutorial/beginner/manage_parameters.ipynb
  [API 文档]: ../api/api.md
  [官方示例]: ../examples/official.md
  [Mesa]: https://github.com/projectmesa/mesa

