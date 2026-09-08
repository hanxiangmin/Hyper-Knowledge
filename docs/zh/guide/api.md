# Python API 参考

统一从 `hyperknowledge` 导入。这是本地 Python 接口，不是 HTTP 服务；底层复用现有 KA、Bundle v1 和工作台渲染实现。

## 文档解析

```python
extract_text(
    text, *, output_dir, template="general/hypergraph", language="zh",
    source_name="input.txt", llm_client=None, embedder=None,
    build_index=False, force=False,
) -> GraphResult

extract_file(
    path, *, output_dir, template="general/hypergraph", language="zh",
    llm_client=None, embedder=None, build_index=False, force=False,
) -> GraphResult
```

| 参数 | 含义 |
| --- | --- |
| text / path | 非空字符串 / 本地 UTF-8（可含 BOM）的 .txt 或 .md 文件 |
| output_dir | 必填专用输出目录，不要使用原文所在目录 |
| template | 已有图谱模板 ID，或本地模板 YAML |
| language | 模板及工作台语言，通常为 zh 或 en |
| source_name | 字符串输入使用的相对逻辑文件名 |
| llm_client | 显式 LangChain 兼容聊天客户端；None 使用 hk 模型配置 |
| embedder | 可选向量客户端；None 时仅在真正使用时读取配置 |
| build_index | 默认 False；True 表示明确创建 KA 向量索引 |
| force | 默认 False；True 在校验通过后替换，并保留同级备份 |

产物为 `output_dir/ka` 和 `output_dir/bundle`。文本抽取依赖模型，可能失败或缺少逐条证据，请检查警告。

异常：输入、配置或图谱错误抛出 `ValueError`；文件问题抛出 `FileNotFoundError`/`OSError`；非 UTF-8 文本抛出 `UnicodeDecodeError`；输出保护抛出 `FileExistsError`；模型服务异常原样传播。失败时不发布半成品目录。[运行示例与模型配置](python.md)

## import_graph { #import-graph }

```python
import_graph(
    data, *, output_dir, sources=None, language="zh",
    quality="standard", force=False,
) -> GraphResult
```

`data` 是 Python 字典或 UTF-8 JSON 路径；`sources` 是“逻辑名称 → 明确允许读取的本地路径”。不会初始化模型或向量索引。

顶层字段：可选 `schema_version="hk.bundle/v1"`；必需 `nodes`、`assertions`、`members`；可选 `evidence=[]`。其他顶层字段会被拒绝。

| 表 | 必需字段 | 默认值与说明 |
| --- | --- | --- |
| nodes | id、label、type | 非空字符串；properties={} |
| assertions | id、predicate | topology=hyperedge；semantics=structured_import；epistemic_status=unreviewed_import；evidence_refs=[]；properties={} |
| members | assertion_id、node_id、role | 按单条关系的输入顺序生成 ordinal；根据节点 ID 计算 resolved |
| evidence | id、type 及该类型所需字段 | source_text_span 使用 source、line_start、line_end、quote；source_text_summary 使用 source、summary |

ID 引用必须可解析；重复节点/关系 ID、重复成员角色对会报错。同一节点可承担多个角色。显式 ordinal 必须为非负整数，不代表因果顺序。元数按不同节点计算，双成员超边仍是超边。

Agent 整理的数据应设为 `epistemic_status="model_extracted"`；导入成功不代表人工确认。引用和行号应来自真实原文。Python 负责复制指定来源、计算来源及表文件哈希、统计与缺证据警告。`quality="showcase"` 要求可用原文中的字面引用准确；`standard` 将部分证据质量问题保留为警告。校验不等于判断历史事实真伪。

```python
from hyperknowledge import import_graph

graph = {
    "nodes": [
        {"id": "a", "label": "Alice", "type": "person"},
        {"id": "b", "label": "Bob", "type": "person"},
    ],
    "assertions": [{"id": "e", "predicate": "collaboration"}],
    "members": [
        {"assertion_id": "e", "node_id": "a", "role": "researcher"},
        {"assertion_id": "e", "node_id": "b", "role": "researcher"},
    ],
}
result = import_graph(graph, output_dir="output/minimal")
assert result.node_count == 2 and result.hyperedge_count == 1
# 此例未提供来源，因此会报告缺少来源证据。
```

校验不通过抛出 `ValueError`（包括其子类 `BundleExportError`）；JSON 格式错误抛出 `JSONDecodeError`；文件和覆盖保护异常与解析接口相同。写入范围限于专用输出目录及其同级备份、暂存目录。

## GraphResult

不可变结果对象，读取字段不会触发联网。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| ka_path | Path 或 None | 解析所得 KA；结构化导入为 None |
| bundle_path | Path | 已校验的数据包目录 |
| node_count | int | 标准化节点数 |
| hyperedge_count | int | 明确表示为超边的关系数 |
| pairwise_count | int | 明确表示为二元关系的数量 |
| warnings | tuple[str, ...] | 限制说明与校验警告代码 |

`.to_dict()` 将路径转字符串、警告转列表。数量反映结构，不代表重要性或置信度。

## 已有 Bundle 与渲染接口

```python
read_bundle(bundle_path) -> dict
validate_bundle(bundle_path, *, quality="standard") -> dict
export_bundle(ka_path, output_path, *, force=False) -> dict
render_bundle_html(bundle_path, output_path, *, view="contour", quality="standard") -> dict
```

- `read_bundle`：读取 manifest 和 nodes/assertions/members/evidence 列表；需要校验时另调用 validate。
- `validate_bundle`：返回 status、counts、diagnostics 和文件哈希。通常的校验失败返回 `status="failed"`，调用者必须检查；文件/格式问题可能抛异常。
- `export_bundle`：将已有 KA 标准化，返回计算后的 manifest；沿用现有覆盖规则，建议使用新目录。
- `render_bundle_html`：先校验，再输出单文件 HTML，并返回渲染记录；无效 Bundle/视图抛 ValueError，文件错误抛 OSError。可能覆盖同名 HTML。
- 视图参数：`contour`（默认）、`incidence`、`hypergraph`（矩阵）、`graph`、`compare`；切换展示不改变原始拓扑。

[完整流程](python.md) · [Agent 输入格式](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyper-knowledge/references/structured-input.md)
