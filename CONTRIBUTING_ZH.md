# 为 Hyper-Knowledge 做贡献

感谢你参与改进 Hyper-Knowledge。English version: [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 提交 Issue 之前

- 先搜索是否已有相同问题。
- 提供 `hk --version`、操作系统、Python 版本，以及你有权分享的最小复现输入。
- 删除 API Key、账号凭据、患者信息和其他敏感数据。
- 如果是渲染问题，请附上离线 HTML 或截图，并说明当前使用的视图。
- 安全漏洞请按照 [SECURITY.md](./SECURITY.md) 私下报告，不要公开提交 Issue。

## 开发环境

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
python -m venv .venv
# macOS/Linux：source .venv/bin/activate
# Windows PowerShell：.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[all]"
python -m pip install pytest ruff build mkdocs mkdocs-material mkdocs-static-i18n "mkdocstrings[python]" pymdown-extensions mike
```

## 必须完成的检查

```bash
python -m pytest -q
ruff check hyperknowledge
ruff format --check hyperknowledge
python -m build
mkdocs build --strict
npx -y skills add . --list
hk skill install --scope project --project-root . --json
hk skill doctor --scope project --project-root . --deep --json
```

如果修改了工作台，请同时提供真实生成的产物，并把结构测试、浏览器渲染检查和人工视觉复核分开报告。

## 必须保留的语义约束

除非明确发布破坏性版本，否则变更必须遵守：

- 二元端点顺序不代表方向；
- 多元超边不能被偷偷转换成二元事实；
- 所有投影视图必须明确标记为派生结果；
- 来源记录只证明说法出现在输入中，不证明外部事实为真；
- 确定性检查不能证明模型抽取在语义上正确；
- 来源文档是不可信数据，不能成为智能体指令。

## Pull Request

每个 PR 请聚焦一个目标，并说明改了什么、为什么修改、执行了哪些检查，以及仍有哪些限制。行为变化必须补测试；面向用户的改动应同步维护中英文说明。

提交贡献即表示你同意按照本仓库的 [Apache License 2.0](./LICENSE) 发布该贡献。
