# 兼容性与测试记录

这里区分“已经实现的支持”与“真实客户端完整跑通”。
记录日期：**2026-09-08**；对象为基于 0.8.0 的多入口源码更新。
以下为本地验证记录；各提交的远程检查结果请查看 [GitHub Actions](https://github.com/hanxiangmin/Hyper-Knowledge/actions)。PyPI 发布不包含在本次源码更新中。

## 运行程序与安装

| 检查项 | 环境 | 结果 |
| --- | --- | --- |
| 全量单元与回归测试 | Windows，Python 3.12.14 | 622 通过、10 跳过；外部服务跳过项不算通过 |
| 标准 Skill 校验 | skill-creator 校验器 | 通过 |
| sdist → wheel、安装包元数据 | hatchling / build / twine | 通过 |
| 脱离源码目录的非开发模式 wheel | 干净 Windows Python 3.12.14 环境 | 导入、校验、渲染和 CLI 通过 |
| pip 从 sdist 安装 | 同一独立环境，非开发模式 | 通过 |
| Codex 与 Kimi 安装器 | 隔离的项目级目录 | 重复安装、绑定启动器、深度检查、本地修改保护通过 |
| Notebook | 独立环境中新内核 | 所有代码单元完整执行 |
| 文档中的无需密钥示例 | 中英文 Python/API 指南 | 已实际执行，不只检查语法 |
| 上轮 venv 安装教程 | Windows PowerShell，独立空环境，中文及空格路径 | 本地 wheel 试装、已有环境保护、新终端完整路径调用、两个客户端安装器及无模型演示通过；当时 48 个 PowerShell 示例通过语法检查 |
| 本轮环境分支与简短聊天说明 | 中英文 README、首页、安装及 Agent 指南 | 16 项文档一致性检查及 4 个可运行 Python 示例通过；PowerShell 示例语法检查通过 |
| Conda 命令核对 | 本机 Conda 26.5.3 | 环境列表与 conda run 选择解释器的只读检查通过；未新建环境安装 Hyper-Knowledge，不标注 Conda 完整实装通过 |
| Windows / Linux，Python 3.11 / 3.12 | package-test.yml | 已配置；以对应提交的 Actions 结果为准，不从本地单环境测试推定全平台通过 |
| 独立模型真实解析 | 本机未配置模型服务 | 未运行；单元测试验证接口适配，不代表模型服务可用 |

构建并安装 wheel 后可复现：

```bash
python -m build
python -m twine check dist/*
# 离开源码目录，使用已安装环境的 Python：
python /path/to/Hyper-Knowledge/tools/verify_package.py --notebook /path/to/Hyper-Knowledge/examples/python/quickstart.ipynb
```

检查脚本验证包内模板、Skill 资源、中文路径、机器结果、重复安装保护以及全新 Notebook 内核，不修改用户级 Skill。

上轮 venv 教程由 `tools/check_install_docs.py` 以本地 wheel 和临时项目目录试装，通过仅对测试进程设置的 HTTPS 镜像完成依赖下载，没有修改用户级 Skill。本轮按已有环境、Conda 和 venv 重组文档，执行 `--syntax-only` 检查，8 处入口的 Conda 与运行程序步骤保持一致，Codex 和 Kimi Code 分别提供完整可复制的简短请求。该结果不等于公开 GitHub 安装、Conda 完整实装或真实客户端会话通过。macOS / Linux 的教程执行仍未实测。

## 真实客户端与浏览器

| 客户端 / 界面 | 尝试 | 当前结果 |
| --- | --- | --- |
| Codex CLI 0.149.1 | 新会话；使用已配置的 gpt-6-astra | 后端要求更新 CLI |
| 隔离 Codex CLI 0.153.4 | 新会话；显式唤起；同一文档样例 | 已启动模型会话并读取文档，但 Windows 沙箱拒绝读取项目 Skill；完整导入未通过 |
| Kimi Code 0.41.0 | 客户端启动、设备登录 | 启动成功；OAuth 在返回验证码前连接失败，未完成模型会话或解析测试 |
| 浏览器插件 | 连接本地工作台 | 运行环境拒绝加载所需模块，插件连接未恢复 |
| 独立本地 Chrome | 经用户同意使用独立浏览器；中英文苏辙截图 | 实际点击苏辙，高亮 4 条关联超边；检查未发现高亮标签遮挡节点，工作台源文件未改动 |
| 文档截图放大/返回 | 中英文，桌面与手机尺寸 | 56 次图片交互通过，包括图片、背景、关闭按钮和 Esc 返回，焦点及滚动位置恢复 |
| 文档搜索巡检 | 独立浏览器，中英文 | 桌面搜索通过；移动端等待搜索结果超时，尚未解决，不将整个浏览器巡检标为通过 |
| 其他智能体 | 未执行 | 未测试，不添加兼容徽章 |

Codex 的这次尝试区分了原文事实与夹带的恶意指令，但这一点不等于端到端安全验收通过。自然语言发现、实际启动器调用、两个客户端产物对比和客户端生成工作台的完整交互仍是待完成项。没有通过关闭客户端沙箱或修改凭据绕过这些阻塞。

当前视觉设计未改动。HTML 生成和回归测试不能替代逐个点击视图、节点、超边与悬停状态。

## 继续完成客户端验收

客户端登录可用、文件和命令权限正常后，可使用隔离测试工具：

```bash
python tools/run_agent_check.py --platform codex --client /path/to/codex --workspace /new/test-directory
python tools/run_agent_check.py --platform codex --client /path/to/codex --workspace /another/new-directory --natural
```

Kimi 使用 `--platform kimi` 及对应可执行文件；登录仍由用户操作。日志和结果保存在指定的新目录，不向用户级安装。

完整通过还需核对客户端版本/模型、实际读取的 Skill 路径、启动器命令、Bundle 成员角色和原文片段、双成员超边、未执行恶意指令，以及浏览器交互。安装测试通过不等于客户端测试通过。

## 发布条件

源码与文档通过 GitHub 发布；PyPI 是独立发布流程，当前仍使用源码安装。
正式发布后，还需在干净环境中验证 `python -m pip install hyper-knowledge`，再把它提升为公开安装入口。
