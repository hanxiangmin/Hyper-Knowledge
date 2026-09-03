# Provider 配置指南

将 Hyper-Knowledge 配置为使用 OpenAI、阿里云百炼或本地 vLLM 部署。

---

## 统一示例

以下三个平台运行**相同的提取任务**，仅客户端配置（前 3 行）不同。

### OpenAI

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("openai", api_key="sk-xxx")
```

### 阿里云百炼

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client("bailian", api_key="sk-xxx")
# 或换模型: create_client("bailian:qwen3.6-plus", api_key="sk-xxx")
```

### Anthropic (Claude)

```python
from hyperknowledge import create_client, AutoGraph

# Anthropic 仅提供 LLM——请搭配 OpenAI 兼容嵌入器。
# 密钥：LLM 使用 ANTHROPIC_API_KEY（或 CLAUDE_API_KEY），嵌入使用 OPENAI_API_KEY。
llm, emb = create_client(
    llm="anthropic",  # 默认模型：claude-opus-4-8（用 "anthropic:<model>" 覆盖）
    embedder="openai:text-embedding-3-small",
)
```

### DeepSeek

```python
from hyperknowledge import create_client, AutoGraph

# DeepSeek 兼容 OpenAI 协议，但无嵌入接口——请搭配 OpenAI 兼容嵌入器。
# V4 模型默认开启 "thinking" 模式，Hyper-Knowledge 会自动关闭以保证结构化抽取可用。
llm, emb = create_client(
    llm="deepseek",  # 默认：deepseek-v4-flash；用 "deepseek:deepseek-v4-pro" 覆盖
    embedder="openai:text-embedding-3-small",
)
```

### 本地 vLLM

```python
from hyperknowledge import create_client, AutoGraph

llm, emb = create_client(
    llm="vllm:Qwen3.5-9B@http://localhost:8000/v1",
    embedder="vllm:bge-m3@http://localhost:8001/v1",
    api_key="dummy",
)
```

### 提取任务（三个平台共用）

```python
graph = AutoGraph(
    instruction="提取文本中的人物及其关系",
    llm_client=llm,
    embedder=emb,
    node_key_extractor=lambda n: n.name,
    edge_key_extractor=lambda e: (e.source, e.target, e.type),
    nodes_in_edge_extractor=lambda e: (e.source, e.target),
)

text = "张三创立了字节跳动，李四担任 CEO。"
graph.parse(text)
print(f"节点: {len(graph.nodes)}, 关系: {len(graph.edges)}")
```

---

## CLI 等价配置

| 平台 | 命令 |
|------|------|
| **OpenAI** | `hk config init -p openai -k sk-xxx` |
| **百炼** | `hk config init -p bailian -k sk-xxx` |
| **Anthropic** | `hk config llm -p anthropic -k sk-ant-xxx` + `hk config embedder -p openai -k sk-xxx` |
| **DeepSeek** | `hk config llm -p deepseek -k sk-xxx` + `hk config embedder -p openai -k sk-xxx` |
| **vLLM** | `hk config init` → 选择「本地 vLLM」 |
| **混合部署**（LLM=百炼 + Embedding=本地） | `hk config llm -p bailian -k sk-xxx` + `hk config embedder -p vllm -u http://localhost:8001/v1 -k dummy` |

---

## 字符串简写格式

`create_client()` 支持紧凑的字符串语法，快速配置：

| 格式 | 示例 | 结果 |
|------|------|------|
| `provider` | `"bailian"` | 使用预设的 LLM + Embedding 默认值 |
| `provider:model` | `"bailian:qwen3.6-plus"` | 覆盖 LLM 模型，保留预设 Embedding |
| `provider:model@url` | `"vllm:Qwen3.5-9B@localhost:8000/v1"` | 完整手动指定 |

---

## 使用配置文件

如果你偏好基于文件的配置，运行一次 `hk config init`，然后使用 `Template.create()` 或 `get_client()`：

```python
from hyperknowledge import get_client, AutoGraph

llm, emb = get_client()  # 读取 ~/.hk/config.toml
graph = AutoGraph(..., llm_client=llm, embedder=emb)
```

---

## 另请参阅

- [Provider 系统与本地模型支持](../../concepts/provider-system.md) — 完整兼容性表格和 vLLM 部署指南
- [CLI 配置参考](../../cli/configuration.md) — 完整的 `hk config` 命令参考
