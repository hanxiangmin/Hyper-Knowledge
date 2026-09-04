# 安装与检查

安装分成两件事：Python 环境运行 `hk`，Skill 告诉智能体何时、怎样调用它。只复制 `SKILL.md` 不会自动安装运行时。

## 安装到你的环境

需要 Python 3.11 或更新版本。在准备长期保留的目录中执行：

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
hk --version
hk skill install --scope user --json
hk skill doctor --scope user --deep --json
```

托管安装会生成绑定该 Python 环境的启动器。安装后不要删除或随意移动 `.venv`；若更换环境，重新安装 Skill 并运行 doctor。

## 只用于当前项目

把上面的最后两条命令替换为：

```bash
hk skill install --scope project --project-root . --json
hk skill doctor --scope project --project-root . --deep --json
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
