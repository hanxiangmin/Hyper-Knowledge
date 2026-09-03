# 保存和加载

将知识库持久化到磁盘并在以后恢复。

---

## 概述

Hyper-Knowledge 提供序列化支持：
- **数据** — 提取的实体和关系
- **元数据** — 提取设置和时间戳
- **索引** — 向量搜索索引（可选）

---

## 保存知识库

### 基本保存

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "zh")
result = ka.parse(text)

# 保存到目录
result.dump("./my_ka/")
```

### 保存结构

```
./my_ka/
├── data.json          # 提取的知识
├── metadata.json      # 提取信息
└── index/             # 搜索索引（如已构建）
    ├── index.faiss
    └── docstore.json
```

### 保存前

```python
# 首先构建索引（如需要）
result.build_index()

# 然后保存
result.dump("./my_ka/")
```

---

## 加载知识库

### 基本加载

```python
from hyperknowledge import Template

# 创建模板（必须与原始匹配）
ka = Template.create("general/biography_graph", "zh")

# 加载保存的数据
ka.load("./my_ka/")

# 使用
print(f"加载了 {len(ka.nodes)} 个节点")
```

### 验证加载的数据

```python
ka.load("./my_ka/")

# 检查是否为空
if ka.empty():
    print("警告：未加载数据")
else:
    print(f"节点: {len(ka.nodes)}")
    print(f"边: {len(ka.edges)}")
```

---

## 用例

### 长期存储

```python
# 提取并保存
ka = Template.create("general/concept_graph", "zh")
result = ka.parse(research_paper)
result.build_index()
result.dump("./research_paper_kb/")

# 数周后使用
ka2 = Template.create("general/concept_graph", "zh")
ka2.load("./research_paper_kb/")
response = ka2.chat("主要发现是什么？")
```

### 共享知识库

```python
# 保存到共享位置
result.dump("/shared/ka/project_x/")

# 其他人可以加载
ka.load("/shared/ka/project_x/")
```

### 备份和版本控制

```python
from datetime import datetime

# 带时间戳保存
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result.dump(f"./backups/kb_{timestamp}/")

# 或版本化
result.dump("./kb_v1/")
# ... 稍后更新 ...
result.dump("./kb_v2/")
```

---

## 使用文件系统

### 检查现有 KA

```python
from pathlib import Path

ka_path = Path("./my_ka/")

if ka_path.exists() and (ka_path / "data.json").exists():
    print("知识库存在，正在加载...")
    ka.load(ka_path)
else:
    print("创建新知识库...")
    result = ka.parse(text)
    result.dump(ka_path)
```

### 列出保存的 KA

```python
import os

kb_dirs = [d for d in os.listdir("./") if os.path.isdir(d) and "_kb" in d]
print("可用知识库:", kb_dirs)
```

### 移动/复制

```python
import shutil

# 复制知识库
shutil.copytree("./kb_v1/", "./kb_backup/")

# 移动知识库
shutil.move("./old_location/", "./new_location/")
```

---

## 元数据

### 访问元数据

```python
result.dump("./my_ka/")

# 元数据自动保存
# 内容：
# - template: 使用的模板
# - lang: 语言
# - created_at: 创建时间戳
# - updated_at: 最后更新时间戳
```

### 自定义元数据

```python
# 添加自定义元数据
result.metadata["project"] = "研究项目 X"
result.metadata["version"] = "1.0"

result.dump("./my_ka/")
```

---

## 完整示例

```python
"""使用保存/加载管理知识库。"""

from hyperknowledge import Template
from pathlib import Path
import json

class KnowledgeBaseManager:
    def __init__(self, storage_dir="./knowledge_bases/"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save(self, ka, name):
        """保存知识库。"""
        ka_path = self.storage_dir / name
        ka.dump(ka_path)
        print(f"保存到 {ka_path}")
        return ka_path
    
    def load(self, name, template="general/biography_graph", lang="zh"):
        """加载知识库。"""
        ka_path = self.storage_dir / name
        
        if not ka_path.exists():
            raise FileNotFoundError(f"未找到知识库: {name}")
        
        ka = Template.create(template, lang)
        ka.load(ka_path)
        return ka
    
    def list(self):
        """列出可用的知识库。"""
        return [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
    
    def info(self, name):
        """获取知识库信息。"""
        ka_path = self.storage_dir / name
        meta_path = ka_path / "metadata.json"
        
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return None

# 用法
manager = KnowledgeBaseManager()

# 保存
ka = Template.create("general/biography_graph", "zh")
result = ka.parse(text)
manager.save(result, "苏轼传记")

# 列出
print(manager.list())  # ['苏轼传记']

# 加载
ka = manager.load("苏轼传记")
print(ka.chat("苏轼创作了哪些代表作？"))
```

---

## 最佳实践

### 1. 加载时匹配模板

```python
# 使用模板 X 保存
ka = Template.create("general/biography_graph", "zh")

# 使用相同模板加载
ka2 = Template.create("general/biography_graph", "zh")
ka2.load("./ka/")
```

### 2. 加载后构建索引

```python
ka.load("./ka/")

# 索引可能需要重建
index_path = Path("./ka/") / "index"
if not index_path.exists():
    ka.build_index()
```

### 3. 使用前验证

```python
try:
    ka.load("./ka/")
    if ka.empty():
        print("警告：空知识库")
except FileNotFoundError:
    print("未找到知识库")
```

### 4. 使用描述性名称

```python
# 好
result.dump("./ka/sushi_2024_01_15/")

# 避免
result.dump("./ka/temp/")
```

---

## 故障排除

### "文件未找到"

```python
from pathlib import Path

ka_path = Path("./my_ka/")
if not ka_path.exists():
    print(f"未找到目录: {ka_path}")
    print(f"可用: {list(Path('.').glob('*/'))}")
```

### "数据损坏"

```python
# 检查数据文件
import json
data = json.load(open("./my_ka/data.json"))
print(f"Keys: {data.keys()}")
```

### "索引未加载"

```python
ka.load("./ka/")

# 检查索引是否存在
if (Path("./ka/") / "index").exists():
    print("索引目录存在")
else:
    print("无索引，正在构建...")
    ka.build_index()
```

---

## 另请参见

**相关工作流：**
- [增量更新](incremental-updates.md) — 添加更多内容
- [搜索和聊天](search-and-chat.md) — 使用加载的知识

**基础知识：**
- [使用模板](using-templates.md) — Level 1 基础
- [CLI `hk parse` 命令](../../cli/commands/parse.md) — 命令行提取
