# 步骤 1：提取知识

解析研究论文并提取结构化概念。

---

## 目标

将实体、关系和概念从研究论文提取到结构化知识图谱中。

---

## 准备

### 1. 获取研究论文

下载论文或使用您自己的。在本教程中，我们将使用一个样例：

```bash
# 下载样例论文（或使用您自己的）
curl -o paper.md https://arxiv.org/abs/1706.03762  # Attention Is All You Need
```

### 2. 转换为文本（如需要）

如果您有 PDF：

```bash
pdftotext paper.pdf paper.md
```

---

## 使用 CLI 提取

### 基本提取

```bash
hk parse paper.md -t general/concept_graph -o ./paper_kb/ -l zh
```

**功能说明：**
- 读取论文
- 提取概念及其关系
- 保存到 `./paper_kb/`

### 验证提取

```bash
hk info ./paper_kb/
```

预期输出：
```
知识摘要信息

路径          ./paper_kb/
模板          general/concept_graph
语言          en
节点          25
边            32
索引          已构建
```

### 可视化

```bash
hk show ./paper_kb/
```

---

## 使用 Python 提取

### 脚本

```python
"""步骤 1：从研究论文提取知识。"""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template
from pathlib import Path

# 配置
PAPER_FILE = "paper.md"
OUTPUT_DIR = "./paper_kb/"

def main():
    # 创建模板
    print("创建概念提取模板...")
    ka = Template.create("general/concept_graph", language="zh")
    
    # 读取论文
    print(f"读取: {PAPER_FILE}")
    text = Path(PAPER_FILE).read_text(encoding="utf-8")
    
    # 提取知识
    print("提取概念和关系...")
    result = ka.parse(text)
    
    # 显示结果
    print(f"\n提取完成:")
    print(f"  节点: {len(result.nodes)}")
    print(f"  边: {len(result.edges)}")
    
    # 显示样例节点
    print("\n样例概念:")
    for node in result.nodes[:5]:
        print(f"  - {node.name} ({node.type})")
    
    # 保存
    print(f"\n保存到: {OUTPUT_DIR}")
    result.dump(OUTPUT_DIR)
    
    # 为下一步构建索引
    print("构建搜索索引...")
    result.build_index()
    result.dump(OUTPUT_DIR)
    
    print("\n✓ 步骤 1 完成!")
    print(f"  知识库: {OUTPUT_DIR}")
    print(f"\n下一步: 运行 'python step2_search.py'")

if __name__ == "__main__":
    main()
```

### 运行

```bash
python step1_extract.py
```

---

## 理解输出

### 提取了什么？

概念图谱模板提取：

**实体：**
- 概念（模型、算法、技术）
- 作者
- 数据集
- 指标

**关系：**
- `uses` — 概念使用另一个
- `improves_upon` — 改进关系
- `evaluated_on` — 评估数据集
- `achieves` — 结果/指标

### 示例输出

```python
# 实体
[
    {"name": "Transformer", "type": "model"},
    {"name": "Attention Mechanism", "type": "concept"},
    {"name": "BLEU Score", "type": "metric"}
]

# 关系
[
    {"source": "Transformer", "target": "Attention Mechanism", "type": "uses"},
    {"source": "Transformer", "target": "BLEU Score", "type": "achieves"}
]
```

---

## 故障排除

### "未提取到实体"

- 检查论文不为空：`wc -l paper.md`
- 尝试不同模板：`general/graph`
- 检查语言设置与文档匹配

### "提取速度慢"

- 长论文会自动分块
- 每个分块都需要大语言模型调用
- 考虑使用 `--no-index` 稍后构建

---

## 下一步

→ [步骤 2：语义搜索](step2-search.md)
