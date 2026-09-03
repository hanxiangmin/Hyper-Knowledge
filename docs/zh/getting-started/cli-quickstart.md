# CLI 快速入门

使用命令行在 5 分钟内完成首次知识提取。

---

## 前置要求

- [Hyper-Knowledge 已安装](installation.md)
- 一个待提取的文本文档（我们将使用示例）

---

## 第 1 步：配置 API 密钥

选择你的部署方式并运行对应的配置命令：

=== "OpenAI"

    ```bash
    hk config init -p openai -k YOUR_OPENAI_API_KEY
    ```

=== "百炼 (阿里云)"

    ```bash
    hk config init -p bailian -k YOUR_BAILIAN_API_KEY
    ```

=== "DeepSeek"

    ```bash
    hk config llm -p deepseek -k YOUR_DEEPSEEK_API_KEY
    hk config embedder -p openai -k YOUR_OPENAI_API_KEY
    ```

=== "本地 vLLM"

    ```bash
    hk config llm -p vllm \
      -u http://localhost:8000/v1 \
      -k dummy \
      -m Qwen/Qwen3.5-9B

    hk config embedder -p vllm \
      -u http://localhost:8001/v1 \
      -k dummy \
      -m BAAI/bge-m3
    ```

=== "Anthropic (Claude)"

    Anthropic 仅提供 LLM —— 搜索/对话功能需搭配 OpenAI 兼容的 embedder：

    ```bash
    hk config llm -p anthropic -k YOUR_ANTHROPIC_API_KEY
    hk config embedder -p openai -k YOUR_OPENAI_API_KEY
    ```

这会在 `~/.hk/config.toml` 创建配置文件，只需配置一次。

> **注意：** Anthropic 和 DeepSeek 仅提供 LLM。如需使用搜索（`hk search`）和对话（`hk talk`）功能，请按上文所示搭配 OpenAI 兼容的 embedder。

---

## 第 2 步：下载示例文档

```bash
# 下载示例传记
curl -o sushi.md https://raw.githubusercontent.com/hanxiangmin/Hyper-Knowledge/main/examples/zh/sushi.md
```

或创建一个简单的测试文件：

```bash
cat > sample.txt << 'EOF'
苏轼，字子瞻，号东坡居士，是北宋时期最杰出的文学家、书画家、政治家。
他与父亲苏洵、弟弟苏辙并称"三苏"，同列唐宋八大家。

苏轼于1037年出生于眉州眉山。1057年科举中举，受欧阳修赏识。
后因乌台诗案被贬黄州，创作了大量千古传诵的名篇。

代表作：《念奴娇·赤壁怀古》《水调歌头·明月几时有》《赤壁赋》

苏轼一生宦海浮沉，历任杭州、密州、徐州、湖州等地知州。
在杭州任上，他疏浚西湖，修筑苏堤，留下"欲把西湖比西子"的千古名句。
晚年因新党执政被贬至惠州、儋州，仍心系百姓，兴办学堂，传播中原文化。

其文学成就横跨诗、词、文、赋，书法位列"宋四家"之首，
绘画开文人画先河，是中国历史上罕见的全才式人物。
EOF
```

---

## 第 3 步：提取知识

运行 `parse` 命令提取知识：

```bash
hk parse sushi.md -t general/biography_graph -o ./output/ -l zh
```

参数说明：
- `-t general/biography_graph` — 使用传记图谱模板
- `-o ./output/` — 保存结果到输出目录
- `-l zh` — 使用中文处理

**输出示例：**
```
Input: sushi.md
Output: ./output/
Template: general/biography_graph
Language: en
Build Index: Yes

Template resolved: Biography Graph Template
✓ Knowledge extracted to ./output/

What's next?
  hk show ./output/                    # 可视化知识图谱
  hk feed ./output/ <new_document>     # 追加更多文档
  hk search ./output/ "关键词"        # 语义搜索
  hk talk ./output/ -i                 # 交互式对话
```

---

## 第 4 步：可视化知识图谱

```bash
hk show ./output/
```

这会在浏览器中打开交互式可视化，显示：
- **实体**（人物、地点、事件）作为节点
- **关系** 作为连接节点的边

![知识图谱可视化](../../assets/zh_show.jpg)

---

## 第 5 步：搜索知识库

```bash
hk search ./output/ "苏轼的代表作有哪些"
```

**输出示例：**
```
Found 3 result(s):

Result 1:
{
  "name": "苏轼",
  "type": "人物",
  "description": "北宋文学家、书画家，号东坡居士"
}
...
```

---

## 第 6 步：与知识库对话

交互模式：

```bash
hk talk ./output/ -i
```

或提问单个问题：

```bash
hk talk ./output/ -q "用三句话总结苏轼的生平"
```

---

## 第 7 步：增量添加知识

有更多文档？无需重新处理即可添加：

```bash
hk feed ./output/ additional_document.md
```

然后可视化更新后的知识：

```bash
hk show ./output/
```

---

## 完整工作流程

以下是典型的工作流程：

```bash
# 1. 提取知识
hk parse document.md -t general/biography_graph -o ./output/ -l zh

# 2. 可视化
hk show ./output/

# 3. 搜索
hk search ./output/ "你的查询"

# 4. 对话
hk talk ./output/ -i

# 5. 添加更多文档
hk feed ./output/ another_document.md

# 6. 如需重新构建索引
hk build-index ./output/
```

---

## 下一步

- [CLI 工作流程指南](../cli/workflow.md) — 完整工作流程演示
- [所有 CLI 命令](../cli/index.md) — 详细命令参考
- [模板库](../templates/index.md) — 找到适合您用例的模板

---

## 故障排除

**"No API key found"**
→ 运行 `hk config init -p openai -k YOUR_OPENAI_API_KEY`（或使用 `-p bailian`、`-p deepseek` 等）

**"Template not found"**
→ 使用 `hk list template` 查看可用模板

**"Output directory already exists"**
→ 添加 `-f` 标志强制覆盖，或选择不同的输出路径
