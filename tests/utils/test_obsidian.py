"""Unit tests for the Obsidian vault exporter (hyperknowledge.utils.obsidian).

These tests exercise the exporter directly with plain Pydantic models and
lambda extractors — no LLM/embedder is involved, so they are fast and fully
deterministic.
"""

from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from hyperknowledge.utils.obsidian import (
    export_to_obsidian,
    sanitize_filename,
    _render_frontmatter,
)


# ---------------------------------------------------------------------------
# Schemas + helpers
# ---------------------------------------------------------------------------


class Entity(BaseModel):
    name: str
    type: str = "ENTITY"
    description: Optional[str] = None
    properties: dict = Field(default_factory=dict)


class Relation(BaseModel):
    source: str
    target: str
    relation_type: str
    description: Optional[str] = None


class Event(BaseModel):
    """N-ary hyperedge schema."""

    label: str
    participants: List[str]


def export_graph(folder, nodes, edges, **kwargs):
    return export_to_obsidian(
        nodes,
        edges,
        node_id_extractor=lambda n: n.name,
        incident_nodes_extractor=lambda e: (e.source, e.target),
        folder_path=folder,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------


class TestSanitizeFilename:
    def test_keeps_plain_names(self):
        assert sanitize_filename("Steve Jobs") == "Steve Jobs"

    def test_replaces_illegal_chars(self):
        result = sanitize_filename('A/B:C*?"<>|[]#^')
        for bad in '\\/:*?"<>|[]#^':
            assert bad not in result

    def test_collapses_whitespace(self):
        assert sanitize_filename("a   b\tc") == "a b c"

    def test_empty_uses_fallback(self):
        assert sanitize_filename("///", fallback="x") == "x"
        assert sanitize_filename("", fallback="x") == "x"

    def test_strips_trailing_dots(self):
        assert sanitize_filename("name...") == "name"

    def test_truncates_long_names(self):
        assert len(sanitize_filename("z" * 500)) <= 120


# ---------------------------------------------------------------------------
# Front-matter rendering
# ---------------------------------------------------------------------------


class TestFrontmatter:
    def test_has_fences(self):
        out = _render_frontmatter({"name": "Apple"})
        assert out.startswith("---\n")
        assert out.endswith("\n---")

    def test_yaml_roundtrip_preserves_structure(self):
        yaml = pytest.importorskip("yaml")
        data = {
            "name": "Apple: the fruit",  # colon -> must be quoted
            "count": 3,
            "ratio": 1.5,
            "active": True,
            "missing": None,
            "tags": ["a", "b c", "needs: quote"],
            "nested": {"founded": 1976, "ceo": "Tim Cook"},
            "mixed": [{"k": 1}, "v"],
            "unicode": "苹果",
        }
        rendered = _render_frontmatter(data)
        body = rendered.strip().strip("-").strip()
        loaded = yaml.safe_load(body)
        assert loaded == data

    def test_reserved_words_quoted(self):
        yaml = pytest.importorskip("yaml")
        data = {"a": "yes", "b": "null", "c": "true"}
        loaded = yaml.safe_load(_render_frontmatter(data).strip().strip("-").strip())
        # Without quoting these would parse as bool/None instead of strings.
        assert loaded == data


# ---------------------------------------------------------------------------
# export_to_obsidian — structure
# ---------------------------------------------------------------------------


class TestExportStructure:
    def test_creates_note_per_node_plus_index(self, tmp_path):
        nodes = [
            Entity(name="Apple", type="ORG"),
            Entity(name="Steve Jobs", type="PERSON"),
        ]
        edges = [
            Relation(source="Apple", target="Steve Jobs", relation_type="founded_by")
        ]

        export_graph(tmp_path / "vault", nodes, edges, vault_name="TestVault")

        vault = tmp_path / "vault"
        assert (vault / "Apple.md").exists()
        assert (vault / "Steve Jobs.md").exists()
        assert (vault / "TestVault.md").exists()  # index
        assert len(list(vault.glob("*.md"))) == 3

    def test_note_has_frontmatter_and_heading(self, tmp_path):
        export_graph(tmp_path / "v", [Entity(name="Apple", type="ORG")], [])
        content = (tmp_path / "v" / "Apple.md").read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "name: Apple" in content
        assert "type: ORG" in content
        assert "# Apple" in content

    def test_description_rendered_in_body(self, tmp_path):
        node = Entity(name="Apple", description="A tech company.")
        export_graph(tmp_path / "v", [node], [])
        content = (tmp_path / "v" / "Apple.md").read_text(encoding="utf-8")
        assert "A tech company." in content

    def test_no_index_when_disabled(self, tmp_path):
        export_graph(
            tmp_path / "v",
            [Entity(name="Apple")],
            [],
            vault_name="TestVault",
            include_index=False,
        )
        assert not (tmp_path / "v" / "TestVault.md").exists()
        assert (tmp_path / "v" / "Apple.md").exists()


# ---------------------------------------------------------------------------
# export_to_obsidian — edges / wikilinks
# ---------------------------------------------------------------------------


class TestExportEdges:
    def test_edge_renders_wikilink_under_source(self, tmp_path):
        nodes = [Entity(name="Apple"), Entity(name="Steve Jobs")]
        edges = [
            Relation(
                source="Apple",
                target="Steve Jobs",
                relation_type="founded_by",
                description="in 1976",
            )
        ]
        export_graph(tmp_path / "v", nodes, edges)

        source = (tmp_path / "v" / "Apple.md").read_text(encoding="utf-8")
        assert "## Relationships" in source
        assert "[[Steve Jobs]]" in source
        assert "founded_by" in source
        assert "in 1976" in source

    def test_unknown_endpoints_are_skipped(self, tmp_path):
        nodes = [Entity(name="Apple")]
        edges = [Relation(source="Apple", target="Ghost", relation_type="x")]
        # Should not raise; Apple note has no resolvable relationship target.
        export_graph(tmp_path / "v", nodes, edges)
        source = (tmp_path / "v" / "Apple.md").read_text(encoding="utf-8")
        assert "[[Ghost]]" not in source

    def test_custom_edge_label_extractor(self, tmp_path):
        nodes = [Entity(name="A"), Entity(name="B")]
        edges = [Relation(source="A", target="B", relation_type="r")]
        export_to_obsidian(
            nodes,
            edges,
            node_id_extractor=lambda n: n.name,
            incident_nodes_extractor=lambda e: (e.source, e.target),
            folder_path=tmp_path / "v",
            edge_label_extractor=lambda e: "LINKS-TO",
        )
        assert "LINKS-TO" in (tmp_path / "v" / "A.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# export_to_obsidian — naming / aliases / collisions
# ---------------------------------------------------------------------------


class TestExportNaming:
    def test_illegal_chars_in_node_name(self, tmp_path):
        nodes = [Entity(name="A/B:C")]
        export_graph(tmp_path / "v", nodes, [])
        files = list((tmp_path / "v").glob("*.md"))
        node_files = [f for f in files if f.stem != "Knowledge Vault"]
        assert len(node_files) == 1
        for bad in '\\/:*?"<>|':
            assert bad not in node_files[0].name

    def test_label_extractor_adds_alias_for_id(self, tmp_path):
        nodes = [Entity(name="apple_inc")]
        export_to_obsidian(
            nodes,
            [],
            node_id_extractor=lambda n: n.name,
            incident_nodes_extractor=lambda e: (e.source, e.target),
            folder_path=tmp_path / "v",
            node_label_extractor=lambda n: "Apple Inc",
        )
        content = (tmp_path / "v" / "Apple Inc.md").read_text(encoding="utf-8")
        assert "aliases:" in content
        assert "apple_inc" in content

    def test_colliding_titles_get_unique_files(self, tmp_path):
        # Two distinct ids whose titles sanitize to the same stem.
        nodes = [Entity(name="A:B"), Entity(name="A/B")]
        export_graph(tmp_path / "v", nodes, [], include_index=False)
        node_files = sorted(f.name for f in (tmp_path / "v").glob("*.md"))
        assert len(node_files) == 2
        assert node_files[0] != node_files[1]

    def test_wikilink_uses_sanitized_stem(self, tmp_path):
        nodes = [Entity(name="Apple"), Entity(name="Steve/Jobs")]
        edges = [Relation(source="Apple", target="Steve/Jobs", relation_type="x")]
        export_graph(tmp_path / "v", nodes, edges)
        source = (tmp_path / "v" / "Apple.md").read_text(encoding="utf-8")
        # Link target is the sanitized stem; display keeps original via alias pipe.
        assert "[[Steve Jobs|Steve/Jobs]]" in source


# ---------------------------------------------------------------------------
# export_to_obsidian — overwrite guard
# ---------------------------------------------------------------------------


class TestOverwriteGuard:
    def test_raises_on_nonempty_dir(self, tmp_path):
        dest = tmp_path / "v"
        dest.mkdir()
        (dest / "existing.md").write_text("keep me", encoding="utf-8")
        with pytest.raises(FileExistsError):
            export_graph(dest, [Entity(name="Apple")], [])

    def test_overwrite_allows_nonempty_dir(self, tmp_path):
        dest = tmp_path / "v"
        dest.mkdir()
        (dest / "existing.md").write_text("keep me", encoding="utf-8")
        export_graph(dest, [Entity(name="Apple")], [], overwrite=True)
        assert (dest / "Apple.md").exists()


# ---------------------------------------------------------------------------
# export_to_obsidian — hypergraph (N-ary edges)
# ---------------------------------------------------------------------------


class TestHypergraphExport:
    def test_nary_edge_links_all_members(self, tmp_path):
        nodes = [Entity(name="A"), Entity(name="B"), Entity(name="C")]
        edges = [Event(label="meeting", participants=["A", "B", "C"])]
        export_to_obsidian(
            nodes,
            edges,
            node_id_extractor=lambda n: n.name,
            incident_nodes_extractor=lambda e: tuple(e.participants),
            edge_label_extractor=lambda e: e.label,
            folder_path=tmp_path / "v",
        )
        # First member is the source; remaining are linked targets.
        source = (tmp_path / "v" / "A.md").read_text(encoding="utf-8")
        assert "meeting" in source
        assert "[[B]]" in source
        assert "[[C]]" in source
