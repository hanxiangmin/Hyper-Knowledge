# Install the Skill

Hyper-Knowledge runs in a local Python environment. The steps below install its runtime and add the Skill to Codex.

## Install from Codex chat (recommended)

Paste this request directly into a local Codex chat. No terminal command or `codex` prefix is needed:

```text
Please install hyper-knowledge from https://github.com/hanxiangmin/Hyper-Knowledge.
Follow the repository instructions to install the runtime in a local Python
virtual environment and add the user-level Codex Skill.
If an existing installation has local changes, ask before overwriting them.
```

Review and approve network and file-write requests when prompted. If the installed Skill does not appear, restart Codex. [Official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)

## From the terminal (optional) { #terminal }

With Codex CLI installed and signed in, run this from a directory where you want to keep the project (Bash / PowerShell):

```bash
codex 'Please install hyper-knowledge from https://github.com/hanxiangmin/Hyper-Knowledge. Follow the repository instructions to install the runtime in a local Python virtual environment and add the user-level Codex Skill. If an existing installation has local changes, ask before overwriting them.'
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
hk skill install --scope user --json
```

You can use the Skill after installation. Its launcher uses this Python environment, so keep the source directory and `.venv` in place. Reinstall the Skill if you change environments.

## Limit installation to one project

Replace the final command above with:

```bash
hk skill install --scope project --project-root . --json
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

## Optional installation check { #installation-check }

If the Skill fails to start, this command helps locate the problem. It checks the Skill files, Python path, and launcher, then tries graph generation with a built-in example.

```bash
hk skill doctor --scope user --deep --json
```

`doctor` diagnoses the installation. `--deep` adds a trial run, and `--json` makes the result easy for Codex to read. This check is optional and runs locally, without uploading documents or calling a model. For a project installation, use `--scope project --project-root .` instead.
