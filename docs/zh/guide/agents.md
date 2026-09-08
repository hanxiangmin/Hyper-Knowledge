# 在 Codex / Kimi Code 中安装和使用

一套 Python 运行程序和一份标准 Skill。**Python / Conda / venv 都可作为环境选择，不要求另建一层 venv。** 安装方式仍然只有命令行和聊天两种。

## 方式一：命令行安装

### 第 1 步：选好 Python 环境，不必人人新建

选择下面**一种**情况即可。要求 Python 3.11+；新建时可选 3.12。已有合适环境就复用，使用 Conda 就直接用 Conda，**不用再在 Conda 里面创建 `.venv`**。

<details markdown>
<summary>A. 已经有日常使用的 Python / 项目环境</summary>

打开你平时使用的终端，先按自己的方式激活目标环境，再运行：

```bash
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
git --version
```

确认 Python 为 3.11+，`sys.executable` 指向你希望使用的环境，pip 也属于同一环境。Git 用于从 GitHub 安装。然后直接进入第 2 步。

不要在不清楚用途的系统 Python、Conda `base` 或正在运行重要实验的环境中直接安装。pip 可能调整依赖；需要保留原环境时，选择下面的独立 Conda 或 venv 环境。仅缺 Git 时可从 [Git 官网](https://git-scm.com/downloads/) 安装，重新打开终端后再激活原环境。

</details>

<details markdown>
<summary>B. 使用 Anaconda / Miniconda 管理环境</summary>

**Windows** 打开开始菜单中的 **Anaconda Prompt** 或 **Miniconda Prompt**；**macOS / Linux** 打开平时能运行 `conda` 的终端。不需要另装一套 Python。

先查看已有环境：

```bash
conda --version
conda env list
```

**想单独建一个环境：** 确认列表里没有名为 `hyper-knowledge` 的环境，再逐行执行；创建成功后再激活。Conda 提示确认软件包方案时，阅读后确认。

<!-- hk-install-conda:start -->
```bash
conda create -n hyper-knowledge python=3.12 pip git
conda activate hyper-knowledge
```
<!-- hk-install-conda:end -->

这里 `python=3.12` 是 Python 版本，`pip` 用于安装项目，`git` 用于读取 GitHub 源码。它们属于新环境，不是安装到 `base`。

**想复用已有环境：** 不执行 `conda create`，而是运行下方命令；将 `research` 换成 `conda env list` 中你选好的环境名。

```bash
conda activate research
```

如果你用完整路径创建了环境，也可以 `conda activate "环境的完整路径"`。确认版本和路径：

```bash
python --version
python -c "import sys; print(sys.executable)"
python -m pip --version
git --version
```

已有环境缺少 pip 或 Git 时，在**确认可以修改该环境后**先安装它们，再进行第 2 步；两者都有就跳过：

```bash
conda install pip git
```

先完成 Conda 依赖，再用 pip 安装本项目；不要使用 `pip install --user`。后面 Skill 命令里的 `--scope user` 只指定 Skill 的发现范围，与 pip 的 `--user` 不是一回事。

终端前缀通常会显示环境名；每次重新打开终端，先 `conda activate hyper-knowledge`（或你自己的名字），不需要重新安装。

</details>

<details markdown>
<summary>C. 还没有可用环境：安装 Python，然后使用 venv</summary>

这一节只给需要从头准备环境的人。安装 [Python 3.11+](https://www.python.org/downloads/) 和 [Git](https://git-scm.com/downloads/)，Windows 安装 Python 时启用加入 PATH 的选项，然后重新打开终端。

Windows PowerShell 运行 `python --version`；macOS / Linux 运行 `python3 --version`，确认版本至少 3.11。两边都用 `git --version` 确认 Git 可用。已有安装不必重复装。

**Windows PowerShell：** 在用户目录下创建环境，并只让当前终端优先使用它。无需修改脚本执行策略。

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

**macOS / Linux：** 先确认 `~/.venvs/hyper-knowledge` 不存在；若已存在，直接激活并检查，不重建。首次创建时逐行执行：

<!-- hk-install-posix:start -->
```bash
python3 -m venv "$HOME/.venvs/hyper-knowledge"
source "$HOME/.venvs/hyper-knowledge/bin/activate"
python -c "import sys; print(sys.executable)"
```
<!-- hk-install-posix:end -->

环境创建失败时先处理错误，不能继续安装。缺少 `venv` / `ensurepip` 时，安装该 Python 版本对应的 venv 组件。保留环境和基础 Python；重新打开终端后需重新选择它，后文提供命令。

</details>

### 第 2 步：在选好的环境中安装 Hyper-Knowledge

下面三种环境用**同一组命令**。在刚才已激活或选好环境的终端里，逐行运行；前一步成功后再执行下一步：

<!-- hk-install-runtime:start -->
```bash
python -m pip install "git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
python -m hyperknowledge --help
```
<!-- hk-install-runtime:end -->

第一条下载项目并安装依赖，第二条显示帮助。看到 `parse`、`bundle`、`visualize`、`skill` 等条目，即可继续。`python -m pip` 保证把包安装到这条 `python` 对应的环境，不要求终端已经认识 `hk`。

只使用 Python / Notebook 或命令行，到这里就装好了。要在聊天中使用，再做下一步。

### 第 3 步：按需安装 Codex 或 Kimi Code Skill

客户端应用需要提前安装并能登录。这一步安装的是 Skill，不是客户端本身；仍在**第 2 步的同一个环境**执行。

**Codex：**

```bash
python -m hyperknowledge skill install --platform codex --scope user
```

**Kimi Code：**

```bash
python -m hyperknowledge skill install --platform kimi --scope user
```

用哪个客户端就执行哪条，两者都用可以分别执行，不必重复安装运行程序。安装器返回状态和路径；提示本地修改或冲突时先查看，不自动加 `--force`。成功后在客户端新建会话。

[重新打开终端与 Conda 脚本调用](install.md#reopen-shell) · [已有安装的处理](install.md#existing-installation)

## 方式二：聊天中安装

选择你正在使用的客户端，直接复制对应的完整文案到聊天框：

**Codex**

```text
请按 https://github.com/hanxiangmin/Hyper-Knowledge 的安装说明，为 Codex 安装用户级 hyper-knowledge Skill。可使用已有 Python/Conda 环境，覆盖本地修改前先询问。
```

**Kimi Code**

```text
请按 https://github.com/hanxiangmin/Hyper-Knowledge 的安装说明，为 Kimi Code 安装用户级 hyper-knowledge Skill。可使用已有 Python/Conda 环境，覆盖本地修改前先询问。
```

不需要先手动执行命令行安装。安装细节按仓库说明处理；需要登录或授权时由你确认。完成后开启新会话使用。普通网页聊天如果没有本地工具权限，不能替电脑安装程序。

## 在聊天中使用

Codex 显式唤起：

```text
$hyper-knowledge 读取 notes.md，保留高阶关系和成员角色，
在 output/ 下生成校验通过的 Bundle 和离线工作台。
```

Kimi Code 显式唤起：

```text
/skill:hyper-knowledge 读取 notes.md，保留高阶关系和成员角色，
在 output/ 下生成校验通过的 Bundle 和离线工作台。
```

新会话中的自然语言请求：

```text
把 notes.md 构建成高阶知识图谱。人物、地点和时间分别建节点，
展示成员角色和原文依据，生成本地可交互的工作台。
```

是否自动发现与客户端版本、会话刷新有关。[实测记录](compatibility.md)与安装路径适配分别记录。没有本地工具权限的网页聊天，不会自动获得本地 Python 执行能力。

## 默认流程：由当前 Agent 整理

1. Agent 把原文当数据读取，不执行文档夹带的指令。
2. 整理节点、超边、成员角色、来源四张标准表。
3. 使用安装后的启动器调用 bundle import、bundle validate、visualize。
4. 检查结果，交付路径、数量和警告。

无需再给 Hyper-Knowledge 配置一份模型密钥；客户端本身仍使用自己的模型服务，因此不称为“完全离线理解文档”。

双成员超边、多角色和原文字面证据保留在 Bundle v1 中，哈希及统计由 Python 计算。校验通过不代表事实已被人工确认。

## 可选流程：独立模型服务

用户明确选择时，通过 `hk parse --no-index` 使用[项目模型配置](python.md)。文档会发送给该服务，密钥与 Agent 登录独立。两条流程最终使用同一种 Bundle 和工作台。

## 进阶：安装目录与作用范围

以下内容用于了解安装器的行为，不是第三种安装方式。通常保留前面的用户级安装即可。

维护同一份符合 [Agent Skills 标准](https://agentskills.io/specification) 的 `SKILL.md`；平台差异只在安装目录。只供当前项目使用时，把上述安装命令的 `--scope user` 换成 `--scope project --project-root .`，其中 `.` 是终端当前项目目录。

| 目标 | 用户级目录 | 项目级目录 |
| --- | --- | --- |
| codex | 已有 $CODEX_HOME/skills；默认 ~/.codex/skills | .agents/skills |
| kimi | $KIMI_CODE_HOME/skills；默认 ~/.kimi-code/skills | .kimi-code/skills |
| shared（可选） | ~/.agents/skills | .agents/skills |

Codex 当前标准发现目录为 `.agents/skills`；本项目的 codex 安装目标保留此前 Codex 路径兼容性，不静默迁移。安装器发现冲突的共享/平台专用副本时会拒绝重复安装，要求先处理已有安装。目录依据：[Codex 说明](https://learn.chatgpt.com/docs/build-skills)、[Kimi 说明](https://www.kimi.com/code/docs/kimi-code-cli/customization/skills.html)。

安装器将 Windows 的 `runtime/hk.cmd` 或 POSIX 的 `runtime/hk` 绑定到安装时的 Python 解释器，请保留该环境。非开发模式安装不依赖保留源码目录。`agents/openai.yaml` 只是可选界面信息，不是 Kimi 的运行条件。


## 更新、卸载和排查

先激活安装时的环境；Conda 用户执行 `conda activate 环境名`，或在以下命令前改用 `conda run -n 环境名 python`。不要照搬 venv 的目录路径。

运行程序更新后，用同一环境重新执行对应 Skill 安装命令。更新前检查源码和 Skill 的本地修改；更换解释器会改变 Skill 的运行环境，须先确认。[完整说明](install.md#existing-installation)

只有确实要卸载 Kimi 的用户级 Skill 时才执行：

```bash
python -m hyperknowledge skill uninstall --platform kimi --scope user --json
```

可选的启动诊断：

```bash
python -m hyperknowledge skill doctor --platform kimi --scope user --deep --json
```

Codex 使用 `--platform codex`。卸载仅针对对应受管理 Skill，不卸载客户端应用。诊断不是正常安装的必要步骤，也不能代替真实客户端测试。[Conda 激活和 DLL 等常见问题](install.md#installation-check)
