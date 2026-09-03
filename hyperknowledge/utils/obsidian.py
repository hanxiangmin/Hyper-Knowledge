"""Obsidian vault exporter.

Converts an extracted Knowledge Abstract into an `Obsidian
<https://obsidian.md>`_ vault: a folder of Markdown notes where each node
becomes a note and each edge becomes an internal ``[[wikilink]]``. Opening the
resulting folder as a vault in Obsidian renders the extracted knowledge in its
interactive graph view, fully browsable and editable.

The core :func:`export_to_obsidian` function is decoupled from the AutoType
classes (mirroring how :mod:`ontosight` powers ``AutoGraph.show``). It works on
plain lists of Pydantic node/edge models plus a few extractor callables, so it
supports the entire graph family (``AutoGraph`` and its temporal/spatial
subclasses) as well as ``AutoHypergraph`` (N-ary edges).

Only the Python standard library is used; no extra dependency is introduced.
"""

import json
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hyperknowledge.utils.logging import get_logger

logger = get_logger(__name__)


# Characters Obsidian/most filesystems disallow (or treat specially) in note
# file names. ``[`` / ``]`` / ``#`` / ``^`` / ``|`` break wikilink parsing.
_ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\[\]#^]')
_WHITESPACE = re.compile(r"\s+")

# Conservative "safe to emit unquoted" YAML plain-scalar charset.
_SAFE_PLAIN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9 _./()\-]*$")
_NUMERIC = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
_YAML_RESERVED = {"", "~", "true", "false", "yes", "no", "on", "off", "null", "none"}

# Field names checked (in order) when guessing a node title / type, or an edge
# label / description, for models with arbitrary schemas.
_TITLE_FIELDS = ("name", "title", "label", "term", "id")
_TYPE_FIELDS = ("type", "category", "kind", "group", "label")
_EDGE_LABEL_FIELDS = ("relation_type", "type", "label", "name", "relation", "predicate")
_DESCRIPTION_FIELDS = ("description", "desc", "summary", "detail", "details", "note")


# ----------------------------------------------------------------------------
# YAML front-matter emission (minimal, dependency-free)
# ----------------------------------------------------------------------------


def _needs_quote(text: str) -> bool:
    """Return True if a string must be quoted to be a valid YAML plain scalar."""
    if text.strip() != text:  # leading/trailing whitespace
        return True
    if text.lower() in _YAML_RESERVED:
        return True
    if _NUMERIC.match(text):
        return True
    return not _SAFE_PLAIN.match(text)


