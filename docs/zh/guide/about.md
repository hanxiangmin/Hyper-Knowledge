# 项目说明

Hyper-Knowledge 面向一个具体任务：让智能体把领域文档整理成可以检查、追溯和探索的高阶知识图谱。

它的使用入口是本地 Agent Skill。输出不止一张图，还包括规范化结构、成员角色、来源记录和检查回执；工作台负责让这些结构更容易阅读。

## 本项目的工作重点

- **建模约定**：人物、地点、时间等实体保持独立；事件作为超边，角色放在成员关联上。
- **规范化交付**：通过 `hk.bundle/v1` 分离节点、断言、成员和证据，并检查拓扑、引用和文件身份。
- **Skill 运行流程**：托管安装、环境检查、无模型演示，以及任务驱动的操作指引。
- **离线阅读体验**：包络、关联聚焦、关联矩阵，以及可追溯来源的详情面板。

这些是本项目的产品与实现侧重点，不表示超图、事件角色或来源追溯等概念由本项目首创。

## 开源基础与致谢

本项目的部分思路受到开源项目 [Hyper-Extract](https://github.com/yifanfeng97/hyper-extract) 启发，感谢原项目作者与贡献者。

Hyper-Knowledge 独立组织自己的高阶关系模型、规范化 bundle、Skill 管理和交互工作台。文档以这些具体工作为主线，不把超图、事件角色或来源追溯等通用概念包装成独立原创成果。

## 从哪里阅读代码

| 入口 | 内容 |
| --- | --- |
| [`hyper-knowledge/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyper-knowledge) | Skill 指令与参考契约 |
| [`hyperknowledge/bundle.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/bundle.py) | 数据包导出与校验 |
| [`hyperknowledge/skill_manager.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/skill_manager.py) | 托管安装、检查与运行时绑定 |
| [`hyperknowledge/visualization/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyperknowledge/visualization) | 可视化与离线 HTML 导出 |
| [`examples/sushi-local-preview/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-local-preview) | 当前苏轼展示案例、bundle 与胶囊总览工作台 |
| [`examples/sushi-document-test/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-document-test) | 早期输入材料、bundle 与工作台案例 |

## 参与项目

欢迎贡献领域案例、建模反例、来源定位改进和可复现的交互问题。说明“预期的关系是什么、当前输出哪里不对”，比只提交一张复杂的图更有帮助。

项目采用 [Apache-2.0 许可证](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/LICENSE)。

搜索关键词：Agent Skill、知识图谱、高阶知识图谱、超图、超边、关系抽取、事件建模、成员角色、来源追溯、关联矩阵、离线可视化。
