# CLI 配置参考

Hyper-Knowledge CLI 的配置指南，支持 **OpenAI**、**Anthropic**、**DeepSeek**、**阿里云百炼** 和 **本地 vLLM** 部署方式。

---

## 快速开始

选择你的部署方式，按步骤完成配置。

=== "OpenAI"

    ```bash
    hk config init -p openai -k YOUR_OPENAI_API_KEY
    ```

    这会创建 `~/.hk/config.toml`，使用 OpenAI 预设：
    - **LLM**: `gpt-4o-mini`
    - **嵌入模型**: `text-embedding-3-small`

=== "百炼 (阿里云)"

    ```bash
    hk config init -p bailian -k YOUR_BAILIAN_API_KEY
    ```

    这会创建 `~/.hk/config.toml`，使用百炼预设：
    - **LLM**: `qwen3.6-plus`
    - **嵌入模型**: `text-embedding-v4`

=== "Anthropic (Claude)"

    Anthropic 仅提供 LLM —— 请搭配 OpenAI 兼容嵌入器：

    ```bash
    hk config llm -p anthropic -k YOUR_ANTHROPIC_API_KEY
    hk config embedder -p openai -k YOUR_OPENAI_API_KEY
    ```

    这会创建 `~/.hk/config.toml`：
    - **LLM**: `claude-opus-4-8` (Anthropic)
    - **嵌入模型**: `text-embedding-3-small` (OpenAI)

=== "DeepSeek"

    DeepSeek 仅提供 LLM —— 请搭配 OpenAI 兼容嵌入器：

    ```bash
    hk config llm -p deepseek -k YOUR_DEEPSEEK_API_KEY
    hk config embedder -p openai -k YOUR_OPENAI_API_KEY
    ```

    这会创建 `~/.hk/config.toml`：
    - **LLM**: `deepseek-v4-flash` (DeepSeek，自动关闭思考模式)
    - **嵌入模型**: `text-embedding-3-small` (OpenAI)

=== "本地 vLLM"

    需先启动 LLM 和 Embedding 两个服务，然后分别配置：

    ```bash
    # LLM 服务
    hk config llm -p vllm \
      -u http://localhost:8000/v1 \
      -k dummy \
      -m Qwen/Qwen3.5-9B

    # Embedding 服务
    hk config embedder -p vllm \
      -u http://localhost:8001/v1 \
      -k dummy \
      -m BAAI/bge-m3
    ```

---

## 验证配置

```bash
hk config show
```