def _yaml_scalar(value: Any) -> str:
    """Serialize a scalar value to a YAML representation."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    text = str(value)
    if _needs_quote(text):
        # A JSON-encoded string is also a valid YAML double-quoted scalar and
        # handles all escaping (quotes, newlines, unicode) for us.
        return json.dumps(text, ensure_ascii=False)
    return text


def _is_scalar(value: Any) -> bool:
    return not isinstance(value, (dict, list, tuple))


def _emit_kv(key: str, value: Any, indent: int) -> list[str]:
    """Emit ``key: value`` as YAML block-style lines."""
    pad = "  " * indent
    key_str = _yaml_scalar(key)

    if isinstance(value, dict):
        if not value:
            return [f"{pad}{key_str}: {{}}"]
        lines = [f"{pad}{key_str}:"]
        for sub_key, sub_value in value.items():
            lines.extend(_emit_kv(str(sub_key), sub_value, indent + 1))
        return lines

    if isinstance(value, (list, tuple)):
        if not value:
            return [f"{pad}{key_str}: []"]
        if all(_is_scalar(item) for item in value):
            lines = [f"{pad}{key_str}:"]
            item_pad = "  " * (indent + 1)
            lines.extend(f"{item_pad}- {_yaml_scalar(item)}" for item in value)
            return lines
        # Mixed/nested list: fall back to a JSON flow sequence (valid YAML).
        return [
            f"{pad}{key_str}: {json.dumps(list(value), ensure_ascii=False, default=str)}"
        ]

    return [f"{pad}{key_str}: {_yaml_scalar(value)}"]


def _render_frontmatter(mapping: dict[str, Any]) -> str:
    """Render a mapping as a YAML front-matter block (with ``---`` fences)."""
    lines = ["---"]
    for key, value in mapping.items():
        lines.extend(_emit_kv(str(key), value, 0))
    lines.append("---")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Field / filename helpers
# ----------------------------------------------------------------------------


def _first_field(model: BaseModel, candidates: Sequence[str]) -> str | None:
    """Return the first present, non-empty candidate field as a string."""
    model_fields = type(model).model_fields
    for field in candidates:
        if field in model_fields:
            value = getattr(model, field, None)
            if value not in (None, "", [], {}):
                return str(value)
    return None


def _safe_call(func: Callable | None, arg: Any) -> str | None:
    """Call ``func(arg)`` defensively, returning a string or None."""
    if func is None:
        return None
    try:
        result = func(arg)
    except Exception as exc:
        logger.debug("obsidian: extractor raised %s", exc)
        return None
    if result in (None, ""):
        return None
    return str(result)


def sanitize_filename(name: str, fallback: str = "untitled") -> str:
    """Turn an arbitrary title into an Obsidian-safe note filename stem."""
    cleaned = _ILLEGAL_FILENAME_CHARS.sub(" ", str(name))
    cleaned = _WHITESPACE.sub(" ", cleaned).strip()
    cleaned = cleaned.strip(".")  # trailing dots are problematic on Windows
    if not cleaned:
        return fallback
    # Keep note names reasonable for the filesystem.
    return cleaned[:120].strip()


def _wikilink(stem: str, display: str | None = None) -> str:
    """Build an Obsidian wikilink targeting ``stem`` with optional display text."""
    if display and display != stem:
        return f"[[{stem}|{display}]]"
    return f"[[{stem}]]"


# ----------------------------------------------------------------------------
# Internal node bookkeeping
# ----------------------------------------------------------------------------


class _NoteEntry:
    """Resolved metadata for a single node note."""

    __slots__ = ("model", "node_id", "stem", "title")

    def __init__(self, node_id: str, title: str, stem: str, model: BaseModel):
        self.node_id = node_id
        self.title = title
        self.stem = stem
        self.model = model


def _resolve_notes(
    nodes: Sequence[BaseModel],
    node_id_extractor: Callable[[Any], str],
    node_label_extractor: Callable[[Any], str] | None,
    reserved_stems: set,
) -> tuple[list[_NoteEntry], dict[str, _NoteEntry]]:
    """Resolve titles and unique, collision-free filename stems for all nodes."""
    used_stems = set(reserved_stems)
    entries: list[_NoteEntry] = []
    by_id: dict[str, _NoteEntry] = {}

    for index, node in enumerate(nodes):
        try:
            node_id = str(node_id_extractor(node))
        except Exception as exc:
            logger.debug("obsidian: node_id_extractor raised %s; skipping node", exc)
            continue

        if node_id in by_id:
            # Defensive: ids should already be deduplicated upstream.
            logger.debug("obsidian: duplicate node id %r; keeping first", node_id)
            continue

        title = (
            _safe_call(node_label_extractor, node)
            or _first_field(node, _TITLE_FIELDS)
            or node_id
        )

        base_stem = sanitize_filename(title, fallback=f"node-{index}")
        stem = base_stem
        suffix = 2
        while stem.lower() in used_stems:
            stem = f"{base_stem} ({suffix})"
            suffix += 1
        used_stems.add(stem.lower())

        entry = _NoteEntry(node_id=node_id, title=title, stem=stem, model=node)
        entries.append(entry)
        by_id[node_id] = entry

    return entries, by_id


def _incident_ids(
    edge: Any, incident_nodes_extractor: Callable[[Any], Sequence[str]]
) -> list[str]:
    """Normalize an edge's incident node keys to a list of strings."""
    try:
        raw = incident_nodes_extractor(edge)
    except Exception as exc:
        logger.debug("obsidian: incident_nodes_extractor raised %s; skipping edge", exc)
        return []
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)):
        return [str(raw)]
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if item is not None]
    return [str(raw)]


def _build_relationships(
    edges: Sequence[BaseModel],
    incident_nodes_extractor: Callable[[Any], Sequence[str]],
    edge_label_extractor: Callable[[Any], str] | None,
    by_id: dict[str, _NoteEntry],
) -> tuple[dict[str, list[str]], int]:
    """Group edges into per-source-note relationship lines.

    Returns a mapping ``{source_node_id: [markdown bullet, ...]}`` and the count
    of edges that were skipped because no incident node was known.
    """
    relationships: dict[str, list[str]] = {}
    skipped = 0

    for edge in edges:
        members = [
            nid for nid in _incident_ids(edge, incident_nodes_extractor) if nid in by_id
        ]
        if not members:
            skipped += 1
            continue

        source_id = members[0]
        target_ids = members[1:]

        label = (
            _safe_call(edge_label_extractor, edge)
            or _first_field(edge, _EDGE_LABEL_FIELDS)
            or "related to"
        )
        description = _first_field(edge, _DESCRIPTION_FIELDS)

        if target_ids:
            targets = ", ".join(
                _wikilink(by_id[tid].stem, by_id[tid].title) for tid in target_ids
            )
            line = f"- **{label}** → {targets}"
        else:
            # Self-contained edge (e.g. a single-member hyperedge): note it.
            line = f"- **{label}** (self)"

        if description:
            line += f" — {description}"

        relationships.setdefault(source_id, []).append(line)

    return relationships, skipped


# ----------------------------------------------------------------------------
# Note rendering
# ----------------------------------------------------------------------------


