# Step 3: Query

Search, update, and maintain your knowledge abstract.

---

## Goal

Query the knowledge abstract and implement maintenance workflows.

---

## Query Interface

### Search Functionality

```python
def search(self, query: str, top_k: int = 5):
    """Search the knowledge abstract."""
    current_path = Path(self.config.kb_dir) / "current"
    
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    results = ka.search(query, top_k=top_k)
    return results
```

### Q&A Functionality

```python
def ask(self, question: str, top_k: int = 5):
    """Ask a question about the knowledge abstract."""
    current_path = Path(self.config.kb_dir) / "current"
    
    ka = Template.create(self.config.template, self.config.language)
    ka.load(current_path)
    
    response = ka.chat(question, top_k=top_k)
    return response.content
```

---

## Interactive Query Shell

```python
"""Step 3: Interactive Query Interface."""

import cmd
from kb_manager import KnowledgeBaseManager

class KBQueryShell(cmd.Cmd):
    intro = """
Knowledge Abstract Query Shell
==========================
Type 'help' for commands, 'quit' to exit

Commands:
  search <query>     - Semantic search
  ask <question>     - Ask a question
  stats              - Show KA statistics
  versions           - List versions
  backup             - Create backup
"""
    prompt = "ka> "
    
    def __init__(self):
        super().__init__()
        self.manager = KnowledgeBaseManager()
        self.ka = None
        self._load_kb()
    
    def _load_kb(self):
        """Load current knowledge abstract."""
        current_path = Path(self.manager.config.kb_dir) / "current"
        if current_path.exists():
            self.ka = Template.create(
                self.manager.config.template,
                self.manager.config.language
            )
            self.ka.load(current_path)
            print(f"Loaded: {self.manager.config.name}")
        else:
            print("Warning: No knowledge abstract found")
    
    def do_search(self, arg):
        """Search the knowledge abstract: search <query>"""
        if not arg:
            print("Usage: search <query>")
            return
        
        if not self.ka:
            print("No knowledge abstract loaded")
            return
        
        nodes, edges = self.ka.search(arg, top_k=5)

        print(f"\nFound {len(nodes)} nodes and {len(edges)} edges:\n")
        for i, node in enumerate(nodes, 1):
            print(f"{i}. [Node] {node.name} ({node.type})")
        for i, edge in enumerate(edges, len(nodes) + 1):
            print(f"{i}. [Edge] {edge.source} -> {edge.target}")
        print()
    
    def do_ask(self, arg):
        """Ask a question: ask <question>"""
        if not arg:
            print("Usage: ask <question>")
            return
        
        if not self.ka:
            print("No knowledge abstract loaded")
            return
        
        print("\nThinking...")
        answer = self.ka.chat(arg).content
        print(f"\n{answer}\n")
    
    def do_stats(self, arg):
        """Show knowledge abstract statistics."""
        if not self.ka:
            print("No knowledge abstract loaded")
            return
        
        print("\nKnowledge Abstract Statistics:")
        print(f"  Nodes: {len(self.ka.nodes)}")
        print(f"  Edges: {len(self.ka.edges)}")
        print(f"  Template: {self.manager.config.template}")

        # Node types
        from collections import Counter
        types = Counter(n.type for n in self.ka.nodes)
        print("\nNode Types:")
        for t, count in types.most_common():
            print(f"  {t}: {count}")
        print()
    
    def do_versions(self, arg):
        """List all versions."""
        kb_dir = Path(self.manager.config.kb_dir)
        versions = [d.name for d in kb_dir.iterdir() if d.is_dir()]
        
        print("\nVersions:")
        for v in sorted(versions):
            marker = " (current)" if v == "current" else ""
            print(f"  {v}{marker}")
        print()
    
    def do_backup(self, arg):
        """Create backup of current version."""
        import shutil
        
        current = Path(self.manager.config.kb_dir) / "current"
        if not current.exists():
            print("No current version to backup")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(self.manager.config.backup_dir) / f"backup_{timestamp}"
        
        shutil.copytree(current, backup_path)
        print(f"✓ Backup created: {backup_path}\n")
    
    def do_quit(self, arg):
        """Exit the shell."""
        print("Goodbye!")
        return True
    
    do_exit = do_quit

if __name__ == "__main__":
    KBQueryShell().cmdloop()
```

