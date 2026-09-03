# hk parse

从文档中提取知识并保存到知识库。

---

## 概要

```bash
hk parse INPUT [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `INPUT` | 输入文件路径、目录或 `-` 表示标准输入 |

## 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--output` | `-o` | 输出目录（必填） |
| `--template` | `-t` | 要使用的模板（省略以进行交互式选择） |
| `--method` | `-m` | 方法模板（例如 `light_rag`、`graph_rag`） |
| `--lang` | `-l` | 语言：`zh` 或 `en`（知识模板必填） |
| `--force` | `-f` | 强制覆盖现有输出 |
| `--no-index` | — | 跳过构建搜索索引 |

---

## 示例

### 基本用法

从单个文件提取：

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l zh
```

### 交互式模板选择

省略 `-t` 以从可用模板中选择：

```bash
hk parse document.md -o ./output/ -l zh

# 您将看到：
# Select a template:
#   [1] general/biography_graph
#   [2] general/graph
#   [3] finance/earnings_summary
#   ...
# Enter number or search keyword: 
```

### 处理目录

从目录中的所有 `.md` 和 `.txt` 文件提取：

```bash
hk parse ./documents/ -t general/concept_graph -o ./output/ -l zh
```

文件按字母顺序组合后进行提取。

### 使用方法而非模板

使用底层提取方法：

```bash
hk parse document.md -m light_rag -o ./output/
```

方法始终使用英文提示。

### 强制覆盖

覆盖现有输出目录：

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l zh -f
```

### 跳过索引构建

如果您不需要搜索/聊天，可以加快提取速度：

```bash
hk parse document.md -t general/biography_graph -o ./output/ -l zh --no-index
```

之后使用 `hk build-index` 构建索引。

### 从标准输入读取

```bash
cat document.md | hk parse - -t general/biography_graph -o ./output/ -l zh
```

---

## 输出结构

```
./output/
├── data.json           # 提取的知识（实体、关系等）
├── metadata.json       # 提取元数据
│   ├── template        # 使用的模板
│   ├── lang           # 语言
│   ├── created_at     # 创建时间戳
│   └── updated_at     # 最后更新时间戳
└── index/             # 向量搜索索引（如已构建）
    ├── index.faiss
    └── docstore.json
```

---

## 语言支持

模板支持多种语言：

```bash
# 英文
hk parse doc.md -t general/biography_graph -o ./output/ -l zh -o ./output/

# 中文
hk parse doc.md -t general/biography_graph -l zh -o ./output/
```

选择与文档匹配的语言以获得最佳效果。

---

## 常见用例

### 研究论文

```bash
hk parse paper.md -t general/concept_graph -o ./paper_kb/ -l zh
```

### 传记

```bash
hk parse biography.md -t general/biography_graph -o ./output/ -l zh
```

### 法律合同

```bash
hk parse contract.md -t legal/contract_obligation -o ./contract_kb/ -l zh
```

### 财务报告

```bash
hk parse earnings.md -t finance/earnings_summary -o ./finance_kb/ -l zh
```

---

## 错误处理

### "输出目录已存在"

输出目录存在且不为空。解决方案：

1. 使用 `-f` 强制覆盖
2. 选择不同的输出路径
3. 先删除现有目录

### "模板未找到"

指定的模板不存在。解决方案：

1. 列出可用模板：`hk list template`
2. 使用交互式选择（省略 `-t`）
3. 检查模板路径拼写

### "需要语言"

知识模板需要语言参数。方法不需要：

```bash
# 模板 - 需要 -l
hk parse doc.md -t general/biography_graph -o ./output/ -l zh

# 方法 - 不需要 -l
hk parse doc.md -m light_rag -o ./out/
```

---

## 最佳实践

1. **选择正确的模板** — 匹配您的文档类型
2. **使用正确的语言** — 提高提取质量
3. **组织输出** — 使用描述性目录名
4. **批量处理时跳过索引** — 使用 `--no-index`，最后统一构建

---

## 另请参见

- [`hk feed`](feed.md) — 增量添加文档
- [`hk build-index`](build-index.md) — 构建搜索索引
- [`hk list`](list.md) — 列出可用模板
- [模板库](../../templates/index.md)
