# 步骤 3：查询

搜索、更新和维护您的知识库。

---

## 目标

查询知识库并实现维护工作流。

---

## 查询接口

### 搜索功能

```python
def search(self, query: str, top_k: int = 5):
    """搜索知识库。"""
    current_path = Path(self.config.kb_dir) / "current"
    
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    results = ka.search(query, top_k=top_k)
    return results
```

### 问答功能

```python
def ask(self, question: str, top_k: int = 5):
    """向知识库提问。"""
    current_path = Path(self.config.kb_dir) / "current"
    
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    response = ka.chat(question, top_k=top_k)
    return response.content
```

---

## 交互式查询 Shell

```python
"""步骤 3：交互式查询界面。"""

import cmd
from kb_manager import KnowledgeBaseManager

class KBQueryShell(cmd.Cmd):
    intro = """
知识库查询 Shell
==========================
输入 'help' 查看命令，'quit' 退出

命令:
  search <query>     - 语义搜索
  ask <question>     - 提问
  stats              - 显示知识库统计
  versions           - 列出版本
  backup             - 创建备份
"""
    prompt = "ka> "
    
    def __init__(self):
        super().__init__()
        self.manager = KnowledgeBaseManager()
        self.ka = None
        self._load_kb()
    
    def _load_kb(self):
        """加载当前知识库。"""
        current_path = Path(self.manager.config.kb_dir) / "current"
        if current_path.exists():
            self.ka = Template.create(
                self.manager.config.template,
                self.manager.config.language
            )
            self.ka.load(current_path)
            print(f"已加载: {self.manager.config.name}")
        else:
            print("警告: 未找到知识库")
    
    def do_search(self, arg):
        """搜索知识库: search <query>"""
        if not arg:
            print("用法: search <query>")
            return
        
        if not self.ka:
            print("未加载知识库")
            return
        
        results = self.ka.search(arg, top_k=5)
        
        print(f"\n找到 {len(results)} 个结果:\n")
        for i, item in enumerate(results, 1):
            if hasattr(item, 'name'):
                print(f"{i}. [{item.type}] {item.name}")
            elif hasattr(item, 'source'):
                print(f"{i}. {item.source} -> {item.target}")
        print()
    
    def do_ask(self, arg):
        """提问: ask <question>"""
        if not arg:
            print("用法: ask <question>")
            return
        
        if not self.ka:
            print("未加载知识库")
            return
        
        print("\n思考中...")
        answer = self.ka.chat(arg).content
        print(f"\n{answer}\n")
    
    def do_stats(self, arg):
        """显示知识库统计。"""
        if not self.ka:
            print("未加载知识库")
            return
        
        print("\n知识库统计:")
        print(f"  实体: {len(self.ka.data.entities)}")
        print(f"  关系: {len(self.ka.data.relations)}")
        print(f"  模板: {self.manager.config.template}")
        
        # 实体类型
        from collections import Counter
        types = Counter(e.type for e in self.ka.data.entities)
        print("\n实体类型:")
        for t, count in types.most_common():
            print(f"  {t}: {count}")
        print()
    
    def do_versions(self, arg):
        """列出所有版本。"""
        kb_dir = Path(self.manager.config.kb_dir)
        versions = [d.name for d in kb_dir.iterdir() if d.is_dir()]
        
        print("\n版本:")
        for v in sorted(versions):
            marker = " (current)" if v == "current" else ""
            print(f"  {v}{marker}")
        print()
    
    def do_backup(self, arg):
        """创建当前版本备份。"""
        import shutil
        
        current = Path(self.manager.config.kb_dir) / "current"
        if not current.exists():
            print("没有当前版本可备份")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(self.manager.config.backup_dir) / f"backup_{timestamp}"
        
        shutil.copytree(current, backup_path)
        print(f"✓ 备份已创建: {backup_path}\n")
    
    def do_quit(self, arg):
        """退出 shell。"""
        print("再见!")
        return True
    
    do_exit = do_quit

if __name__ == "__main__":
    KBQueryShell().cmdloop()
```

---

## 维护操作

### 备份策略

