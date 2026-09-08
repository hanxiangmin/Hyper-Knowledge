"""Small, file-oriented API shared by notebooks, scripts, and Agent Skills."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import uuid
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from hyperknowledge.bundle import (
    BUNDLE_SCHEMA_VERSION,
    BundleExportError,
    _json_bytes,
    _stable_id,
    _write_bundle_tables,
    export_bundle,
    read_bundle,
    validate_bundle,
)
from hyperknowledge.utils.template_engine import Template


@dataclass(frozen=True)
class GraphResult:
    """Paths and structural counts, not a model confidence score."""

    ka_path: Path | None
    bundle_path: Path
    node_count: int
    hyperedge_count: int
    pairwise_count: int
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable receipt."""
        return {
            "ka_path": str(self.ka_path) if self.ka_path else None,
            "bundle_path": str(self.bundle_path),
            "node_count": self.node_count,
            "hyperedge_count": self.hyperedge_count,
            "pairwise_count": self.pairwise_count,
            "warnings": list(self.warnings),
        }


@contextmanager
def _staged_output(output_dir: str | Path, *, force: bool):
    """Validate first, publish last; keep an existing output as a sibling backup."""
    target = Path(output_dir).expanduser().resolve()
    if (
        target in {Path(target.anchor), Path.home().resolve(), Path.cwd().resolve()}
        or (target / ".git").exists()
    ):
        raise ValueError(
            "Choose a dedicated output directory, not a home, drive, repository, or working directory."
        )
    if target.exists() and not target.is_dir():
        raise FileExistsError(f"Output is not a directory: {target}")
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(
            f"Output directory is not empty: {target}; choose a new directory or pass force=True."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{target.name}-staging-", dir=target.parent
    ) as temporary:
        stage = Path(temporary) / "result"
        stage.mkdir()
        yield stage
        backup = None
        if target.exists():
            backup = target.with_name(f"{target.name}.backup-{uuid.uuid4().hex[:12]}")
            target.replace(backup)
        try:
            stage.replace(target)
        except OSError:
            if backup is not None and not target.exists():
                backup.replace(target)
            raise


def _assert_valid(bundle: Path, quality: str) -> dict[str, Any]:
    receipt = validate_bundle(bundle, quality=quality)
    if receipt["status"] != "passed":
        errors = [
            f"{d['code']}: {d['subject']} ({d['evidence']})"
            for d in receipt.get("diagnostics", [])
            if d["severity"] == "error"
        ]
        raise BundleExportError("Invalid graph: " + "; ".join(errors))
    return receipt


def _result(bundle: Path, ka: Path | None = None) -> GraphResult:
    data = read_bundle(bundle)
    receipt = _assert_valid(bundle, "standard")
    warnings = tuple(
        dict.fromkeys(
            [
                *data["manifest"].get("limitations", []),
                *(
                    f"{d['code']}: {d['subject']}"
                    for d in receipt.get("diagnostics", [])
                    if d["severity"] == "warning"
                ),
            ]
        )
    )
    return GraphResult(
        ka,
        bundle,
        len(data["nodes"]),
        sum(row["topology"] == "hyperedge" for row in data["assertions"]),
        sum(row["topology"] == "pairwise" for row in data["assertions"]),
        warnings,
    )


def _source_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip() or "\\" in name or ":" in name:
        raise ValueError("Source names must be nonempty relative POSIX paths.")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or str(path) == ".":
        raise ValueError(f"Unsafe source name: {name!r}")
    return path.as_posix()


