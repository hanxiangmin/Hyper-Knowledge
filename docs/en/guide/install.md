# Install and verify

There are two parts to the installation: a Python environment runs `hk`, and the Skill tells an agent when and how to use it. Copying `SKILL.md` alone does not install the runtime.

## Install in an environment you will keep

Use Python 3.11 or later:

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Then install the runtime and user-level Skill:

```bash
python -m pip install -e .
hk --version
hk skill install --scope user --json
hk skill doctor --scope user --deep --json
```

The managed installer creates a launcher bound to this Python environment. Keep the environment in place. If you replace or move it, reinstall the Skill and run doctor again.

## Limit installation to one project

Replace the final two commands above with:

```bash
hk skill install --scope project --project-root . --json
hk skill doctor --scope project --project-root . --deep --json
```

Project scope makes the selected runtime explicit for that project; user scope is convenient across personal projects. The managed integration currently targets Codex. Other Agent Skills clients need their own runtime-invocation check.

## Try a result before configuring a model

```bash
hk skill demo -o output/first-demo --json
```

Open the HTML path reported by the command. This demo uses programmatically constructed synthetic data and makes no model call. It checks installation and the graph workflow, not extraction accuracy on real documents.

If the runtime is already installed and you only need the instruction bundle:

```bash
npx skills add hanxiangmin/Hyper-Knowledge --skill hyper-knowledge -g
```

Next: [process your own document](document.md), or follow the [troubleshooting sequence](faq.md).
