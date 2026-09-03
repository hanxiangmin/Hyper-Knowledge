# Troubleshooting

Solutions to common issues.

---

## Installation Issues

### pip install fails

**Problem**: Installation fails with errors

**Solutions**:

1. Upgrade pip: `pip install --upgrade pip`
2. Use Python 3.11+: `python --version`
3. Install in virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install hyperknowledge
   ```

### ImportError: No module named 'hyperknowledge'

**Problem**: Can't import after installation

**Solutions**:

1. Check Python version: `python --version` (need 3.11+)
2. Verify installation: `pip list | grep hyper`
3. Check virtual environment is activated
4. Reinstall: `pip install --force-reinstall hyperknowledge`

---

## Configuration Issues

### API Key Not Found

**Error**: `No API key configured`

**Solutions**:

1. **CLI Configuration** (recommended):
   ```bash
   # OpenAI / Bailian (one-step)
   hk config init -p openai -k YOUR_API_KEY
   
   # Anthropic / DeepSeek (LLM + separate embedder)
   hk config llm -p deepseek -k YOUR_DEEPSEEK_API_KEY
   hk config embedder -p openai -k YOUR_OPENAI_API_KEY
   ```

2. **Environment Variable**:
   ```bash
   export OPENAI_API_KEY=your-api-key
   export ANTHROPIC_API_KEY=your-api-key    # for Anthropic
   export DEEPSEEK_API_KEY=your-api-key     # for DeepSeek
   ```

3. **Verify Configuration**:
   ```bash
   hk config show
   ```

### Invalid API Key

**Error**: `Authentication failed`

**Solutions**:

1. Verify key is correct
2. Check for extra spaces
3. For Anthropic: ensure `ANTHROPIC_API_KEY` (not `OPENAI_API_KEY`)
4. For DeepSeek: ensure `DEEPSEEK_API_KEY` (not `OPENAI_API_KEY`)
5. Check if key has available credits/quota

---

## Runtime Issues

### Template Not Found

**Error**: `Template 'xxx' not found`

**Solutions**:

1. **List available templates**:
   ```bash
   hk list template
   ```

2. **Check spelling**:
   ```bash
   # Correct
   hk parse doc.md -t general/biography_graph
   
   # Incorrect
   hk parse doc.md -t general/biography
   ```

3. **Use Python to search**:
   ```python
   from hyperknowledge import Template
   templates = Template.list(filter_by_query="bio")
   ```

### Language Required

**Error**: `--lang is required`

**Solution**:

```bash
# Add language flag
hk parse doc.md -t general/biography_graph -o ./out/ -l en
```

Note: Method templates don't require language.

### Output Directory Exists

**Error**: `Output directory already exists`

**Solutions**:

1. **Force overwrite**:
   ```bash
   hk parse doc.md -t general/graph -o ./out/ -l en -f
   ```

2. **Use different directory**:
   ```bash
   hk parse doc.md -t general/graph -o ./out2/ -l en
   ```

3. **Remove existing**:
   ```bash
   rm -rf ./out/
   hk parse doc.md -t general/graph -o ./out/ -l en
   ```

---

## Index and Search Issues

### Index Not Found

**Error**: `Search index not built`

**Solution**:

```bash
hk build-index ./output/
```

### Search Returns Empty

**Problem**: `hk search` finds no results

**Solutions**:

1. **Verify index exists**:
   ```bash
   hk info ./output/
   # Should show: Index: Built
   ```

2. **Try different query**:
   ```bash
   hk search ./output/ "different keywords"
   ```

3. **Increase top_k**:
   ```bash
   hk search ./output/ "query" -n 10
   ```

4. **Check data exists**:
   ```bash
   hk info ./output/
   # Should show Nodes > 0
   ```

### Chat Fails

**Error**: `Chat failed: index not found`

**Solution**:

```bash
hk build-index ./output/
hk talk ./output/ -q "your question"
```

---

## Performance Issues

### Extraction is Very Slow

**Problem**: Taking too long to process

**Solutions**:

1. **Skip index during batch**:
   ```bash
   hk parse doc.md -t general/graph -o ./out/ -l en --no-index
   ```

2. **Reduce chunk size** (Python):
   ```python
   ka = Template.create("general/graph", "en")
   ka.chunk_size = 1024  # Default: 2048
   ```

3. **Reduce workers** (if hitting rate limits):
   ```python
   ka = Template.create("general/graph", "en")
   ka.max_workers = 5  # Default: 10
   ```

### Out of Memory

**Problem**: Process killed or memory error

**Solutions**:

1. **Process smaller chunks**:
   ```python
   for chunk in split_document(text, chunk_size=1000):
       result.feed_text(chunk)
   ```

2. **Save intermediate results**:
   ```python
   for i, doc in enumerate(documents):
       result.feed_text(doc)
       if i % 5 == 0:
           result.dump(f"./checkpoint_{i}/")
   ```

3. **Don't build index for intermediate steps**:
   ```python
   # Build only at the end
   result.build_index()
   ```

---

## Data Issues

### No Entities Extracted

**Problem**: Empty result

**Solutions**:

1. **Check input text**:
   ```bash
   wc -l document.md  # Check not empty
   ```

2. **Try different template**:
   ```bash
   hk parse doc.md -t general/model -l en
   ```

3. **Check language**:
   ```bash
   # Wrong language
   hk parse chinese_doc.md -t general/graph -l en
   
   # Correct
   hk parse chinese_doc.md -t general/graph -l zh
   ```

### Corrupted Knowledge Abstract

**Problem**: Can't load or errors reading

**Solutions**:

1. **Check file structure**:
   ```bash
   ls ./ka/
   # Should have: data.json, metadata.json
   ```

2. **Validate JSON**:
   ```bash
   python -c "import json; json.load(open('./ka/data.json'))"
   ```

3. **Re-extract**:
   ```bash
   rm -rf ./ka/
   hk parse doc.md -t general/graph -o ./ka/ -l en
   ```

---

## Still Having Issues?

1. **Check logs** — Look for detailed error messages
2. **Update to latest** — `pip install --upgrade hyperknowledge`
3. **Check GitHub Issues** — [github.com/hanxiangmin/Hyper-Knowledge/issues](https://github.com/hanxiangmin/Hyper-Knowledge/issues)
4. **Create new issue** — Include error messages and reproduction steps

---

## Debug Mode

Enable verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from hyperknowledge import Template
ka = Template.create("general/graph", "en")
```

Or in CLI config:
```toml
[defaults]
verbose = true
```
