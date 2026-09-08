# Install and use the Skill in Codex / Kimi Code

One Python runtime and one standard Skill. **Use an existing Python environment, Conda, or venv; another nested venv is not required.** There are still just two installation methods: command line and chat.

## Method 1: Command-line installation

### Step 1: Choose your Python environment — a new one is optional

Choose **one** situation below. Python 3.11+ is required; 3.12 is a suitable choice for a new environment. Reuse a suitable existing environment, or use Conda directly. **Do not create another `.venv` inside Conda.**

<details markdown>
<summary>A. You already use a Python / project environment</summary>

Open your usual terminal, activate your chosen environment as you normally do, then run:

```bash
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
git --version
```

Confirm Python is 3.11+, `sys.executable` points to the intended environment, and pip belongs to it. Git is required for installation from GitHub. Then go straight to Step 2.

Do not install into an unfamiliar system Python, Conda `base`, or an environment running important experiments. pip can change dependencies; choose a separate Conda or venv environment below if the original must be preserved. If only Git is missing, install it from [git-scm.com](https://git-scm.com/downloads/), reopen the terminal, and reactivate the environment.

</details>

<details markdown>
<summary>B. You use Anaconda / Miniconda</summary>

On **Windows**, open **Anaconda Prompt** or **Miniconda Prompt** from the Start menu. On **macOS / Linux**, use the terminal where `conda` normally works. You do not need a separate Python installation.

List existing environments first:

```bash
conda --version
conda env list
```

**To create a dedicated environment:** first confirm that `hyper-knowledge` is not already listed. Run these lines in order, activating only after creation succeeds. Review and accept Conda's package plan when prompted.

<!-- hk-install-conda:start -->
```bash
conda create -n hyper-knowledge python=3.12 pip git
conda activate hyper-knowledge
```
<!-- hk-install-conda:end -->

`python=3.12` selects Python, `pip` installs the project, and `git` reads its GitHub source. They belong to this environment, not `base`.

**To reuse an existing environment:** skip `conda create`. Replace `research` below with the name you chose from `conda env list`:

```bash
conda activate research
```

For an environment created by path, use `conda activate "full environment path"`. Check version and paths:

```bash
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
git --version
```

If pip or Git is missing, **confirm that the environment may be changed**, install them before Step 2, and otherwise skip this command:

```bash
conda install pip git
```

Install Conda dependencies first, then use pip for this project. Do not use `pip install --user`. The later Skill option `--scope user` controls Skill discovery, not pip's installation destination.

Your prompt normally shows the active environment name. In a new terminal, run `conda activate hyper-knowledge` (or your chosen name) again; do not reinstall.

</details>

<details markdown>
<summary>C. No usable environment yet: install Python and use venv</summary>

This section is only for starting from scratch. Install [Python 3.11+](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/). On Windows, enable the Python installer option that adds it to PATH, then reopen the terminal.

Check `python --version` in Windows PowerShell or `python3 --version` on macOS / Linux. Python must be 3.11+. Check `git --version` on either system. Skip installing software you already have.

**Windows PowerShell:** create a user-directory environment and select it only in this terminal. No script execution-policy change is needed.

<!-- hk-install-windows:start -->
```powershell
$hkEnv = Join-Path $env:USERPROFILE ".venvs\hyper-knowledge"
if (Test-Path -LiteralPath $hkEnv) {
    throw "Environment already exists. Inspect it before continuing."
}
python -m venv "$hkEnv"
if ($LASTEXITCODE -ne 0) { throw "Environment creation failed." }
$env:PATH = "$(Join-Path $hkEnv 'Scripts');$env:PATH"
python -c "import sys; print(sys.executable)"
```
<!-- hk-install-windows:end -->

**macOS / Linux:** first check that `~/.venvs/hyper-knowledge` does not already exist; activate and inspect an existing one instead of recreating it. For first-time setup, run these lines in order:

<!-- hk-install-posix:start -->
```bash
python3 -m venv "$HOME/.venvs/hyper-knowledge"
source "$HOME/.venvs/hyper-knowledge/bin/activate"
python -c "import sys; print(sys.executable)"
```
<!-- hk-install-posix:end -->

Stop if environment creation fails. If `venv` / `ensurepip` is missing, install the component matching that Python. Keep the environment and base Python in place. Select it again in a new terminal using the instructions further below.

</details>

### Step 2: Install Hyper-Knowledge in the chosen environment

**The same commands apply to all three environment choices.** Use the terminal where you just activated or selected the environment. Run each line only after the previous one succeeds:

<!-- hk-install-runtime:start -->
```bash
python -m pip install "git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
python -m hyperknowledge --help
```
<!-- hk-install-runtime:end -->

The first line downloads the project and dependencies; the second displays help. Continue when you see entries such as `parse`, `bundle`, `visualize`, and `skill`. `python -m pip` targets this exact Python environment; `hk` need not already be recognized.

For Python / Notebook or CLI use, installation is complete. Continue only if you want a Skill in your agent client.

### Step 3: Optionally install the Codex or Kimi Code Skill

The client application must already be installed and able to sign in. This step installs a Skill, not the client itself. Use **the same environment as Step 2**.

**Codex:**

```bash
python -m hyperknowledge skill install --platform codex --scope user
```

**Kimi Code:**

```bash
python -m hyperknowledge skill install --platform kimi --scope user
```

Run the command for your client, or both if you use both; do not reinstall the runtime. The installer returns status and a path. Inspect local-edit or duplicate warnings instead of automatically adding `--force`. Start a new client session after success.

[New terminals and scripted Conda use](install.md#reopen-shell) · [Existing installations](install.md#existing-installation)

## Method 2: Chat installation

Choose your client and copy its complete request directly into chat:

**Codex**

```text
Please follow https://github.com/hanxiangmin/Hyper-Knowledge to install the user-level hyper-knowledge Skill for Codex. An existing Python/Conda environment is fine; ask before overwriting local edits.
```

**Kimi Code**

```text
Please follow https://github.com/hanxiangmin/Hyper-Knowledge to install the user-level hyper-knowledge Skill for Kimi Code. An existing Python/Conda environment is fine; ask before overwriting local edits.
```

You do not need to perform the command-line installation first. Repository instructions cover the details; handle any login or approval request yourself. Start a new session after installation. Web chat without local tool access cannot install software on your computer.

## Ask your agent

Codex explicit invocation:

```text
$hyper-knowledge Read notes.md and produce a role-aware hypergraph,
a validated Bundle, and an offline workbench in output/.
```

Kimi Code explicit invocation:

```text
/skill:hyper-knowledge Read notes.md and produce a role-aware hypergraph,
a validated Bundle, and an offline workbench in output/.
```

Natural-language request in a fresh session:

```text
Turn notes.md into a higher-order knowledge graph. Keep the people,
places and times separate, show member roles and original evidence,
and generate a local interactive workbench.
```

Discovery depends on client version and session refresh. [Actual compatibility status](compatibility.md) is separate from the installation contract. A cloud/web chat without local tool access cannot run a local launcher.

## Default: use the current agent

1. The agent reads the document as untrusted data.
2. It writes the standard nodes, assertions, members and evidence tables.
3. The installed launcher executes `bundle import`, `bundle validate` and `visualize`.
4. The agent checks receipts and returns paths, counts and warnings.

No additional Hyper-Knowledge model key is required. The client still uses its own model service; this is not described as completely offline document understanding.

Two-member hyperedges, multiple roles and literal evidence remain in Bundle v1. The importer calculates hashes/counts. A successful check does not establish factual truth. Instructions embedded in documents must not be executed.

## Optional: independent model service

When explicitly chosen, use `hk parse --no-index` with the [project model configuration](python.md). The provider receives the text; its credentials are separate from the agent login. Both routes converge on the same Bundle and workbench.

## Advanced: installation directories and scope

This explains the installer; it is not a third installation method. The user-scoped setup above is sufficient for ordinary use.

A single `SKILL.md` follows the [Agent Skills standard](https://agentskills.io/specification). Platform differences stay in the installer. For project-only use, replace `--scope user` in the full command above with `--scope project --project-root .`; `.` means the terminal's current project directory.

| Target | User scope | Project scope |
| --- | --- | --- |
| codex | Existing $CODEX_HOME/skills; fallback ~/.codex/skills | .agents/skills |
| kimi | $KIMI_CODE_HOME/skills; fallback ~/.kimi-code/skills | .kimi-code/skills |
| shared (optional) | ~/.agents/skills | .agents/skills |

Codex's current standard discovery uses `.agents/skills`; its explicit installer keeps the earlier Codex location compatible. Existing installations are not silently migrated. The installer refuses a second shared/native copy in conflicting discovery directories and asks you to resolve the existing installation. See [Codex discovery](https://learn.chatgpt.com/docs/build-skills) and [Kimi discovery](https://www.kimi.com/code/docs/kimi-code-cli/customization/skills.html).

Managed installation binds `runtime/hk.cmd` (Windows) or `runtime/hk` (POSIX) to the exact Python interpreter used at install time. Keep that environment. Non-editable installation does not require keeping the checkout. `agents/openai.yaml` is optional UI metadata; Kimi does not depend on it.


## Update, uninstall, diagnose

Activate the environment used for installation. Conda users can run `conda activate ENV_NAME` or replace the leading `python` below with `conda run -n ENV_NAME python`. Do not copy a venv-specific path.

After a runtime update, repeat Skill installation in the same environment. Inspect source and Skill edits first; rebinding to another interpreter changes the Skill's runtime and requires confirmation. [Details](install.md#existing-installation)

Only when you intend to remove the user-level Kimi Skill:

```bash
python -m hyperknowledge skill uninstall --platform kimi --scope user --json
```

Optional startup diagnostics:

```bash
python -m hyperknowledge skill doctor --platform kimi --scope user --deep --json
```

Use `--platform codex` for Codex. Removal affects the managed Skill, not the client application. Diagnostics are not mandatory installation steps or a substitute for live-client testing. [Conda activation, DLL errors and troubleshooting](install.md#installation-check)