=== "云 API (OpenAI / 百炼)"

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │              Hyper-Knowledge Configuration                    │
    ├──────────┬──────────┬─────────────────────┬────────────┬────┤
    │ Service  │ Provider │ Model               │ API Key    │ ...│
    ├──────────┼──────────┼─────────────────────┼────────────┼────┤
    │ LLM      │ bailian  │ qwen3.6-plus        │ sk-xxxx... │ ...│
    │ Embedder │ bailian  │ text-embedding-v4   │ sk-xxxx... │ ...│
    └──────────┴──────────┴─────────────────────┴────────────┴────┘
    ```

=== "本地 vLLM"

    ```
    ┌──────────────────────────────────────────────────────────────────┐
    │                Hyper-Knowledge Configuration                       │
    ├──────────┬──────────┬─────────────────────┬──────────┬───────────┤
    │ Service  │ Provider │ Model               │ API Key  │ Base URL  │
    ├──────────┼──────────┼─────────────────────┼──────────┼───────────┤
    │ LLM      │ vllm     │ Qwen/Qwen3.5-9B     │ dummy... │ localhost…│
    │ Embedder │ vllm     │ BAAI/bge-m3         │ dummy... │ localhost…│
    └──────────┴──────────┴─────────────────────┴──────────┴───────────┘
    ```

---

## CLI 命令参考

### 命令概览

| 命令 | 常用参数 | 描述 |
|------|---------|------|
| `hk config init` | `-p, --provider` — 提供商 preset<br>`-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址 | 初始化配置（首次使用） |
| `hk config llm` | `-p, --provider` — 提供商<br>`-m, --model` — 模型名称<br>`-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址<br>`--show` — 查看当前配置<br>`--unset` — 清除配置 | 配置 LLM |
| `hk config embedder` | `-p, --provider` — 提供商<br>`-m, --model` — 模型名称<br>`-k, --api-key` — API 密钥<br>`-u, --base-url` — 自定义 API 地址<br>`--show` — 查看当前配置<br>`--unset` — 清除配置 | 配置嵌入模型 |
| `hk config show` | — | 查看完整配置 |

### 常见用法示例

**交互式初始化（推荐首次使用）：**

```bash
hk config init
# 按提示选择提供商、输入模型名和 API 密钥
```

**查看 LLM 配置：**

```bash
hk config llm --show
```

**清除配置（重置为默认值）：**

```bash
hk config llm --unset
hk config embedder --unset
```

---

## 分平台配置示例

=== "OpenAI"

    ```bash
    # 一键配置
    hk config init -p openai -k sk-your-key

    # 或换模型
    hk config llm -p openai -k sk-your-key -m gpt-4o
    ```

=== "百炼 (阿里云)"

    ```bash
    # 一键配置（默认 qwen3.6-plus + text-embedding-v4）
    hk config init -p bailian -k sk-your-key

    # 或换模型
    hk config llm -p bailian -k sk-your-key -m qwen-plus
    ```

=== "Anthropic (Claude)"

    ```bash
    # LLM 用 Anthropic，Embedding 用 OpenAI
    hk config llm -p anthropic -k sk-ant-your-key
    hk config embedder -p openai -k sk-your-openai-key
    ```

=== "DeepSeek"

    ```bash
    # LLM 用 DeepSeek，Embedding 用 OpenAI
    hk config llm -p deepseek -k sk-your-key
    hk config embedder -p openai -k sk-your-openai-key
    ```

=== "本地 vLLM"

    ```bash
    # 需先启动服务，然后分别配置
    hk config llm -p vllm \
      -u http://localhost:8000/v1 \
      -k dummy \
      -m Qwen/Qwen3.5-9B

    hk config embedder -p vllm \
      -u http://localhost:8001/v1 \
      -k dummy \
      -m BAAI/bge-m3
    ```

=== "混合部署"

    LLM 和 Embedder 可以使用不同提供商：

    ```bash
    # LLM 用百炼，Embedding 用本地 vLLM
    hk config llm -p bailian -k sk-your-key
    hk config embedder -p vllm \
      -u http://localhost:8001/v1 \
      -k dummy \
      -m BAAI/bge-m3

    # 或 LLM 用本地，Embedding 用百炼
    hk config llm -p vllm \
      -u http://localhost:8000/v1 \
      -k dummy \
      -m Qwen/Qwen3.5-9B
    hk config embedder -p bailian -k sk-your-key
    ```

---

## 配置文件详解

运行 `hk config init` 时会自动创建 `~/.hk/config.toml`。

### 文件位置

- **Linux/macOS**: `~/.hk/config.toml`
- **Windows**: `%USERPROFILE%\.hk\config.toml`

### 配置格式

=== "云 API — 百炼"

    ```toml
    [llm]
    provider = "bailian"
    model = "qwen3.6-plus"
    api_key = "sk-your-api-key"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    [embedder]
    provider = "bailian"
    model = "text-embedding-v4"
    api_key = ""
    base_url = ""
    ```

=== "本地 vLLM"

    ```toml
    [llm]
    provider = "vllm"
    model = "Qwen/Qwen3.5-9B"
    api_key = "dummy"
    base_url = "http://localhost:8000/v1"

    [embedder]
    provider = "vllm"
    model = "BAAI/bge-m3"
    api_key = "dummy"
    base_url = "http://localhost:8001/v1"
    ```

=== "混合部署"

    ```toml
    [llm]
    provider = "bailian"
    model = "qwen3.6-plus"
    api_key = "sk-your-api-key"
    base_url = ""

    [embedder]
    provider = "vllm"
    model = "BAAI/bge-m3"
    api_key = "dummy"
    base_url = "http://localhost:8001/v1"
    ```

### 配置项说明

| 节 | 键 | 描述 | 默认值 |
|---|-----|------|--------|
| `[llm]` | `provider` | 提供商 preset | — |
| `[llm]` | `model` | LLM 模型名称 | 取决于 provider preset |
| `[llm]` | `api_key` | API 密钥 | 必填 |
| `[llm]` | `base_url` | API 基础 URL | 取决于 provider preset |
| `[embedder]` | `provider` | 提供商 preset | — |
| `[embedder]` | `model` | 嵌入模型名称 | 取决于 provider preset |
| `[embedder]` | `api_key` | API 密钥（留空继承 llm） | — |
| `[embedder]` | `base_url` | API 基础 URL（留空继承 llm） | — |

> 不同 provider 的默认模型见 [Provider 系统](../concepts/provider-system.md) 兼容性表格。

---

## 环境变量

以下环境变量可作为配置的备选方案：

| 变量 | 映射到 | 示例 |
|------|--------|------|
| `OPENAI_API_KEY` | `llm.api_key`, `embedder.api_key` | `sk-...` |
| `OPENAI_BASE_URL` | `llm.base_url` | `https://api.openai.com/v1` |

**优先级说明：** 环境变量优先级高于配置文件，低于命令行参数。

**使用场景：**
- 临时切换 API 密钥
- CI/CD 环境中注入密钥
- 不想在配置文件中硬编码密钥

---

## 故障排除

=== "云 API 问题"

    **"API key not found"**

    ```bash
    hk config init -p bailian -k YOUR_API_KEY
    ```

    **"The model does not exist" / 404**

    检查配置的模型名是否在对应平台可用。百炼可用模型见 [Provider 系统](../concepts/provider-system.md)。

    **"Failed to connect to API"**

    ```bash
    # 检查配置
    hk config llm --show

    # 重新设置 base_url
    hk config llm --base-url https://dashscope.aliyuncs.com/compatible-mode/v1
    ```

=== "本地 vLLM 问题"

    **"Connection refused"**

    vLLM 服务未启动或服务已停止：

    ```bash
    # 检查服务是否运行
    curl http://localhost:8000/v1/models
    curl http://localhost:8001/v1/models

    # 重新启动服务
    ```

    **"CUDA out of memory"**

    降低 `--gpu-memory-utilization` 或换用更小的模型/量化版本。

---

## 另请参见

- [`hk config`](commands/config.md) — 详细的配置命令说明
- [Provider 系统](../concepts/provider-system.md) — 完整模型兼容性列表
- [安装指南](../getting-started/installation.md) — 初始安装步骤
