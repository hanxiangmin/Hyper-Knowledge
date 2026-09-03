# 步骤 2：导入

向知识库添加文档。

---

## 目标

将文档导入知识库并进行适当的版本控制。

---

## 文档准备

### 支持的格式

- Markdown (.md)
- Text (.txt)
- 转换 PDF：`pdftotext document.pdf document.txt`

### 组织文档

```
documents/
├── raw/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── doc1.md
│   │   │   └── doc2.md
│   │   └── 02/
│   │       └── doc3.md
│   └── archive/
└── processed/  # 处理日志
```

---

## 导入方法

### 方法 1：初始导入

第一批文档：

```python
def initial_ingest(self, documents_dir: str):
    """文档初始导入。"""
    print("开始初始导入...")
    
    # 获取所有文档
    docs = list(Path(documents_dir).glob("**/*.md"))
    docs.extend(Path(documents_dir).glob("**/*.txt"))
    
    print(f"发现 {len(docs)} 个文档")
    
    # 解析第一个文档
    print(f"处理: {docs[0].name}")
    text = docs[0].read_text(encoding="utf-8")
    ka = self.ka.parse(text)
    
    # 添加剩余文档
    for doc in docs[1:]:
        print(f"添加: {doc.name}")
        text = doc.read_text(encoding="utf-8")
        ka.feed_text(text)
    
    # 构建索引
    print("构建搜索索引...")
    ka.build_index()
    
    # 保存版本
    version_path = self.save_version(ka, "v1.0")
    
    # 记录处理
    self._log_processing(docs, version_path)
    
    print(f"✓ 已导入 {len(docs)} 个文档")
    print(f"✓ 知识库: {version_path}")
    
    return ka
```

### 方法 2：增量更新

向现有知识库添加新文档：

```python
def add_documents(self, document_paths: list[str]):
    """向现有知识库添加新文档。"""
    print("加载当前知识库...")
    
    # 加载当前版本
    current_path = Path(self.config.kb_dir) / "current"
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    # 添加新文档
    for path in document_paths:
        doc_path = Path(path)
        print(f"添加: {doc_path.name}")
        
        text = doc_path.read_text(encoding="utf-8")
        ka.feed_text(text)
    
    # 重建索引
    print("重建搜索索引...")
    ka.build_index()
    
    # 保存新版本
    version = self._get_next_version()
    version_path = self.save_version(ka, version)
    
    print(f"✓ 已添加 {len(document_paths)} 个文档")
    print(f"✓ 新版本: {version}")
    
    return ka

def _get_next_version(self) -> str:
    """生成下一个版本号。"""
    current = Path(self.config.kb_dir) / "current"
    if not current.exists():
        return "v1.0"
    
    # 解析当前版本
    current_target = current.readlink().name
    if current_target.startswith("v"):
        try:
            parts = current_target[1:].split(".")
            major = int(parts[0])
            minor = int(parts[1])
            return f"v{major}.{minor + 1}"
        except:
            pass
    
    return datetime.now().strftime("v%Y%m%d_%H%M%S")
```

---

## 完整导入脚本

```python
"""步骤 2：文档导入。"""

import argparse
from pathlib import Path
from kb_manager import KnowledgeBaseManager

def main():
    parser = argparse.ArgumentParser(description="导入文档到知识库")
    parser.add_argument("--initial", action="store_true", help="初始导入")
    parser.add_argument("--add", nargs="+", help="添加特定文档")
    parser.add_argument("--dir", default="./documents/raw", help="文档目录")
    args = parser.parse_args()
    
    # 初始化管理器
    manager = KnowledgeBaseManager()
    manager.initialize()
    
    if args.initial:
        # 初始导入
        ka = manager.initial_ingest(args.dir)
        
        # 打印统计
        print("\n知识库统计:")
        print(f"  实体: {len(ka.data.entities)}")
        print(f"  关系: {len(ka.data.relations)}")
        
    elif args.add:
        # 添加特定文档
        ka = manager.add_documents(args.add)
        
        print("\n知识库统计:")
        print(f"  实体: {len(ka.data.entities)}")
        print(f"  关系: {len(ka.data.relations)}")

if __name__ == "__main__":
    main()
```

### 使用

```bash
# 初始导入
python step2_ingest.py --initial

# 添加特定文档
python step2_ingest.py --add documents/raw/2024/02/new_doc.md

# 添加多个文档
python step2_ingest.py --add doc1.md doc2.md doc3.md
```

---

## 处理日志

跟踪已导入的内容：

```python
def _log_processing(self, documents: list[Path], version_path: Path):
    """记录处理详情。"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "version": version_path.name,
        "documents": [str(d) for d in documents],
        "document_count": len(documents)
    }
    
    log_file = Path("logs") / "ingestions.jsonl"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## 最佳实践

### 1. 批次大小

分批处理文档：

```python
BATCH_SIZE = 10

for i in range(0, len(docs), BATCH_SIZE):
    batch = docs[i:i + BATCH_SIZE]
    for doc in batch:
        ka.feed_text(doc.read_text())
    
    # 保存检查点
    if i % (BATCH_SIZE * 5) == 0:
        ka.dump(f"./ka/checkpoint_{i}/")
```

### 2. 错误处理

```python
try:
    text = doc.read_text(encoding="utf-8")
    ka.feed_text(text)
except Exception as e:
    print(f"处理 {doc} 时出错: {e}")
    # 记录错误，继续下一个
    continue
```

### 3. 验证

```python
def validate_ingestion(self, ka):
    """导入后验证知识库。"""
    assert not ka.empty(), "知识库为空"
    assert len(ka.data.entities) > 0, "未提取到实体"
    
    # 尝试构建索引
    try:
        ka.build_index()
    except Exception as e:
        raise ValueError(f"构建索引失败: {e}")
```

---

## 下一步

→ [步骤 3：查询和维护](step3-query.md)
