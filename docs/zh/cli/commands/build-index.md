# hk build-index

为知识库构建或重建向量搜索索引。

---

## 概要

```bash
hk build-index KA_PATH [OPTIONS]
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `KA_PATH` | 知识库目录的路径 |

## 选项

| 选项 | 简写 | 描述 |
|--------|-------|-------------|
| `--force` | `-f` | 即使索引存在也强制重建 |

---

## 描述

为语义搜索和聊天功能构建向量搜索索引：

1. **读取所有实体/关系** — 从知识库数据中
2. **生成嵌入** — 使用配置的嵌入模型
3. **构建 FAISS 索引** — 用于快速相似度搜索
4. **保存到磁盘** — 在 `index/` 子目录中

**必需用于**：`hk search` 和 `hk talk` 命令。

---

## 示例

### 构建索引

```bash
hk build-index ./output/
```

**输出：**
```
Template: general/biography_graph
Language: en

Success! Index built for ./output/

Now you can:
  hk search ./output/ "关键词"  # Semantic search
  hk talk ./output/ -i           # Interactive chat
```

### 强制重建

如果索引损坏或您想重建：

```bash
hk build-index ./output/ -f
```

---

## 何时构建索引

### Parse 后（默认）

默认情况下，`hk parse` 会自动构建索引：

```bash
hk parse doc.md -t general/biography_graph -o ./ka/ -l zh
# 索引自动构建
```

如果不需要搜索/聊天，使用 `--no-index` 跳过：

```bash
hk parse doc.md -t general/biography_graph -o ./ka/ -l zh --no-index
```

### Feed 后

喂养新文档后始终重建：

```bash
hk feed ./ka/ new_doc.md
hk build-index ./ka/
```

### 手动更改后

如果您手动修改了 `data.json`：

```bash
hk build-index ./ka/ -f
```

---

## 索引存储

索引存储在知识库目录中：

```
./ka/
├── data.json
├── metadata.json
└── index/              # 索引目录
    ├── index.faiss     # FAISS 向量索引
    └── docstore.json   # 文档存储映射
```

---

## 性能

### 构建时间

| 知识库大小 | 预计构建时间 |
|---------------------|----------------------|
| 小型（< 100 项） | < 5 秒 |
| 中型（100-1000） | 5-30 秒 |
| 大型（1000+） | 30+ 秒 |

### 搜索速度

一旦构建完成，搜索非常快：

```bash
hk search ./ka/ "查询"  # 通常 < 1 秒
```

---

## 最佳实践

1. **Feed 后构建** — `hk feed` 后索引会变旧
2. **批量处理使用 `--no-index`** — 所有解析后统一构建一次
3. **有问题时强制重建** — 如果搜索返回意外结果，使用 `-f`
4. **备份大型索引** — `index/` 目录可能很大

---

## 批量工作流程

高效处理多个文档：

```bash
# 解析所有文件，不构建索引
hk parse doc1.md -t general/biography_graph -o ./ka/ -l zh --no-index
hk feed ./ka/ doc2.md
hk feed ./ka/ doc3.md

# 最后统一构建索引
hk build-index ./ka/

# 现在可以进行搜索/聊天
hk search ./ka/ "查询"
hk talk ./ka/ -q "问题"
```

---

## 故障排除

### "索引已存在"

使用 `-f` 强制重建：

```bash
hk build-index ./ka/ -f
```

### "索引构建失败"

检查：
1. 知识库有数据：`hk info ./ka/`
2. API 密钥已配置：`hk config show`
3. 有足够的磁盘空间存储索引

### 搜索仍然不工作

尝试强制重建：

```bash
hk build-index ./ka/ -f
```

---

## 另请参见

- [`hk parse`](parse.md) — 可选索引构建的解析
- [`hk feed`](feed.md) — 添加文档（需要重建）
- [`hk search`](search.md) — 搜索索引
- [`hk talk`](talk.md) — 使用索引聊天
