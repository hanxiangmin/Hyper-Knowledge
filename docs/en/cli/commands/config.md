# hk config

Manage Hyper-Knowledge configuration for LLM and embedder settings.

---

## Synopsis

```bash
hk config [COMMAND] [OPTIONS]
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize configuration (uses provider preset to auto-fill model and URL) |
| `show` | Display current configuration |
| `llm` | Configure LLM settings |
| `embedder` | Configure embedder settings |

---

## hk config init

Initialize configuration. This is the **lazy one-step setup** — if you pass `-p` and `-k`, it skips all prompts and uses built-in presets:

- **OpenAI preset**: `gpt-4o-mini` + `text-embedding-3-small`
- **Bailian preset**: `qwen3.6-plus` + `text-embedding-v4`
- **DeepSeek preset**: `deepseek-v4-flash` (LLM only — no embedder preset)
- **Anthropic preset**: `claude-opus-4-8` (LLM only — no embedder preset, pair with an OpenAI-compatible embedder)

```bash
hk config init [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--provider` | `-p` | Provider preset (`openai` / `anthropic` / `deepseek` / `bailian` / `vllm`) |
| `--api-key` | `-k` | API key for both LLM and embedder |
| `--base-url` | `-u` | Custom API base URL (optional) |

### Examples

#### Lazy one-step setup (recommended)

```bash
# OpenAI
hk config init -p openai -k sk-your-api-key-here

# Bailian (Alibaba Cloud)
hk config init -p bailian -k sk-your-api-key-here

# DeepSeek (LLM only — pair with an OpenAI-compatible embedder)
hk config llm -p deepseek -k sk-your-deepseek-key
hk config embedder -p openai -k sk-your-openai-key

# Anthropic (LLM only — pair with an OpenAI-compatible embedder)
hk config llm -p anthropic -k sk-your-anthropic-key
hk config embedder -p openai -k sk-your-openai-key
```

This saves the preset's default model and API URL automatically.

#### With custom base URL

```bash
hk config init -p openai -k sk-your-key -u https://api.openai.com/v1
```

#### Interactive setup

```bash
hk config init
# Prompts for model names and API keys step by step
```

---

## hk config show

Display current configuration.

```bash
hk config show
```

**Output:**

```
┌──────────────────────────────────────────────────────────────────┐
│                Hyper-Knowledge Configuration                       │
├──────────┬──────────┬─────────────────────┬──────────┬───────────┤
│ Service  │ Provider │ Model               │ API Key  │ Base URL  │
├──────────┼──────────┼─────────────────────┼──────────┼───────────┤
│ LLM      │ bailian  │ qwen3.6-plus        │ sk-xx... │ dashsc... │
│ Embedder │ bailian  │ text-embedding-v4   │ sk-xx... │ dashsc... │
└──────────┴──────────┴─────────────────────┴──────────┴───────────┘
```

---

## hk config llm

Configure LLM settings individually.

```bash
hk config llm [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--provider` | `-p` | Provider preset (e.g. `openai`, `anthropic`, `deepseek`, `bailian`, `vllm`) |
| `--api-key` | `-k` | LLM API key |
| `--model` | `-m` | LLM model name |
| `--base-url` | `-u` | Custom API base URL |
| `--show` | — | Show current LLM configuration |
| `--unset` | — | Clear LLM configuration |

### Examples

```bash
# View LLM config
hk config llm --show

# Update LLM model (OpenAI)
hk config llm -p openai --model gpt-4o

# Update LLM model (Bailian)
hk config llm -p bailian --model qwen-plus

# Configure local vLLM
hk config llm -p vllm \
  --api-key dummy \
  --base-url http://localhost:8000/v1 \
  --model Qwen/Qwen3.5-9B

# Reset LLM config
hk config llm --unset
```

---

## hk config embedder

Configure embedder settings individually.

```bash
hk config embedder [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--provider` | `-p` | Provider preset (e.g. `openai`, `anthropic`, `deepseek`, `bailian`, `vllm`) |
| `--api-key` | `-k` | Embedder API key |
| `--model` | `-m` | Embedder model name |
| `--base-url` | `-u` | Custom API base URL |
| `--show` | — | Show current embedder configuration |
| `--unset` | — | Clear embedder configuration |

### Examples

```bash
# View embedder config
hk config embedder --show

# Use a larger OpenAI embedding model
hk config embedder -p openai --model text-embedding-3-large

# Configure local vLLM embedder
hk config embedder -p vllm \
  --api-key dummy \
  --base-url http://localhost:8001/v1 \
  --model BAAI/bge-m3

# Reset embedder config
hk config embedder --unset
```

---

## Configuration File

Configuration is stored at:

- **Linux/macOS**: `~/.hk/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### Examples

=== "Bailian (Alibaba Cloud)"

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

=== "Local vLLM"

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

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key fallback for LLM and embedder |
| `OPENAI_BASE_URL` | Custom API base URL fallback |

**Priority (highest first):** command-line flags → environment variables → config file → defaults.

---

## Troubleshooting

### "API key not found"

```bash
hk config init -k your-api-key
```

Or:

```bash
export OPENAI_API_KEY=your-api-key
```

### "Configuration file not found"

```bash
hk config init -k your-api-key
```

---

## See Also

- [Configuration Reference](../configuration.md) — Detailed configuration options
- [Installation Guide](../../getting-started/installation.md) — Initial setup
