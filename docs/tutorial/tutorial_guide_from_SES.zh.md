# :checkered_flag: 我熟悉 SES

如果您了解 SES 相关的概念，您应该知道[涌现]是非常重要的特征，ABM 的优点就是能够揭示并模拟它们。
当然 SES 还有其他特征，我们强烈建议从具体的案例模型开始，了解 ABM 这个方法如何帮助您识别 SES 的具体特征。

!!! warning "警告"

    我们正在积极开发不同的案例，以下一些示例将很快推出。

| SES 特征      | 相关案例模型                          |
| ----------- | ------------------------------------ |
| :material-merge: 涌现       | :bulb: [火灾]  |
| :material-chart-line: 动态性       | :bulb: [捕食] |
| :fontawesome-solid-person-circle-question: 人类决策    | :bulb: [Hotelling] |
| :material-police-badge-outline: 现实世界政策    | :bulb: 水资源分配 |

如果您曾使用 [Python] 实现过地表过程/人类社会过程模型，您可以轻松地将它们作为子模块嵌入到 `ABSESpy` 的 ABM 中使用。
这是因为 `ABSESpy` 的框架结构完美[匹配 SES 结构]，并且设计用于轻松耦合。

<!-- links -->
  [涌现]: ../wiki/concepts/emergence.md
  [匹配 SES 结构]: ../tutorial/beginner/organize_model_structure.ipynb
  [Hotelling]: ../tutorial/beginner/hotelling_tutorial.ipynb
  [火灾]: ../tutorial/completing/fire_tutorial.ipynb
  [捕食]: ../tutorial/beginner/predation_tutorial.ipynb