def _copy_sources(
    stage: Path, source_bytes: Mapping[str, bytes]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    records, names = [], {}
    for name, content in source_bytes.items():
        relative = f"sources/{_source_name(name)}"
        if relative.casefold() in {value.casefold() for value in names.values()}:
            raise ValueError(f"Duplicate source name: {name}")
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        names[name] = relative
        records.append(
            {
                "path": relative,
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return records, names


def import_graph(
    data: Mapping[str, Any] | str | Path,
    *,
    output_dir: str | Path,
    sources: Mapping[str, str | Path] | None = None,
    language: str = "zh",
    quality: str = "standard",
    force: bool = False,
) -> GraphResult:
    """Import Bundle-v1 tables without a model or index.

    ``data`` is a mapping or a UTF-8 JSON file containing ``nodes``,
    ``assertions``, ``members`` and optional ``evidence`` arrays. Member
    ordinals and resolved flags, counts, and hashes are computed locally.
    ``sources`` maps logical evidence source names to explicitly allowed files;
    those files are copied into the bundle. Paths embedded in JSON are never read.
    Invalid input is rejected before replacing any existing output.
    """
    if quality not in {"standard", "showcase"}:
        raise ValueError("quality must be 'standard' or 'showcase'")
    if isinstance(data, (str, Path)):
        data = json.loads(Path(data).read_text(encoding="utf-8-sig"))
    if not isinstance(data, Mapping):
        raise ValueError(
            "Graph input must be an object with nodes, assertions, members and evidence tables."
        )
    if set(data) - {"schema_version", "nodes", "assertions", "members", "evidence"}:
        raise ValueError(
            "Unexpected graph fields; pass source files through sources=, not paths embedded in JSON."
        )
    if data.get("schema_version", BUNDLE_SCHEMA_VERSION) != BUNDLE_SCHEMA_VERSION:
        raise ValueError(f"Expected schema_version={BUNDLE_SCHEMA_VERSION}")
    tables = {}
    for name in ("nodes", "assertions", "members", "evidence"):
        rows = data.get(name, [] if name == "evidence" else None)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError(f"{name} must be an array of objects")
        tables[name] = json.loads(json.dumps(rows, ensure_ascii=False, allow_nan=False))
    for node in tables["nodes"]:
        for key in ("id", "label", "type"):
            if not isinstance(node.get(key), str) or not node[key].strip():
                raise ValueError(f"Each node needs a nonempty {key}")
        node.setdefault("properties", {})
    node_ids = {node["id"] for node in tables["nodes"]}
    for assertion in tables["assertions"]:
        for key in ("id", "predicate"):
            if not isinstance(assertion.get(key), str) or not assertion[key].strip():
                raise ValueError(f"Each assertion needs a nonempty {key}")
        assertion.setdefault("topology", "hyperedge")
        assertion.setdefault("semantics", "structured_import")
        assertion.setdefault("epistemic_status", "unreviewed_import")
        assertion.setdefault("evidence_refs", [])
        assertion.setdefault("properties", {})
    for row in [*tables["nodes"], *tables["assertions"]]:
        if not isinstance(row["properties"], dict):
            raise ValueError("properties must be an object")
    next_ordinal: dict[str, int] = {}
    for member in tables["members"]:
        for key in ("assertion_id", "node_id", "role"):
            if not isinstance(member.get(key), str) or not member[key].strip():
                raise ValueError(f"Each member needs a nonempty {key}")
        assertion_id = member["assertion_id"]
        member.setdefault("ordinal", next_ordinal.get(assertion_id, 0))
        ordinal = member["ordinal"]
        if type(ordinal) is not int or ordinal < 0:
            raise ValueError("Member ordinal must be a nonnegative integer")
        next_ordinal[assertion_id] = max(next_ordinal.get(assertion_id, 0), ordinal + 1)
        member["resolved"] = member["node_id"] in node_ids
    source_bytes = {}
    for name, path in (sources or {}).items():
        normalized = _source_name(name)
        if normalized.casefold() in {value.casefold() for value in source_bytes}:
            raise ValueError(f"Duplicate source name: {name}")
        source_bytes[normalized] = Path(path).read_bytes()
    destination = Path(output_dir).expanduser().resolve()
    with _staged_output(destination, force=force) as stage:
        records, names = _copy_sources(stage, source_bytes)
        for item in tables["evidence"]:
            if item.get("type") in {"source_text_span", "source_text_summary"}:
                source = item.get("source")
                if not isinstance(source, str) or source not in names:
                    raise ValueError(
                        f"Evidence source {source!r} needs an explicit sources= mapping (CLI: --source NAME=PATH)."
                    )
                item["source"] = names[source]
        limitations = []
        if any(not row["evidence_refs"] for row in tables["assertions"]):
            limitations.append(
                "Some assertions lack source-level evidence; missing evidence is not inferred during import."
            )
        manifest = {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "bundle_id": _stable_id("bundle", {"tables": tables, "sources": records}),
            "source_data_sha256": hashlib.sha256(_json_bytes(data)).hexdigest(),
            "source_ka": None,
            "template": "structured/import",
            "language": language,
            "topology_type": "hypergraph"
            if any(row["topology"] == "hyperedge" for row in tables["assertions"])
            else "graph",
            "sources": records,
            "limitations": limitations,
        }
        _write_bundle_tables(stage, manifest, tables)
        _assert_valid(stage, quality)
    return _result(destination)


def _extract(
    text: str,
    source_name: str,
    raw: bytes,
    *,
    output_dir: str | Path,
    template: str,
    language: str,
    llm_client: Any,
    embedder: Any,
    build_index: bool,
    force: bool,
) -> GraphResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")
    source_name = _source_name(source_name)
    config = Template.get(template)
    if config is None or config.type not in {
        "graph",
        "hypergraph",
        "temporal_graph",
        "spatial_graph",
        "spatio_temporal_graph",
    }:
        raise ValueError("The extraction API requires a graph or hypergraph template")
    destination = Path(output_dir).expanduser().resolve()
    with _staged_output(destination, force=force) as stage:
        ka_path = stage / "ka"
        ka_path.mkdir()
        records, _ = _copy_sources(ka_path, {source_name: raw})
        ka = Template.create(
            template,
            language=language,
            llm_client=llm_client,
            embedder=embedder,
            defer_embeddings=True,
        )
        ka.feed_text(text)
        ka.metadata["sources"] = records
        if Path(template).is_file():
            # KA metadata uses the template's declared name on reload.
            shutil.copy2(template, ka_path / f"{config.name}.yaml")
        if build_index:
            ka.build_index()
        if build_index:
            ka.dump(ka_path)
        else:
            ka.dump_data(ka_path / "data.json")
            ka.dump_metadata(ka_path / "metadata.json")
        export_bundle(ka_path, stage / "bundle")
        _assert_valid(stage / "bundle", "standard")
        manifest_path = stage / "bundle" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["source_ka"] = str(destination / "ka")
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return _result(destination / "bundle", destination / "ka")


def extract_text(
    text: str,
    *,
    output_dir: str | Path,
    template: str = "general/hypergraph",
    language: str = "zh",
    source_name: str = "input.txt",
    llm_client: Any = None,
    embedder: Any = None,
    build_index: bool = False,
    force: bool = False,
) -> GraphResult:
    """Extract a string through the existing template engine; save KA and Bundle.

    Model configuration is read only when ``llm_client`` is omitted. An embedder
    is resolved only when an operation uses it. Existing outputs are protected;
    ``force=True`` retains the previous directory as a sibling backup.
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    return _extract(
        text,
        source_name,
        text.encode("utf-8"),
        output_dir=output_dir,
        template=template,
        language=language,
        llm_client=llm_client,
        embedder=embedder,
        build_index=build_index,
        force=force,
    )


def extract_file(
    path: str | Path,
    *,
    output_dir: str | Path,
    template: str = "general/hypergraph",
    language: str = "zh",
    llm_client: Any = None,
    embedder: Any = None,
    build_index: bool = False,
    force: bool = False,
) -> GraphResult:
    """Extract one UTF-8 .txt/.md file; retain its exact bytes and source hash."""
    source = Path(path).expanduser().resolve()
    if source.suffix.lower() not in {".txt", ".md"}:
        raise ValueError(
            "extract_file supports UTF-8 .txt and .md; convert other formats to text first."
        )
    if source.is_relative_to(Path(output_dir).expanduser().resolve()):
        raise ValueError("The source must be outside the output directory")
    raw = source.read_bytes()
    return _extract(
        raw.decode("utf-8-sig"),
        source.name,
        raw,
        output_dir=output_dir,
        template=template,
        language=language,
        llm_client=llm_client,
        embedder=embedder,
        build_index=build_index,
        force=force,
    )