def _build_frontmatter(entry: _NoteEntry) -> dict[str, Any]:
    """Build the YAML front-matter mapping for a node note."""
    data: dict[str, Any] = dict(entry.model.model_dump())

    # Ensure the original id / title remain resolvable as aliases, so wikilinks
    # written against either still point at this note.
    extra_aliases = [
        value for value in (entry.node_id, entry.title) if value and value != entry.stem
    ]
    if extra_aliases:
        existing = data.get("aliases")
        if isinstance(existing, list):
            merged = list(existing)
        elif existing:
            merged = [existing]
        else:
            merged = []
        for alias in extra_aliases:
            if alias not in merged:
                merged.append(alias)
        data["aliases"] = merged

    return data


def _render_note(entry: _NoteEntry, relationship_lines: list[str]) -> str:
    """Render a single node note's full Markdown content."""
    parts = [_render_frontmatter(_build_frontmatter(entry)), "", f"# {entry.title}", ""]

    description = _first_field(entry.model, _DESCRIPTION_FIELDS)
    if description:
        parts.extend([description, ""])

    if relationship_lines:
        parts.append("## Relationships")
        parts.append("")
        parts.extend(relationship_lines)
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def _render_index(entries: list[_NoteEntry], vault_name: str, edge_count: int) -> str:
    """Render the vault index / map-of-content note."""
    parts = [
        _render_frontmatter({"tags": ["index"], "title": vault_name}),
        "",
        f"# {vault_name}",
        "",
        f"> {len(entries)} notes · {edge_count} relationships",
        "",
    ]

    # Group notes by a guessed "type" field for a tidy table of contents.
    groups: dict[str, list[_NoteEntry]] = {}
    for entry in entries:
        group = _first_field(entry.model, _TYPE_FIELDS) or "Notes"
        groups.setdefault(group, []).append(entry)

    for group in sorted(groups):
        parts.append(f"## {group}")
        parts.append("")
        for entry in sorted(groups[group], key=lambda e: e.title.lower()):
            parts.append(f"- {_wikilink(entry.stem, entry.title)}")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------


def export_to_obsidian(
    nodes: Sequence[BaseModel],
    edges: Sequence[BaseModel],
    *,
    node_id_extractor: Callable[[Any], str],
    incident_nodes_extractor: Callable[[Any], Sequence[str]],
    folder_path: str | Path,
    node_label_extractor: Callable[[Any], str] | None = None,
    edge_label_extractor: Callable[[Any], str] | None = None,
    vault_name: str = "Knowledge Vault",
    include_index: bool = True,
    overwrite: bool = False,
) -> Path:
    """Export graph-structured knowledge to an Obsidian vault.

    Each node is written as a Markdown note whose YAML front-matter holds the
    node's fields; each edge is rendered under its source note as a
    ``[[wikilink]]`` to the target note(s). For N-ary (hyper)edges the first
    incident node is treated as the source and the rest as targets.

    Args:
        nodes: Node/entity models to export.
        edges: Edge/relationship models to export.
        node_id_extractor: Maps a node to its unique key (matches edge endpoints).
        incident_nodes_extractor: Maps an edge to the node keys it connects
            (a 2-tuple for pairwise graphs, an N-tuple for hypergraphs).
        folder_path: Destination vault directory.
        node_label_extractor: Optional node -> display title. Falls back to common
            fields (name/title/...) then the node id.
        edge_label_extractor: Optional edge -> relationship label. Falls back to
            common fields (relation_type/type/...) then "related to".
        vault_name: Title used for the generated index note.
        include_index: Whether to write an index/map-of-content note.
        overwrite: Allow writing into an existing, non-empty directory.

    Returns:
        The vault directory :class:`~pathlib.Path`.

    Raises:
        FileExistsError: If ``folder_path`` exists, is non-empty and ``overwrite``
            is False.
    """
    root = Path(folder_path)
    if root.exists() and root.is_dir() and any(root.iterdir()) and not overwrite:
        raise FileExistsError(
            f"Destination '{root}' already exists and is not empty. "
            f"Pass overwrite=True to write into it."
        )
    root.mkdir(parents=True, exist_ok=True)

    reserved_stems: set = set()
    index_stem = None
    if include_index:
        index_stem = sanitize_filename(vault_name, fallback="Index")
        reserved_stems.add(index_stem.lower())

    entries, by_id = _resolve_notes(
        nodes, node_id_extractor, node_label_extractor, reserved_stems
    )
    relationships, skipped_edges = _build_relationships(
        edges, incident_nodes_extractor, edge_label_extractor, by_id
    )

    for entry in entries:
        content = _render_note(entry, relationships.get(entry.node_id, []))
        (root / f"{entry.stem}.md").write_text(content, encoding="utf-8")

    if include_index and index_stem is not None:
        index_content = _render_index(entries, vault_name, len(edges))
        (root / f"{index_stem}.md").write_text(index_content, encoding="utf-8")

    logger.info(
        "obsidian: exported vault notes=%d edges=%d skipped_edges=%d path=%s",
        len(entries),
        len(edges),
        skipped_edges,
        root,
    )
    return root
