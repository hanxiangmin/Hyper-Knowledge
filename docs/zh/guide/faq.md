# 常见问题与排查

## 我需要搭建服务器吗？

本地运行程序和导出的工作台不需要网站服务器。默认 Skill 流程使用当前 Agent 的模型理解文档；独立 Python/CLI 解析使用单独配置的模型；结构化导入和画图不需要模型服务。[选择执行流程](agents.md)。

这个 GitHub Pages 站点用于说明和展示，不提供文档上传解析服务。

## 已经有 bundle，还要再解析吗？

不用。先校验，再渲染。改视图、查看成员、拖动节点或重新取景都不需要重新抽取文档。[已有 bundle 的命令](commands.md)

## 为什么 Skill 装好了，却找不到 hk？

只复制 Skill 文件并不等于安装了 Python 运行程序。即使运行程序已装好，终端不在对应环境中也可能找不到 `hk`。请先用明确的 Python 路径查看帮助，而不是再执行一次找不到的命令。

**Conda 用户**：不必猜 Python 的安装路径，指定环境即可；如果环境名不同，请替换：

```bash
conda run -n hyper-knowledge python -m hyperknowledge --help
```

**venv 用户**，按教程创建环境后的 Windows PowerShell 命令：

```powershell
& "$env:USERPROFILE\.venvs\hyper-knowledge\Scripts\python.exe" -m hyperknowledge --help
```

按教程创建 venv 后的 macOS / Linux 命令：

```bash
"$HOME/.venvs/hyper-knowledge/bin/python" -m hyperknowledge --help
```

其他已有环境按原方式激活，再执行 `python -m hyperknowledge --help`。帮助能显示时，不必重装；[准备当前终端的快捷命令](commands.md#prepare-shell)即可。提示模块或路径不存在时，回到[完整安装步骤](install.md)。仍无法启动再使用[可选诊断](install.md#installation-check)，不要靠关闭检查或随意改路径掩盖问题。

## 能直接读 PDF 和扫描件吗？

当前文本入口处理 `.txt` 和 `.md`。PDF、Word 和图像需要先转换，并保留段落与来源定位。OCR 错字会影响实体和关系识别，值得在抽取前复核。

## 有来源记录，为什么还要检查？

来源覆盖表示存在引用记录；不代表引用确实支持整条断言，更不代表输入材料真实可靠。结构通过、来源可追溯、语义正确是不同检查。[详细解释](artifacts.md)

## 多个年份和地点又混到了一起怎么办？

回到建模层检查事件范围。不同经历分别建超边，同一人物复用节点；同一事件的多个时间点则用明确的开始、结束等角色区分。只移动图上的圆圈不能解决语义混合。[建模示例](modeling.md)

## 图太密，应该隐藏节点吗？

先用矩阵查成员，再用关联视图聚焦一个节点或一条超边。显示上淡化或暂时隐藏其他元素，不等于删掉数据。包络适合看共享结构，不必承担逐项核对的所有任务。

## 如何报告问题？

附上命令、版本、错误回执和最小可复现输入；涉及私密材料时，提供去标识化示例。布局问题附上视图类型、所选节点或超边，以及窗口大小。请先移除密钥和无关个人信息。

[提交 Issue](https://github.com/hanxiangmin/Hyper-Knowledge/issues)
