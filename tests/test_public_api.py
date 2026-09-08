"""Public entrypoints run without credentials, a checkout, or implicit embeddings."""

import copy
import json

import pytest
from typer.testing import CliRunner

from hyperknowledge import (
    import_graph,
    read_bundle,
    render_bundle_html,
    validate_bundle,
)
from hyperknowledge.cli.cli import app


@pytest.fixture
def graph_data():
    return {
        "nodes": [
            {"id": "su", "label": "苏轼", "type": "person"},
            {"id": "zhe", "label": "苏辙", "type": "person"},
            {"id": "year", "label": "1101年", "type": "time"},
            {"id": "place", "label": "常州", "type": "place"},
        ],
        "assertions": [
            {
                "id": "return",
                "predicate": "北归",
                "epistemic_status": "model_extracted",
            },
            {
                "id": "brothers",
                "predicate": "兄弟",
                "epistemic_status": "model_extracted",
            },
        ],
        "members": [
            {"assertion_id": "return", "node_id": "su", "role": "actor"},
            {"assertion_id": "return", "node_id": "year", "role": "time"},
            {"assertion_id": "return", "node_id": "place", "role": "destination"},
            {"assertion_id": "brothers", "node_id": "su", "role": "older_brother"},
            {"assertion_id": "brothers", "node_id": "zhe", "role": "younger_brother"},
        ],
    }


def test_keyless_import_render_and_no_input_mutation(tmp_path, monkeypatch, graph_data):
    monkeypatch.setattr(
        "hyperknowledge.utils.client.create_llm",
        lambda *a, **k: pytest.fail("unexpected LLM"),
    )
    monkeypatch.setattr(
        "hyperknowledge.utils.client.create_embedder",
        lambda *a, **k: pytest.fail("unexpected embeddings"),
    )
    before = copy.deepcopy(graph_data)
    result = import_graph(graph_data, output_dir=tmp_path / "中文 路径")
    assert graph_data == before
    assert result.ka_path is None
    assert (result.node_count, result.hyperedge_count, result.pairwise_count) == (
        4,
        2,
        0,
    )
    assert validate_bundle(result.bundle_path)["status"] == "passed"
    tables = read_bundle(result.bundle_path)
    assert all(a["topology"] == "hyperedge" for a in tables["assertions"])
    assert [m["ordinal"] for m in tables["members"]] == [0, 1, 2, 0, 1]
    page = tmp_path / "workbench.html"
    render_bundle_html(result.bundle_path, page)
    assert page.is_file() and page.stat().st_size > 10000
    assert tables["manifest"]["table_sha256"]["nodes.jsonl"]


