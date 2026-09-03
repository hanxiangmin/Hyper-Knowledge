# Contributing

How to contribute to Hyper-Knowledge.

---

## Ways to Contribute

- **Report bugs** — Open GitHub issues
- **Request features** — Suggest new functionality
- **Improve documentation** — Fix typos, add examples
- **Add templates** — Share domain-specific templates
- **Submit code** — Fix bugs or add features

---

## Getting Started

### 1. Fork the Repository

```bash
git clone https://github.com/your-username/hyper-knowledge.git
cd hyper-knowledge
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest
```

---

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)

### Example

```python
def process_data(text: str, max_length: int = 1000) -> dict:
    """Process input text and return structured data.
    
    Args:
        text: Input text to process
        max_length: Maximum length to process
        
    Returns:
        Dictionary containing processed data
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    # Processing logic
    return {"result": text[:max_length]}
```

### Testing

Write tests for new features:

```python
def test_new_feature():
    result = new_feature("input")
    assert result["status"] == "success"
```

Run tests:
```bash
pytest tests/test_new_feature.py -v
```

---

## Adding Templates

### Template Structure

Create a YAML file in `hyperknowledge/templates/presets/<domain>/`:

```yaml
language: [zh, en]

name: my_template
type: graph
tags: [domain, category]

description:
  zh: "中文描述"
  en: "English description"

output:
  # Schema definition
  
guideline:
  # LLM instructions

identifiers:
  # ID rules

display:
  # Visualization settings
```

### Testing Templates

```python
from hyperknowledge import Template

# Test your template
ka = Template.create("domain/my_template", "en")
result = ka.parse(test_text)

# Verify output
assert len(result.nodes) > 0
```

### Submitting Templates

1. Add template YAML file
2. Add test case
3. Update documentation
4. Submit PR with description

---

## Documentation

### Building Docs

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve locally
mkdocs serve

# Build
mkdocs build
```

### Documentation Guidelines

- Write clear, concise instructions
- Include code examples
- Test all examples
- Use markdown formatting

---

## Pull Request Process

1. **Create a branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes** with clear commit messages

3. **Add tests** for new functionality

4. **Update documentation** as needed

5. **Submit PR** with:
   - Clear description
   - What changed and why
   - Testing performed
   - Screenshots (if UI changes)

---

## Code Review

All submissions require review. We'll check:

- Code quality and style
- Test coverage
- Documentation
- Backward compatibility

---

## Questions?

- Open a [GitHub Discussion](https://github.com/hanxiangmin/Hyper-Knowledge/discussions)
- Comment on existing issues

---

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
