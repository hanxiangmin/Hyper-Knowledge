# Step 1: Setup

Project structure and template selection.

---

## Goal

Set up a robust project structure for maintaining a domain-specific knowledge abstract.

---

## Project Structure

Create the following directory structure:

```bash
mkdir -p my_ka/{documents,ka,backups,logs}
cd my_ka
```

Structure:
```
my_ka/
├── config.yaml         # Project configuration
├── documents/          # Source documents
│   ├── raw/           # Original files
│   └── processed/     # Processing log
├── ka/                # Knowledge base versions
│   └── current/       # Current version (symlink)
├── backups/           # Version backups
├── logs/              # Operation logs
└── kb_manager.py      # Management script
```

---

## Configuration

### config.yaml

```yaml
# Knowledge Abstract Configuration
name: "Company Knowledge Abstract"
domain: "legal"  # or finance, medical, etc.

# Template settings
template: "legal/contract_obligation"  # Choose based on domain
language: "en"

# Processing settings
chunk_size: 2048
max_workers: 10

# Versioning
version_format: "v{major}.{minor}"
auto_backup: true

# Paths
documents_dir: "./documents/raw"
ka_dir: "./ka"
backup_dir: "./backups"
```

### Template Selection Guide

| Domain | Recommended Template | Auto-Type |
|--------|---------------------|-----------|
| Legal | `legal/contract_obligation` | list |
| Finance | `finance/earnings_summary` | model |
| Medical | `medicine/anatomy_graph` | graph |
| General | `general/graph` | graph |
| Research | `general/concept_graph` | graph |

---

## Management Script

### Prerequisites

Install the required packages:

```bash
pip install pyyaml hyperknowledge python-dotenv
```

> **Note:** The management script uses `pyyaml` for config files and `python-dotenv` for loading API keys. These are not included in Hyper-Knowledge's default dependencies.

### kb_manager.py (Starter)

```python
"""Knowledge Abstract Manager."""

import yaml
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from hyperknowledge import Template

@dataclass
class KBConfig:
    name: str
    domain: str
    template: str
    language: str
    documents_dir: str
    ka_dir: str
    backup_dir: str

class KnowledgeBaseManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.ka = None
        self.current_kb = None
        
    def _load_config(self, path: str) -> KBConfig:
        """Load configuration from YAML."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return KBConfig(**data)
    
    def initialize(self):
        """Initialize knowledge abstract."""
        print(f"Initializing: {self.config.name}")
        
        # Create directories
        Path(self.config.documents_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.kb_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Create template
        self.ka = Template.create(
            self.config.template,
            language=self.config.language
        )
        
        print("✓ Initialization complete")
        
    def get_version_path(self, version: Optional[str] = None) -> Path:
        """Get path for a specific version."""
        if version is None:
            version = datetime.now().strftime("v%Y%m%d_%H%M%S")
        return Path(self.config.kb_dir) / version
    
    def save_version(self, kb_instance, version: Optional[str] = None):
        """Save knowledge abstract version."""
        path = self.get_version_path(version)
        kb_instance.dump(str(path))
        
        # Update current symlink
        current_link = Path(self.config.kb_dir) / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(path, target_is_directory=True)
        
        print(f"✓ Saved version: {path.name}")
        return path

# Usage
if __name__ == "__main__":
    manager = KnowledgeBaseManager()
    manager.initialize()
```

---

## Initialization

### 1. Create Config

```bash
cat > config.yaml << 'EOF'
name: "My Knowledge Abstract"
domain: "general"
template: "general/graph"
language: "en"
documents_dir: "./documents/raw"
ka_dir: "./ka"
backup_dir: "./backups"
EOF
```

### 2. Run Setup

Ensure `pyyaml` and `python-dotenv` are installed (see [Prerequisites](#prerequisites) above):

```bash
python kb_manager.py
```

Expected output:
```
Initializing: My Knowledge Abstract
✓ Initialization complete
```

### 3. Verify Structure

```bash
tree my_ka/
```

---

## Template Testing

Before ingesting documents, test your template:

```python
# test_template.py
from hyperknowledge import Template

# Load config
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Test template
ka = Template.create(config["template"], config["language"])

# Test with sample text
test_text = "This is a test document for template validation."
result = ka.parse(test_text)

print(f"Template: {config['template']}")
print(f"Nodes: {len(result.nodes)}")
print(f"Edges: {len(result.edges)}")
```

---

## Next Step

→ [Step 2: Ingest Documents](step2-ingest.md)
