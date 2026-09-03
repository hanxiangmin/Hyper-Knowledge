# CLI 工作流程指南

本指南通过实际案例带您完成完整的知识提取工作流程。

---

## 场景：研究论文分析

假设您是一位研究人员，想要从学术论文中提取和交互知识。以下是使用 Hyper-Knowledge 的方法。

---

## 步骤 1：准备文档

Hyper-Knowledge 支持 `.md` 和 `.txt` 文件。下载下面的示例研究论文以跟随本指南：

<a href="../../assets/examples/zh/transformer_paper.txt" download class="md-button">📥 下载示例文档</a>

将文件保存为 `transformer_paper.md` 在你的工作目录中。

---

## 步骤 2：提取知识

使用 `parse` 命令提取知识：

```bash
hk parse transformer_paper.md -t general/concept_graph -o ./transformer_kb/ -l zh
```

**发生了什么：**
1. 读取文档并分块（如文档较长）
2. LLM 提取实体和关系
3. 结果保存到 `./transformer_kb/`

**输出结构：**
```
./transformer_kb/
├── data.json       # 提取的知识
├── metadata.json   # 提取元数据
└── index/          # 向量搜索索引（如已构建）
```

---

## 步骤 3：探索知识

### 查看统计信息

```bash
hk info ./transformer_kb/
```

**输出：**
```
Knowledge Abstract Info

Path          ./transformer_kb/
Template      general/concept_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:30:00
Nodes         12
Edges         15
Index         Built
```

### 可视化

```bash
hk show ./transformer_kb/
```

![知识图谱可视化](../../assets/zh_show.jpg)

这将在浏览器中打开交互式图谱，显示：

- **节点**：作者、概念、模型、指标
- **边**：它们之间的关系

---

## 步骤 4：搜索信息

### 语义搜索

即使关键词不完全匹配也能查找信息：

```bash
hk search ./transformer_kb/ "神经网络架构"
```

**结果：**
```
Found 3 result(s):

Result 1:
{
  "name": "Transformer",
  "type": "model",
  "description": "A neural network architecture based solely on attention mechanisms"
}

Result 2:
{
  "name": "Attention Mechanism",
  "type": "concept",
  "description": "Mechanism to draw global dependencies between sequences"
}
...
```

### 特定查询

```bash
hk search ./transformer_kb/ "性能指标" -n 5
```

---

## 步骤 5：与知识对话

### 单个问题

```bash
hk talk ./transformer_kb/ -q "本文的主要贡献是什么？"
```

**响应：**
```
主要贡献是引入了 Transformer 架构，它在机器翻译任务上实现了最先进的成果，
同时比循环或卷积架构更易于并行化，训练时间也显著减少。
```

### 交互模式

```bash
hk talk ./transformer_kb/ -i
```

**会话：**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

> 作者是谁？
本文作者是 Ashish Vaswani、Noam Shazeer、Niki Parmar、Jakob Uszkoreit、
Llion Jones、Aidan N. Gomez、Lukasz Kaiser 和 Illia Polosukhin。

> 他们取得了什么 BLEU 分数？
该模型在 WMT 2014 英德翻译任务上取得了 28.4 的 BLEU 分数。

> exit
Goodbye!
```

---

## 步骤 6：扩展知识库

### 添加另一个文档

```bash
# 下载另一篇论文
curl -o bert_paper.md https://example.com/bert.md

# 添加到现有知识库
hk feed ./transformer_kb/ bert_paper.md
```

### 验证更新

```bash
hk info ./transformer_kb/
```

注意节点/边数增加和时间戳更新。

---

## 步骤 7：重建索引（如需要）

添加文档后，重建搜索索引：

```bash
hk build-index ./transformer_kb/
```

或强制完全重建：

```bash
hk build-index ./transformer_kb/ -f
```

---

## 完整脚本示例

以下是一个自动化整个工作流程的 bash 脚本：

```bash
#!/bin/bash

# 配置
INPUT_FILE="paper.md"
OUTPUT_DIR="./paper_kb/"
TEMPLATE="general/concept_graph"
LANGUAGE="en"

echo "=== Hyper-Knowledge Workflow ==="
echo

# 步骤 1: 解析
echo "Step 1: Extracting knowledge..."
hk parse "$INPUT_FILE" -t "$TEMPLATE" -o "$OUTPUT_DIR" -l "$LANGUAGE"
echo

# 步骤 2: 信息
echo "Step 2: Knowledge base info:"
hk info "$OUTPUT_DIR"
echo

# 步骤 3: 搜索示例
echo "Step 3: Sample search:"
hk search "$OUTPUT_DIR" "主要贡献" -n 2
echo

# 步骤 4: 打开可视化
echo "Step 4: Opening visualization..."
hk show "$OUTPUT_DIR"

echo "=== Workflow Complete ==="
```

---

## 高级：批量处理

一次处理多个文档：

```bash
# 创建输出目录
mkdir -p ./ka/paper1 ./ka/paper2 ./ka/paper3

# 处理每个
hk parse papers/paper1.md -t general/concept_graph -o ./ka/paper1/ -l zh
hk parse papers/paper2.md -t general/concept_graph -o ./ka/paper2/ -l zh
hk parse papers/paper3.md -t general/concept_graph -o ./ka/paper3/ -l zh

# 或使用循环
for file in papers/*.md; do
    name=$(basename "$file" .md)
    hk parse "$file" -t general/concept_graph -o "./ka/$name/" -l zh
done
```

---

## 常见模式

### 模式 1：持续构建知识

```bash
# 初始提取
hk parse initial_doc.md -t general/biography_graph -o ./ka/ -l zh

# 每周更新
hk feed ./ka/ week1_update.md
hk feed ./ka/ week2_update.md
hk feed ./ka/ week3_update.md

# 每月重建
hk build-index ./ka/ -f
```

### 模式 2：多领域项目

```bash
# 技术文档
hk parse api_docs.md -t general/concept_graph -o ./project_kb/tech/ -l zh

# 法律合同
hk parse contract.md -t legal/contract_obligation -o ./project_kb/legal/ -l zh

# 财务报告
hk parse q4_report.md -t finance/earnings_summary -o ./project_kb/finance/ -l zh
```

### 模式 3：比较文档

```bash
# 提取两个版本
hk parse draft_v1.md -t general/concept_graph -o ./ka/v1/ -l zh
hk parse draft_v2.md -t general/concept_graph -o ./ka/v2/ -l zh

# 通过聊天比较
hk talk ./ka/v1/ -q "主要主题是什么？"
hk talk ./ka/v2/ -q "主要主题是什么？"
```

---

## 故障排除提示

| 问题 | 解决方案 |
|-------|----------|
| 提取速度慢 | 长文档会被分块；使用 `--no-index` 在解析时跳过索引 |
| 搜索无结果 | 确保索引已构建：`hk build-index ./ka/` |
| 模板未找到 | 列出可用模板：`hk list template` |
| 内存不足 | 减少配置中的块大小或处理较小的文档 |

---

## 下一步

- 了解[所有 CLI 命令](commands/parse.md)
- 探索[模板库](../templates/index.md)
- 阅读[选择正确的自动类型](../concepts/autotypes.md)
