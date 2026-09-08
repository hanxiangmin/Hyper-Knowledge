# Python 与 Notebook

Python、命令行和 Skill 共用一套运行程序。在长期保留的 Python 3.11+ 环境中[安装一次](install.md#python)即可。

## 解析一份文档

先配置模型服务；这条流程会把文档文本发送给所选服务。

```python
from hyperknowledge import extract_file, render_bundle_html

result = extract_file("notes.md", output_dir="output", language="zh")
render_bundle_html(result.bundle_path, "output/workbench.html")
print(result.to_dict())
```

字符串使用 `extract_text("文本……", output_dir="output/text")`。两个接口复用现有模板引擎，默认模板为 `general/hypergraph`，同时保存 Knowledge Abstract 与 Bundle v1，**默认不建立向量索引**。

## 用到什么，配置什么

`hk config llm` 配置的是独立 Python/CLI 的模型服务，不是复用 Codex 或 Kimi 登录。配置文件为 `~/.hk/config.toml`。

```bash
hk config llm --provider openai --model YOUR_AVAILABLE_MODEL
```

密钥可放在环境变量中：OpenAI 兼容服务使用 `OPENAI_API_KEY`，Anthropic 使用 `ANTHROPIC_API_KEY`；也支持现有配置文件。兼容端点使用 `--base-url`。不要把密钥提交到 Git；复制一个 `.env` 并不等于完成 CLI 配置。

也可以显式传入客户端：

```python
import os
from langchain_openai import ChatOpenAI
from hyperknowledge import extract_text

client = ChatOpenAI(model=os.environ["HK_CHAT_MODEL"])
result = extract_text(
    "某研究者在一次会议上报告了一项研究。",
    output_dir="output/text",
    language="zh",
    llm_client=client,
)
```

客户端应支持模板引擎使用的 LangChain 聊天与结构化输出接口。其他已支持的模型服务使用相应客户端包；具体模型是否可用取决于该服务与账号。

只有设置 `build_index=True`、执行语义检索等需要向量的操作时，才加载向量客户端。只解析、不建索引，无需先配置向量模型；缺少配置会明确报错，不生成假向量。

## 不调用模型的结构化导入

使用仓库中的[四节点样例](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/python)：

```python
from hyperknowledge import import_graph, read_bundle, validate_bundle, render_bundle_html

result = import_graph(
    "examples/python/graph.json",
    sources={"notes.md": "examples/python/notes.md"},
    output_dir="output/tutorial/bundle",
    quality="showcase",
)
tables = read_bundle(result.bundle_path)
print([(node["label"], node["type"]) for node in tables["nodes"]])
assert validate_bundle(result.bundle_path)["status"] == "passed"
render_bundle_html(result.bundle_path, "output/tutorial/workbench.html")
```

输入可为 Python 字典或 JSON 路径。双成员超边、多角色原样保留；Python 计算哈希和统计，检查引用，不替输入补造事实或证据。只读取 `sources=` 中明确指定的文件，不执行 JSON 中提出的文件读取要求。

[数据格式和接口参考](api.md#import-graph) · [同一份输入的 CLI 流程](commands.md)

## Notebook

[quickstart.ipynb](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/python/quickstart.ipynb) 是可执行的 Notebook：构造输入、导入、查看节点与成员角色、校验、嵌入交互工作台。

Anaconda / Miniconda 用户先按[同一环境的内核设置](install.md#conda-notebook)选择 **Python (Hyper-Knowledge)**。已经在该环境安装好运行程序，无需重复安装；先在 Notebook 运行 `import sys; print(sys.executable)` 确认内核。

只有当前内核还没有安装项目时，才用 `%pip` 安装到当前内核环境：

```python
%pip install "hyper-knowledge[notebook] @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

通过 `sys.executable` 核对内核；升级后重启内核。尚未发布的本地修改请安装本地构建的 wheel。HTML 应生成在 Notebook 所在目录之下，才能由 Jupyter 提供给嵌入页面：

```python
from IPython.display import IFrame
IFrame("output/tutorial/workbench.html", width="100%", height=720)
```

Notebook 完整执行与浏览器交互分别验证，见[兼容性记录](compatibility.md)。

## 输出与重复运行

`GraphResult` 包含 `ka_path`（导入时为 None）、`bundle_path`、`node_count`、`hyperedge_count`、`pairwise_count` 和 `warnings`；`.to_dict()` 返回可序列化字典。

重复运行时优先换输出目录。解析和导入默认拒绝覆盖非空目录；明确设置 `force=True` 后，将旧目录保留为旁边的 `.backup-...` 备份，先校验新结果再替换。HTML 渲染沿用原有覆盖行为，需要保留旧文件时请使用新文件名。
