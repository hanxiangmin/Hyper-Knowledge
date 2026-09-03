# 故障排除

常见问题的解决方案。

---

## 安装问题

### pip 安装失败

**问题**：安装时出现错误

**解决方案**：
1. 升级 pip：`pip install --upgrade pip`
2. 使用 Python 3.11+：`python --version`
3. 在虚拟环境中安装：
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
   ```

### ImportError: No module named 'hyperknowledge'

**问题**：安装后无法导入

**解决方案**：
1. 检查 Python 版本：`python --version`（需要 3.11+）
2. 验证安装：`pip list | grep hyper`
3. 检查虚拟环境是否已激活
4. 重新安装：`pip install --force-reinstall "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"`

---

## 配置问题

### API 密钥未找到

**错误**：`No API key configured`

**解决方案**：

1. **CLI 配置**（推荐）：
   ```bash
   # OpenAI / 百炼（一步到位）
   hk config init -p openai -k YOUR_API_KEY
   
   # Anthropic / DeepSeek（LLM + 独立嵌入器）
   hk config llm -p deepseek -k YOUR_DEEPSEEK_API_KEY
   hk config embedder -p openai -k YOUR_OPENAI_API_KEY
   ```

2. **环境变量**：
   ```bash
   export OPENAI_API_KEY=your-api-key
   export ANTHROPIC_API_KEY=your-api-key    # 用于 Anthropic
   export DEEPSEEK_API_KEY=your-api-key     # 用于 DeepSeek
   ```

3. **验证配置**：
   ```bash
   hk config show
   ```

### API 密钥无效

**错误**：`Authentication failed`

**解决方案**：
1. 验证密钥是否正确
2. 检查是否有额外的空格
3. Anthropic：确保使用 `ANTHROPIC_API_KEY`（而非 `OPENAI_API_KEY`）
4. DeepSeek：确保使用 `DEEPSEEK_API_KEY`（而非 `OPENAI_API_KEY`）
5. 检查密钥是否有可用额度/配额

---

## 运行问题

### 模板未找到

**错误**：`Template 'xxx' not found`

**解决方案**：

1. **列出可用模板**：
   ```bash
   hk list template
   ```

2. **检查拼写**：
   ```bash
   # 正确
   hk parse doc.md -t general/biography_graph
   
   # 错误
   hk parse doc.md -t general/biography
   ```

3. **使用 Python 搜索**：
   ```python
   from hyperknowledge import Template
   templates = Template.list(filter_by_query="bio")
   ```

### 需要指定语言

**错误**：`--lang is required`

**解决方案**：
```bash
# 添加语言参数
hk parse doc.md -t general/biography_graph -o ./out/ -l zh
```

注意：方法模板不需要语言参数。

### 输出目录已存在

**错误**：`Output directory already exists`

**解决方案**：

1. **强制覆盖**：
   ```bash
   hk parse doc.md -t general/graph -o ./out/ -l zh -f
   ```

2. **使用不同目录**：
   ```bash
   hk parse doc.md -t general/graph -o ./out2/ -l zh
   ```

3. **删除现有目录**：
   ```bash
   rm -rf ./out/
   hk parse doc.md -t general/graph -o ./out/ -l zh
   ```

---

## 索引和搜索问题

### 索引未找到

**错误**：`Search index not built`

**解决方案**：
```bash
hk build-index ./output/
```

### 搜索返回空结果

**问题**：`hk search` 找不到结果

**解决方案**：

1. **验证索引是否存在**：
   ```bash
   hk info ./output/
   # 应该显示：Index: Built
   ```

2. **尝试不同的查询**：
   ```bash
   hk search ./output/ "不同的关键词"
   ```

3. **增加 top_k**：
   ```bash
   hk search ./output/ "查询" -n 10
   ```

4. **检查数据是否存在**：
   ```bash
   hk info ./output/
   # 应该显示 Nodes > 0
   ```

### 对话失败

**错误**：`Chat failed: index not found`

**解决方案**：
```bash
hk build-index ./output/
hk talk ./output/ -q "你的问题"
```

---

## 性能问题

### 提取速度非常慢

**问题**：处理时间过长

**解决方案**：

1. **批量处理时跳过索引**：
   ```bash
   hk parse doc.md -t general/graph -o ./out/ -l zh --no-index
   ```

2. **减少分块大小**（Python）：
   ```python
   ka = Template.create("general/graph", "zh")
   ka.chunk_size = 1024  # 默认：2048
   ```

3. **减少工作线程**（如果达到速率限制）：
   ```python
   ka = Template.create("general/graph", "zh")
   ka.max_workers = 5  # 默认：10
   ```

### 内存不足

**问题**：进程被终止或出现内存错误

**解决方案**：

1. **处理更小的分块**：
   ```python
   for chunk in split_document(text, chunk_size=1000):
       result.feed_text(chunk)
   ```

2. **保存中间结果**：
   ```python
   for i, doc in enumerate(documents):
       result.feed_text(doc)
       if i % 5 == 0:
           result.dump(f"./checkpoint_{i}/")
   ```

3. **中间步骤不构建索引**：
   ```python
   # 只在最后构建
   result.build_index()
   ```

---

## 数据问题

### 没有提取到实体

**问题**：结果为空

**解决方案**：

1. **检查输入文本**：
   ```bash
   wc -l document.md  # 检查是否为空
   ```

2. **尝试不同的模板**：
   ```bash
   hk parse doc.md -t general/model -l zh
   ```

3. **检查语言**：
   ```bash
   # 错误的语言
   hk parse chinese_doc.md -t general/graph -l en
   
   # 正确
   hk parse chinese_doc.md -t general/graph -l zh
   ```

### 知识库损坏

**问题**：无法加载或读取错误

**解决方案**：

1. **检查文件结构**：
   ```bash
   ls ./ka/
   # 应该有：data.json, metadata.json
   ```

2. **验证 JSON**：
   ```bash
   python -c "import json; json.load(open('./ka/data.json'))"
   ```

3. **重新提取**：
   ```bash
   rm -rf ./ka/
   hk parse doc.md -t general/graph -o ./ka/ -l zh
   ```

---

## 仍有问题？

1. **检查日志** — 查看详细的错误信息
2. **更新到最新版本** — `pip install --upgrade hyperknowledge`
3. **查看 GitHub Issues** — [github.com/hanxiangmin/Hyper-Knowledge/issues](https://github.com/hanxiangmin/Hyper-Knowledge/issues)
4. **创建新 issue** — 包含错误消息和复现步骤

---

## 调试模式

启用详细输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from hyperknowledge import Template
ka = Template.create("general/graph", "zh")
```

或在 CLI 配置中：
```toml
[defaults]
verbose = true
```