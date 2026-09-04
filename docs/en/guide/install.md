# Install and verify

There are two parts to the installation: a Python environment runs `hk`, and the Skill tells an agent when and how to use it. Copying `SKILL.md` alone does not install the runtime.

## Install from Codex chat (recommended)

Paste this request directly into a local Codex chat. No terminal command or `codex` prefix is needed:

```text
Please install hyper-knowledge from https://github.com/hanxiangmin/Hyper-Knowledge.
Follow the repository's manual installation steps to install the project runtime
in a persistent Python environment and the user-level Codex Skill.
Verify with hk skill doctor --scope user --deep --json.
If an existing installation has local changes, ask before overwriting them.
```

Review and approve network and file-write requests when prompted. If the installed Skill does not appear, restart Codex. [Official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)

## From the terminal (optional) { #terminal }

With Codex CLI installed and signed in, run this from a directory where you want to keep the project (Bash / PowerShell):

```bash
codex 'Install the complete hyper-knowledge from https://github.com/hanxiangmin/Hyper-Knowledge. Follow its manual setup steps for the runtime in a persistent Python environment and user-level Codex Skill, then verify with hk skill doctor --scope user --deep --json. Ask before overwriting any existing local changes.'
```

This sends the same installation request from your terminal. Review and approve actions when prompted. [Official Codex CLI usage](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## Manual installation

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
