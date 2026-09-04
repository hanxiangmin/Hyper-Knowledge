# 苏轼案例：从人物到一件事

用一份传记材料说明建模和阅读方式，比只看一张复杂的图更直接。本例选取十组代表性关系，不追求穷尽整份传记。

[查看输入材料](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/sushi-document-test/source/sushi.md) · [查看规范化数据包](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-document-test/bundle)

## 第一步：辨认共享人物

包络视图中的苏轼节点跨越多条超边。节点复用表示同一实体参与不同事件；并不表示这些事件彼此等价。

切换到关联视图并选中苏轼，可以只查看他所属的十条关系。再选中“三苏家族与文学群体”，视图展开苏轼、苏洵、苏辙和三苏四个成员。

## 第二步：检查角色，而不只是名字

在这条超边中，四个成员的角色依次是核心人物、父亲、弟弟和群体称谓。“三苏”是一个文学群体，不应因为与苏洵同处一条超边而合并成同一个节点。

打开来源详情，可沿 `evidence:family-san-su` 回到输入文档第 3 行。接着在矩阵里核对这四个成员是否落在同一列。

## 第三步：把多段经历分开

曾经将多个年份、地点汇总到一条“晚年轨迹”关系，会让对应方式不清楚。本例现在采用以下组织：

| 事件超边 | 人物 | 时间 | 地点及角色 |
| --- | --- | --- | --- |
| 贬谪惠州 | 苏轼／被贬者 | 1094 年 | 惠州／贬谪地 |
| 贬谪儋州 | 苏轼／被贬者 | 1097 年 | 儋州／贬谪地 |
| 北归 | 苏轼／北归者 | 1101 年 | 常州／到达地 |

这比“1097 年 + 1101 年 + 儋州 + 常州”集中挂在同一条关系下更容易核对。时间顺序可以记录为属性，不必改变无向成员关系。

## 在本地打开同一份案例

在仓库根目录、已安装的运行环境中执行：

```bash
hk bundle validate examples/sushi-document-test/bundle --quality showcase --json
hk visualize examples/sushi-document-test/bundle -o output/sushi-workbench.html --view contour --no-open --json
```

然后打开 `output/sushi-workbench.html`。这两步读取已有结构，不重新抽取，也不调用远程模型。

## 这个例子能说明什么

当前案例包含 **38 个节点、10 条超边、49 条成员关联**，十条超边均有来源记录。它展示实体拆分、事件范围、共享成员和来源追溯的工作方式。

结构由 Codex 生成，并标记为 `model_predicted`；输入是二手传记材料，未进行独立历史核验。因此这不是人工金标准，也不是抽取准确率实验。迁移到自己的领域时，仍需检查实体身份和事件边界。
