# 命令行配方

先完成[命令行或聊天安装](install.md)，再使用本页配方。所有相对路径均从终端当前目录开始；示例中的文件需要由你提供或下载。

## 先让当前终端找到 `hk` { #prepare-shell }

`hk` 是安装后生成的快捷命令，不是系统内置命令。按安装时选择的环境准备终端，下面只做适合自己的一种。

**Anaconda / Miniconda 用户**：打开 Conda 终端，激活安装时的环境；如果用了其他环境名，请替换 `hyper-knowledge`。

```bash
conda activate hyper-knowledge
python -c "import sys; print(sys.executable)"
hk --help
```

不想手动激活时，可把配方开头的 `hk` 换成 `conda run -n hyper-knowledge python -m hyperknowledge`。

**按教程创建了 venv 的 Windows 用户**：PowerShell 只在**当前窗口**临时加入该环境的命令目录，无需修改脚本执行策略；这不是 Conda 的目录：

```powershell
$hkScripts = Join-Path $env:USERPROFILE ".venvs\hyper-knowledge\Scripts"
if (-not (Test-Path -LiteralPath (Join-Path $hkScripts "hk.exe"))) {
    throw "Hyper-Knowledge is not installed at this path. Follow the installation guide first."
}
$env:PATH = "$hkScripts;$env:PATH"
hk --help
```

**按教程创建了 venv 的 macOS / Linux 用户**：

```bash
source "$HOME/.venvs/hyper-knowledge/bin/activate"
hk --help
```

**其他已有环境用户**：按平时的方式激活，并执行 `python -m hyperknowledge --help`。看到帮助后再运行配方；新开终端要重新选择环境。`hk` 简写不可用时，在已选好的环境中用 `python -m hyperknowledge` 替换即可。[环境选择与完整路径说明](install.md#reopen-shell)

## 文档 → KA → Bundle → 工作台

先[配置聊天模型](python.md)，然后执行：

```bash
hk parse notes.md -t general/hypergraph -l zh --no-index -o output/ka
hk bundle export output/ka -o output/bundle
hk visualize output/bundle -o output/workbench.html --no-open
```

`--no-index` 不建立索引，不要求向量模型；文档解析仍使用模型服务。

## 结构化输入，无需模型密钥

与 Python、Notebook 使用同一份[教程输入](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/python)：

```bash
hk bundle import examples/python/graph.json --source notes.md=examples/python/notes.md -o output/cli-bundle --json
hk bundle validate output/cli-bundle --quality showcase --json
hk visualize output/cli-bundle -o output/cli-workbench.html --no-open --json
```

`bundle import` 与 `import_graph()` 共用实现。
多个来源可重复传入 `--source NAME=PATH`；含空格的参数加引号。
`--quality` 默认 standard，showcase 加强证据检查。
通常使用新输出目录；`--force` 必须主动指定，替换时保留同级备份。

## 批量处理文档

Bash：

```bash
for file in notes/*.md; do
  name="$(basename "$file" .md)"
  hk parse "$file" -t general/hypergraph -l zh --no-index -o "output/$name/ka" &&
  hk bundle export "output/$name/ka" -o "output/$name/bundle" &&
  hk visualize "output/$name/bundle" -o "output/$name/workbench.html" --no-open || exit 1
done
```

PowerShell：

```powershell
Get-ChildItem notes -Filter *.md | ForEach-Object {
  $target = Join-Path output $_.BaseName
  hk parse $_.FullName -t general/hypergraph -l zh --no-index -o "$target/ka"
  if ($LASTEXITCODE) { throw "Parse failed" }
  hk bundle export "$target/ka" -o "$target/bundle"
  if ($LASTEXITCODE) { throw "Export failed" }
  hk visualize "$target/bundle" -o "$target/workbench.html" --no-open
  if ($LASTEXITCODE) { throw "Render failed" }
}
```

每份文档使用独立输出和来源记录，失败即停止；不会隐式合并成一张图。

## 机器调用与失败处理

import/export/validate/visualize 支持 `--json`，它不是所有命令通用的参数。
导入成功返回 `ok=true`、路径、计数和警告，退出码 0；
导入失败返回 `ok=false`、error 和退出码 1；命令行参数错误使用非零用法错误码。
校验调用方必须检查进程退出码及结果 status。
依赖日志可能出现在 stderr，JSON 应从 stdout 读取，不要将两者混合解析。

## 可选检查与帮助

```bash
hk skill doctor --platform codex --scope user --deep --json
hk bundle import --help
hk parse --help
hk visualize --help
```

doctor 仅用于安装诊断，平台和范围与实际安装一致。
