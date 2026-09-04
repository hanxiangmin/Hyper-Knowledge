# 从一条关系读到原文

图谱不是唯一交付物。Hyper-Knowledge 用 `hk.bundle/v1` 将实体、关系、成员和证据分开保存，让人和程序都能检查“画面背后究竟记录了什么”。

## 先读关系，再查成员

在苏轼案例中，`assertion:family-san-su` 记录“三苏家族与文学群体”。它的 `topology` 是 `hyperedge`，`epistemic_status` 是 `model_predicted`，并通过 `evidence_refs` 指向来源记录。

对应的成员表是：

| 节点 ID | 在这条关系中的角色 |
| --- | --- |
| `person:su-shi` | 核心人物 |
| `person:su-xun` | 父亲 |
| `person:su-zhe` | 弟弟 |
| `group:san-su` | 群体称谓 |

“父亲”在这里是苏洵参与这条关系的角色，并不是对所有相邻节点都成立的边标签。

## 沿着证据引用回到段落

本例的 `evidence:family-san-su` 记录来源 `source/sushi.md`、第 3 行和对应引文。可以在[仓库源文档](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/sushi-document-test/source/sushi.md)中核对。

证据表的用途是保留来源位置，不是替代阅读。模型可能误解段落，输入文档本身也可能有错误；“有来源”与“事实为真”是两回事。

## 一个数据包包含什么

| 文件 | 阅读问题 |
| --- | --- |
| `manifest.json` | 数据包是谁、使用哪个契约、文件是否一致？ |
| `nodes.jsonl` | 有哪些独立实体，它们的标识和名称是什么？ |
| `assertions.jsonl` | 有哪些关系断言，拓扑与认知状态是什么？ |
| `members.jsonl` | 哪个实体属于哪条关系，承担什么角色？ |
| `evidence.jsonl` | 关系引用了哪些来源记录？ |

校验命令另行返回结构检查结果；导出流程也可能附带 `REPORT.md` 等报告。不要把报告中的文件完整性或引用通过率当作语义准确率。

## 三种检查不能混为一谈

1. **结构检查**：文件存在、ID 引用可解析、成员数量与拓扑兼容、文件身份一致。
2. **来源检查**：记录是否能定位到材料中的相关内容，是否缺少精确引文或位置。
3. **语义复核**：实体合并、关系范围和成员角色是否正确，需要阅读材料后判断。

```bash
hk bundle validate output/notes-bundle --quality showcase --json
```

`showcase` 用更严格的要求检查展示用数据。若原始 KA 没有保留精确原文片段，导出并不能补造证据；应说明缺失并回查来源。

布局坐标、悬停和选中状态属于视图，不应回写成成员事实。如何使用这些交互见[三种视图](workbench.md)。
