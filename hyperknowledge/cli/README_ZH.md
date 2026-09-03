# Hyper-Knowledge CLI

> **"停止阅读。开始理解。"**

从非结构化文本中提取结构化知识的强大命令行工具。

---

## ⚡ 快速开始

```bash
# 安装
uv tool install hyperknowledge

# 首次设置
hk config init

# 从文档提取知识
hk parse document.md -o my_ka -l zh

# 可视化知识图谱
hk show my_ka

# 在知识摘要中搜索
hk search my_ka "关键洞察"
```

---

## ⚙️ 配置

### 一键设置（最简单）

```bash
# 只需提供您的 API 密钥 - 默认设置适用于大多数用户
hk config init --api-key YOUR_API_KEY

# 使用自定义 base URL
hk config init -k YOUR_KEY -u https://your-endpoint.com/v1
```

这会自动配置大语言模型和嵌入模型：
- LLM: gpt-4o-mini
- Embedder: text-embedding-3-small

### 交互式设置

```bash
hk config init
```

### 手动配置

对于需要单独配置的高级用户：

```bash
# 配置 LLM
hk config llm --api-key YOUR_KEY --model gpt-4o

# 配置 Embedder
hk config embedder --api-key YOUR_KEY --model text-embedding-3-small
```

### 环境变量

您也可以使用环境变量作为替代方案：

```bash
export OPENAI_API_KEY=your_api_key
export OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
```

环境变量优先于配置文件设置。

### 查看当前配置

```bash
hk config show
```

---

## 📄 Parse 命令

将文档中的知识提取到结构化知识摘要中。

### 基本用法

```bash
# 交互式选择模板进行解析
hk parse document.md -o my_ka -l zh

# 使用特定模板解析
hk parse document.md -o my_ka -t general/knowledge_graph -l zh

# 使用特定方法解析
hk parse document.md -o my_ka -m light_rag
```

### 选项

- `<input>` - 输入文件路径、目录或 `-` 表示标准输入
- `-o, --output` - 输出知识摘要目录（必需）
- `-t, --template` - 模板 ID（省略则进入交互式选择）
- `-m, --method` - 方法模板（例如 `light_rag`、`hyper_rag`）
- `-l, --lang` - 语言（知识模板需要 `zh` 或 `en`）
- `-f, --force` - 强制覆盖现有输出
- `--no-index` - 跳过构建搜索索引

### 列出可用模板

```bash
hk list template
hk list template -l zh  # 按语言筛选
hk list template -a graph  # 按类型筛选
hk list template -q finance  # 按关键词搜索
```

### 列出可用方法

```bash
hk list method
hk list method -q rag  # 按关键词搜索
```

---

## 🔍 其他命令

### 构建搜索索引

语义搜索和聊天功能需要。

```bash
hk build-index my_ka
hk build-index my_ka --force  # 重建现有索引
```

### 搜索知识摘要

在您的知识摘要中执行语义搜索。

```bash
hk search my_ka "关键发现是什么？"
hk search my_ka "关键洞察" -n 5  # 返回前 5 个结果
```

### 与知识摘要对话

询问关于您知识摘要的问题。

```bash
# 单个查询
hk talk my_ka -q "会议讨论了什么？"

# 交互模式
hk talk my_ka -i
```

### 可视化知识图谱

以交互式图谱形式查看您的知识摘要。

```bash
hk show my_ka
```

### 查看知识摘要信息

显示关于您知识摘要的统计信息和元数据。

```bash
hk info my_ka
```

### 向现有 KA 添加知识

将新知识追加到现有知识摘要。

```bash
hk feed my_ka new_document.md
```

---

## 📝 示例

### 示例 1：提取金融数据

```bash
# 配置 API 密钥
hk config init

# 列出金融模板
hk list template -l zh | grep finance

# 提取财报
hk parse earnings_report.md -o finance_ka -t finance/earnings_summary -l zh

# 为搜索构建索引
hk build-index finance_ka

# 搜索洞察
hk search finance_ka "营收增长是多少？"
```

### 示例 2：提取法律合同

```bash
# 列出法律模板
hk list template -l zh | grep legal

# 提取合同信息
hk parse contract.md -o legal_ka -t legal/contract_summary -l zh

# 以知识图谱形式查看
hk show legal_ka
```

### 示例 3：使用方法模板

```bash
# 使用 Light RAG 方法
hk parse document.md -o ka -m light_rag

# 使用 Hyper RAG 方法
hk parse document.md -o ka -m hyper_rag
```

---

## ❓ 常见问题

### Q: 如何选择模板和方法？

**A:** 需要领域特定提取（金融、法律、医疗等）时使用**模板**。想要算法驱动提取（基于 RAG 的方法）时使用**方法**。

### Q: 为什么需要构建索引？

**A:** 索引启用语义搜索和聊天功能。没有它，您仍然可以提取和可视化知识，但搜索和对话命令将无法工作。

### Q: 如何切换语言？

**A:** 使用 `-l` 或 `--lang` 选项：
- `-l zh` 表示中文
- `-l en` 表示英文

### Q: 可以使用自定义 API 端点吗？

**A:** 可以！使用 `--base-url` 配置 API 兼容端点：
```bash
hk config llm --api-key YOUR_KEY --base-url https://your-custom-api.com/v1
```

### Q: 配置存储在哪里？

**A:** 配置存储在 `~/.hk/config.toml`

### Q: 如何更新 API 密钥？

**A:** 只需再次运行配置命令：
```bash
hk config llm --api-key NEW_API_KEY
```

---

## 🆘 需要帮助？

```bash
# 查看所有可用命令
hk --help

# 查看特定命令的帮助
hk parse --help
hk config --help
hk search --help
```

---

## 📚 了解更多

- [完整文档](../README.md)
- [模板库](../templates/)
- [示例](../examples/)