```python
def create_backup(self, name: Optional[str] = None):
    """创建当前知识库备份。"""
    import shutil
    
    current = Path(self.config.kb_dir) / "current"
    if not current.exists():
        raise ValueError("没有当前版本可备份")
    
    if name is None:
        name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    
    backup_path = Path(self.config.backup_dir) / name
    shutil.copytree(current, backup_path)
    
    print(f"✓ 备份已创建: {backup_path}")
    return backup_path

def restore_backup(self, backup_name: str):
    """从备份恢复。"""
    import shutil
    
    backup_path = Path(self.config.backup_dir) / backup_name
    if not backup_path.exists():
        raise ValueError(f"备份未找到: {backup_name}")
    
    # 先保存当前为版本
    current = Path(self.config.kb_dir) / "current"
    if current.exists():
        self._save_current_as_version("pre-restore")
    
    # 恢复备份
    if current.exists():
        shutil.rmtree(current)
    shutil.copytree(backup_path, current)
    
    print(f"✓ 已从备份恢复: {backup_path}")
```

### 版本管理

```python
def list_versions(self):
    """列出所有版本。"""
    kb_dir = Path(self.config.kb_dir)
    versions = []
    
    for item in kb_dir.iterdir():
        if item.is_dir() and item.name != "current":
            # 获取版本信息
            metadata_file = item / "metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                versions.append({
                    "name": item.name,
                    "created": metadata.get("created_at", "unknown"),
                    "updated": metadata.get("updated_at", "unknown")
                })
    
    return sorted(versions, key=lambda x: x["name"])

def rollback(self, version: str):
    """回滚到特定版本。"""
    version_path = Path(self.config.kb_dir) / version
    if not version_path.exists():
        raise ValueError(f"版本未找到: {version}")
    
    # 更新当前符号链接
    current_link = Path(self.config.kb_dir) / "current"
    if current_link.exists():
        current_link.unlink()
    current_link.symlink_to(version_path, target_is_directory=True)
    
    print(f"✓ 已回滚到: {version}")
```

### 清理

```python
def cleanup_old_versions(self, keep: int = 10):
    """删除旧版本，仅保留最近的。"""
    versions = self.list_versions()
    
    if len(versions) <= keep:
        print(f"无需清理 ({len(versions)} 个版本)")
        return
    
    to_remove = versions[:-keep]
    for v in to_remove:
        version_path = Path(self.config.kb_dir) / v["name"]
        shutil.rmtree(version_path)
        print(f"已删除: {v['name']}")
    
    print(f"✓ 已清理 {len(to_remove)} 个旧版本")
```

---

## 导出和报告

### 导出为 JSON

```python
def export_to_json(self, output_file: str = "kb_export.json"):
    """导出知识库为 JSON。"""
    data = {
        "config": {
            "name": self.config.name,
            "template": self.config.template,
            "language": self.config.language
        },
        "data": self.ka.data.model_dump(),
        "metadata": self.ka.metadata
    }
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✓ 已导出到: {output_file}")
```

### 生成报告

```python
def generate_report(self):
    """生成知识库报告。"""
    from collections import Counter
    
    report = []
    report.append("# 知识库报告")
    report.append(f"\n名称: {self.config.name}")
    report.append(f"模板: {self.config.template}")
    report.append(f"\n统计:")
    report.append(f"- 实体: {len(self.ka.data.entities)}")
    report.append(f"- 关系: {len(self.ka.data.relations)}")
    
    # 实体类型
    types = Counter(e.type for e in self.ka.data.entities)
    report.append("\n## 实体类型")
    for t, count in types.most_common():
        report.append(f"- {t}: {count}")
    
    return "\n".join(report)
```

---

## 总结

您现在拥有一个完整的知识库系统，具备：

✓ 带版本控制的文档导入  
✓ 搜索和问答功能  
✓ 备份和恢复功能  
✓ 维护操作  
✓ 导出和报告  

### 下一步

- 安排定期备份
- 监控知识库增长
- 设置自动导入管道
- 集成到您的应用程序中

---

## 参见

- [研究助手教程](../research-assistant/index.md)
- [文档分析教程](../document-analysis/index.md)
