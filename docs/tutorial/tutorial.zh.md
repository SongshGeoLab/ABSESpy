# 教程

在这里，我们提供了一系列基于 [Jupyter Notebook] 的教程，展示使用 `ABSESpy` 开发时可能遇到的需求及其解决策略。我们希望您已经阅读了[快速开始]指南，并评估了 `ABSESpy` 是否[适合您]。以下提供三个级别的教程：

> [!INFO] 进行中
> 本文档正在编写中，如果您发现任何错误、遗漏或有任何问题，请[联系我们](https://github.com/SongshGeoLab/ABSESpy/issues)。

## :hatching_chick: 初级教程

您希望使用 `ABSESpy` 框架创建和操作基本模型。想知道什么是"简单"模型？探索 [NetLogo 模型库]；您会在那里找到许多经典但易于理解的示例。

<div class="grid" markdown>

[:material-book: __B01__](beginner/get_started.ipynb) 随时在 notebook 中回顾快速开始。
{ .card }

[:material-book: __B02__](beginner/organize_model_structure.ipynb) 优雅地组织您的模型结构。
{ .card }

[:material-book: __B03__](beginner/time_control.ipynb) 让您的模型与现实世界保持同步。
{ .card }

[:material-book: __B04__](beginner/manage_parameters.ipynb) 使用配置文件分离配置和模型逻辑。
{ .card }

[:material-book: __B05__](beginner/actors.ipynb) 使用不同的容器更好地管理智能体。
{ .card }

[:material-book: __B06__](beginner/movement.ipynb) 在人工世界中移动您的智能体。
{ .card }

[:material-book: __B07__](beginner/predation_tutorial.ipynb) 狼羊捕食模型示例，一个经典的启发式模型[^1]。
{ .card }

[:material-book: __B08__](beginner/hotelling_tutorial.ipynb) 学习 `Actor` 和 `PatchCell` 之间的连接。
{ .card }

> :material-book: __Huh__ ... 此级别的更多教程即将推出。

</div>

## :horse_racing_tone1: 高级教程

您已经对基于智能体的模型有了透彻的理解。现在，您不仅满足于启发式模型[^1]，还渴望承担更大的项目来解决现实世界的 SES 问题。

<div class="grid" markdown>

[:material-book: __A01__](advanced/geodata.ipynb) 为自然模块包含真实世界的地理数据集。
{ .card }

> :material-book: __Huh__ ... 此级别的更多教程即将推出。

</div>

## :scientist: 完善教程

您已经建立了自己的模型并确认它没有重大逻辑问题。您需要批量实验、数据分析、绘图、参数敏感性分析和可视化方面的帮助。

<div class="grid" markdown>

[:material-book: __C01__](completing/fire_tutorial.ipynb) 使用不同参数进行批量运行，这是模型可视化和实验的综合示例。
{ .card }

> :material-book: __Huh__ ... 此级别的更多教程即将推出。

</div>

[^1]:
    启发式模型是用于解决复杂问题的简化策略，当精确公式或解决方案不可行时使用。这些模型依赖于启发式方法，即实用策略，可能不总是产生最佳解决方案，但在可接受的时间限制内提供令人满意的解决方案。

<!-- Links -->
  [Jupyter Notebook]: https://jupyter.org/
  [快速开始]: ../home/get_started.md
  [适合您]: ../home/guide_checklist.md
  [NetLogo 模型库]: https://ccl.northwestern.edu/netlogo/models/

