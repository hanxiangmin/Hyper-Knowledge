# 安装 Skill

Hyper-Knowledge 在本地 Python 环境中运行。下面的安装方式会准备好运行程序，并把 Skill 加入 Codex。

## 在 Codex 聊天框安装（推荐）

直接将下面这段话复制到本地 Codex 的聊天框，不需要打开终端，也不需要加 `codex` 前缀：

```text
请帮我安装 https://github.com/hanxiangmin/Hyper-Knowledge 中的 hyper-knowledge。
请按仓库说明，在本地 Python 虚拟环境中安装运行程序和用户级 Codex Skill。
已有安装如有本地修改，请先询问再覆盖。
```

按提示确认联网和写入权限即可。如果安装后 Skill 没有出现，重启 Codex。[OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)

## 从命令行发起（可选） { #terminal }

已安装并登录 Codex CLI 后，在准备保存项目的目录中运行（Bash / PowerShell）：

```bash
codex '请帮我安装 https://github.com/hanxiangmin/Hyper-Knowledge 中的 hyper-knowledge。请按仓库说明，在本地 Python 虚拟环境中安装运行程序和用户级 Codex Skill。已有安装如有本地修改，请先询问再覆盖。'
```

这是从终端发起同样的安装请求，执行时按提示确认操作。[Codex CLI 官方用法](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## 手动安装

需要 Python 3.11 或更新版本。在准备保存源码的普通本地目录中执行：

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
python -m venv .venv
```

激活环境：

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

随后安装运行时及用户级 Skill：

```bash
python -m pip install -e .
hk skill install --scope user --json
```

安装后即可使用。Skill 的启动器会使用这个 Python 环境，请保留源码目录和 `.venv`；更换环境后重新安装 Skill。

## 只用于当前项目

把上面的最后一条命令替换为：

```bash
hk skill install --scope project --project-root . --json
```

项目级安装便于团队明确这个项目使用哪个运行环境，用户级安装适合个人跨项目使用。当前托管集成针对 Codex；其他支持 Agent Skills 的客户端需自行确认运行时调用方式。

## 不配模型，先看结果

```bash
hk skill demo -o output/first-demo --json
```

打开回执中的 HTML 路径。演示使用程序构造的合成数据，不调用模型，也不需要上传文档。它检查安装和图谱流程，不代表真实文档的抽取准确率。

已经有运行时，只需要安装 Skill 指令包时，可以使用：

```bash
npx skills add hanxiangmin/Hyper-Knowledge --skill hyper-knowledge -g
```

下一步：[处理自己的文档](document.md)。遇到问题先看[排查顺序](faq.md)。

## 安装自检（可选） { #installation-check }

如果 Skill 无法启动，可以运行以下命令定位问题。它检查 Skill 文件、Python 路径和启动器，并用内置示例试跑图谱生成。

```bash
hk skill doctor --scope user --deep --json
```

`doctor` 的意思是安装诊断。`--deep` 加上实际试跑，`--json` 让 Codex 方便读取结果。这不是安装前置条件；整个检查在本地完成，不上传文档，也不调用模型。项目级安装改用 `--scope project --project-root .`。