---

## Maintenance Operations

### Backup Strategy

```python
def create_backup(self, name: Optional[str] = None):
    """Create a backup of current knowledge abstract."""
    import shutil
    
    current = Path(self.config.kb_dir) / "current"
    if not current.exists():
        raise ValueError("No current version to backup")
    
    if name is None:
        name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    
    backup_path = Path(self.config.backup_dir) / name
    shutil.copytree(current, backup_path)
    
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def restore_backup(self, backup_name: str):
    """Restore from backup."""
    import shutil
    
    backup_path = Path(self.config.backup_dir) / backup_name
    if not backup_path.exists():
        raise ValueError(f"Backup not found: {backup_name}")
    
    # Save current as version first
    current = Path(self.config.kb_dir) / "current"
    if current.exists():
        self._save_current_as_version("pre-restore")
    
    # Restore backup
    if current.exists():
        shutil.rmtree(current)
    shutil.copytree(backup_path, current)
    
    print(f"✓ Restored from: {backup_path}")
```

### Version Management

```python
def list_versions(self):
    """List all versions."""
    kb_dir = Path(self.config.kb_dir)
    versions = []
    
    for item in kb_dir.iterdir():
        if item.is_dir() and item.name != "current":
            # Get version info
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
    """Rollback to a specific version."""
    version_path = Path(self.config.kb_dir) / version
    if not version_path.exists():
        raise ValueError(f"Version not found: {version}")
    
    # Update current symlink
    current_link = Path(self.config.kb_dir) / "current"
    if current_link.exists():
        current_link.unlink()
    current_link.symlink_to(version_path, target_is_directory=True)
    
    print(f"✓ Rolled back to: {version}")
```

### Cleanup

```python
def cleanup_old_versions(self, keep: int = 10):
    """Remove old versions, keeping only the most recent."""
    versions = self.list_versions()
    
    if len(versions) <= keep:
        print(f"No cleanup needed ({len(versions)} versions)")
        return
    
    to_remove = versions[:-keep]
    for v in to_remove:
        version_path = Path(self.config.kb_dir) / v["name"]
        shutil.rmtree(version_path)
        print(f"Removed: {v['name']}")
    
    print(f"✓ Cleaned up {len(to_remove)} old versions")
```

---

## Export and Reporting

### Export to JSON

```python
def export_to_json(self, output_file: str = "kb_export.json"):
    """Export knowledge abstract to JSON."""
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
    
    print(f"✓ Exported to: {output_file}")
```

### Generate Report

```python
def generate_report(self):
    """Generate knowledge abstract report."""
    from collections import Counter
    
    report = []
    report.append("# Knowledge Abstract Report")
    report.append(f"\nName: {self.config.name}")
    report.append(f"Template: {self.config.template}")
    report.append(f"\nStatistics:")
    report.append(f"- Entities: {len(self.ka.data.entities)}")
    report.append(f"- Relations: {len(self.ka.data.relations)}")
    
    # Entity types
    types = Counter(e.type for e in self.ka.data.entities)
    report.append("\n## Entity Types")
    for t, count in types.most_common():
        report.append(f"- {t}: {count}")
    
    return "\n".join(report)
```

---

## Summary

You now have a complete knowledge abstract system with:

✓ Document ingestion with versioning  
✓ Search and Q&A capabilities  
✓ Backup and restore functionality  
✓ Maintenance operations  
✓ Export and reporting  

### Next Steps

- Schedule regular backups
- Monitor knowledge abstract growth
- Set up automated ingestion pipelines
- Integrate with your applications

---

## See Also

- [Research Assistant Tutorial](../research-assistant/index.md)
- [Document Analysis Tutorial](../document-analysis/index.md)
