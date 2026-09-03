# 贡献指南

如何为 Hyper-Knowledge 做出贡献。

---

## 贡献方式

- **报告 Bug** — 提交 GitHub Issue
- **请求新功能** — 建议新功能
- **改进文档** — 修复错别字，添加示例
- **添加模板** — 分享领域特定模板
- **提交代码** — 修复 Bug 或添加功能

---

## 快速开始

### 1. Fork 仓库

```bash
git clone https://github.com/your-username/hyper-knowledge.git
cd hyper-knowledge
```

### 2. 配置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 以可编辑模式安装
pip install -e ".[dev]"
```

### 3. 运行测试

```bash
pytest
```

---

## 开发规范

### 代码风格

- 遵循 PEP 8
- 使用类型提示
- 编写文档字符串（Google 风格）

### 示例

```python
def process_data(text: str, max_length: int = 1000) -> dict:
    """处理输入文本并返回结构化数据。
    
    Args:
        text: 要处理的输入文本
        max_length: 最大处理长度
        
    Returns:
        包含处理后数据的字典
        
    Raises:
        ValueError: 如果文本为空
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    # 处理逻辑
    return {"result": text[:max_length]}
```

### 测试

为新功能编写测试：

```python
def test_new_feature():
    result = new_feature("input")
    assert result["status"] == "success"
```

运行测试：
```bash
pytest tests/test_new_feature.py -v
```

---

## 添加模板

### 模板结构

在 `hyperknowledge/templates/presets/<domain>/` 目录下创建 YAML 文件：

```yaml
language: [zh, en]

name: my_template
type: graph
tags: [domain, category]

description:
  zh: "中文描述"
  en: "English description"

output:
  # 模式定义
  
guideline:
  # LLM 指令

identifiers:
  # ID 规则

display:
  # 可视化设置
```

### 测试模板

```python
from hyperknowledge import Template

# 测试你的模板
ka = Template.create("domain/my_template", "en")
result = ka.parse(test_text)

# 验证输出
assert len(result.nodes) > 0
```

### 提交模板

1. 添加模板 YAML 文件
2. 添加测试用例
3. 更新文档
4. 提交 PR 并附带描述

---

## 文档

### 构建文档

```bash
# 安装文档依赖
pip install mkdocs mkdocs-material mkdocstrings[python]

# 本地预览
mkdocs serve

# 构建
mkdocs build
```

### 文档规范

- 编写清晰、简洁的说明
- 包含代码示例
- 测试所有示例
- 使用 Markdown 格式

---

## Pull Request 流程

1. **创建分支**：
   ```bash
   git checkout -b feature/my-feature
   ```

2. **进行更改**，提交信息清晰

3. **添加测试**，覆盖新功能

4. **更新文档**，如有需要

5. **提交 PR**，包含：
   - 清晰的描述
   - 更改内容和原因
   - 执行的测试
   - 截图（如有 UI 更改）

---

## 代码审查

所有提交都需要审查。我们会检查：

- 代码质量和风格
- 测试覆盖率
- 文档
- 向后兼容性

---

## 有问题？

- 开启 [GitHub Discussion](https://github.com/hanxiangmin/Hyper-Knowledge/discussions)
- 在现有 Issue 中评论

---

## 许可证

通过贡献，您同意您的贡献将在 Apache-2.0 许可证下授权。