def test_sources_copied_and_quotes_validated(tmp_path, graph_data):
    source = tmp_path / "原文.md"
    source.write_text("1101年，苏轼北归抵达常州。\n", encoding="utf-8")
    graph_data["evidence"] = [
        {
            "id": "ev",
            "type": "source_text_span",
            "source": "notes.md",
            "line_start": 1,
            "line_end": 1,
            "quote": "苏轼北归抵达常州",
        }
    ]
    graph_data["assertions"][0]["evidence_refs"] = ["ev"]
    target = tmp_path / "bundle"
    import_graph(
        graph_data, output_dir=target, sources={"notes.md": source}, quality="showcase"
    )
    assert (target / "sources/notes.md").read_bytes() == source.read_bytes()
    original = (target / "manifest.json").read_bytes()
    graph_data["evidence"][0]["quote"] = "原文没有这句话"
    with pytest.raises(ValueError, match="Invalid graph"):
        import_graph(
            graph_data,
            output_dir=target,
            sources={"notes.md": source},
            quality="showcase",
            force=True,
        )
    assert (target / "manifest.json").read_bytes() == original
    assert not list(tmp_path.glob("bundle.backup-*"))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d["nodes"].append(d["nodes"][0]),
        lambda d: d["members"].append(d["members"][0]),
        lambda d: d["members"][0].update(assertion_id="missing"),
        lambda d: d["assertions"][0].update(evidence_refs=["missing"]),
        lambda d: d["assertions"][0].update(directed=True),
        lambda d: d["members"][0].update(role=""),
        lambda d: d["members"][0].update(ordinal=True),
        lambda d: d["assertions"][0].update(id=[]),
    ],
)
def test_bad_graph_rejected(tmp_path, graph_data, mutation):
    mutation(graph_data)
    with pytest.raises(ValueError):
        import_graph(graph_data, output_dir=tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_multiple_roles_do_not_inflate_arity(tmp_path, graph_data):
    graph_data["members"].append(
        {"assertion_id": "brothers", "node_id": "su", "role": "author"}
    )
    result = import_graph(graph_data, output_dir=tmp_path / "out")
    assert result.hyperedge_count == 2
    assert len(read_bundle(result.bundle_path)["members"]) == 6


def test_force_keeps_backup_and_default_refuses(tmp_path, graph_data):
    target = tmp_path / "out"
    import_graph(graph_data, output_dir=target)
    (target / "my-note.txt").write_text("keep me", encoding="utf-8")
    with pytest.raises(FileExistsError):
        import_graph(graph_data, output_dir=target)
    import_graph(graph_data, output_dir=target, force=True)
    backups = list(tmp_path.glob("out.backup-*"))
    assert len(backups) == 1 and (backups[0] / "my-note.txt").read_text() == "keep me"


@pytest.mark.parametrize("name", ["../escape", "/absolute", "C:/absolute", "a\\b"])
def test_source_name_traversal(tmp_path, graph_data, name):
    with pytest.raises(ValueError, match="source|Source"):
        import_graph(graph_data, output_dir=tmp_path / "out", sources={name: "unread"})


def test_json_cannot_request_file_reads(tmp_path, graph_data):
    graph_data["sources"] = {"secret": "C:/Users/HAN/secret"}
    with pytest.raises(ValueError, match="Unexpected"):
        import_graph(graph_data, output_dir=tmp_path / "out")


def test_cli_import_json_receipts(tmp_path, graph_data):
    source = tmp_path / "graph.json"
    source.write_text(json.dumps(graph_data), encoding="utf-8")
    result = CliRunner().invoke(
        app, ["bundle", "import", str(source), "-o", str(tmp_path / "out"), "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["hyperedge_count"] == 2
    result = CliRunner().invoke(
        app, ["bundle", "import", str(source), "-o", str(tmp_path / "out"), "--json"]
    )
    assert result.exit_code == 1 and json.loads(result.stdout)["ok"] is False


def test_deferred_embeddings_and_explicit_client(tmp_path, monkeypatch):
    from hyperknowledge import Template
    from hyperknowledge.runtime_clients import DeferredEmbeddings
    from tests.mocks import MockChatModel

    monkeypatch.setattr(
        "hyperknowledge.runtime_clients.configured_llm",
        lambda: pytest.fail("unexpected default LLM"),
    )
    monkeypatch.setattr(
        "hyperknowledge.utils.client.create_embedder",
        lambda *a, **k: pytest.fail("eager embedder"),
    )
    template = Template.create(
        "general/hypergraph", "zh", llm_client=MockChatModel(), defer_embeddings=True
    )
    assert isinstance(template.embedder, DeferredEmbeddings)
    # The real engine can accept and save structured data without resolving an embedder.
    template.dump(tmp_path / "ka")
    assert (tmp_path / "ka/data.json").is_file()


def test_extract_file_uses_existing_engine(tmp_path, monkeypatch):
    from hyperknowledge import extract_file, extract_text
    from hyperknowledge.types.hypergraph import AutoHypergraph
    from tests.mocks import MockChatModel

    def feed(self, text):
        self._set_data_state(
            self.graph_schema(
                nodes=[{"name": "甲", "type": "人物"}, {"name": "乙", "type": "人物"}],
                edges=[{"name": "合作", "type": "合作", "actors": ["甲", "乙"]}],
            )
        )
        return self

    monkeypatch.setattr(AutoHypergraph, "feed_text", feed)
    source = tmp_path / "资料.md"
    source.write_bytes(b"\xef\xbb\xbf" + "甲和乙合作。".encode("utf-8"))
    result = extract_file(
        source, output_dir=tmp_path / "result", llm_client=MockChatModel()
    )
    assert result.hyperedge_count == 1
    assert (result.ka_path / "sources/资料.md").read_bytes() == source.read_bytes()
    assert read_bundle(result.bundle_path)["manifest"]["source_ka"] == str(
        result.ka_path
    )
    assert not (result.ka_path / "index").exists()
    with pytest.raises(ValueError, match="empty"):
        extract_text(" ", output_dir=tmp_path / "empty")
    with pytest.raises(ValueError, match="supports"):
        extract_file(tmp_path / "document.pdf", output_dir=tmp_path / "pdf")


def test_deferred_embeddings_fail_only_on_use(tmp_path):
    from hyperknowledge.runtime_clients import DeferredEmbeddings

    client = DeferredEmbeddings(tmp_path / "absent.toml")
    assert client._client is None
    with pytest.raises(ValueError, match="needs embeddings"):
        client.embed_query("test")


def test_table_hash_integrity(tmp_path, graph_data):
    result = import_graph(graph_data, output_dir=tmp_path / "out")
    path = result.bundle_path / "nodes.jsonl"
    path.write_text(
        path.read_text(encoding="utf-8").replace("苏轼", "someone"), encoding="utf-8"
    )
    receipt = validate_bundle(result.bundle_path)
    assert receipt["status"] == "failed"
    assert any(d["code"] == "bundle.table_sha256" for d in receipt["diagnostics"])


def test_source_alias_collision(tmp_path, graph_data):
    source = tmp_path / "input.txt"
    source.write_text("test", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate source"):
        import_graph(
            graph_data,
            output_dir=tmp_path / "out",
            sources={"A.md": source, "a.md": source},
        )
