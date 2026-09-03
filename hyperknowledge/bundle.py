"""Export Knowledge Abstracts into a normalized, versioned bundle."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from hyperknowledge.utils.template_engine import Gallery, Template

BUNDLE_SCHEMA_VERSION = "hk.bundle/v1"
BUNDLE_VALIDATION_SCHEMA_VERSION = "hk.bundle-validation/v1"


class BundleExportError(ValueError):
    """Raised when a Knowledge Abstract cannot be normalized safely."""


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}_{hashlib.sha256(_json_bytes(value)).hexdigest()[:16]}"


def _value(item: dict[str, Any], expression: str | None) -> str:
    if not expression:
        return ""
    if "{" not in expression:
        value = item.get(expression)
        return "" if value is None else str(value)
    fields = re.findall(r"\{(\w+)\}", expression)
    replacements = {field: item.get(field, "") for field in fields}
    return expression.format(**replacements)


def _resolve_template(ka_path: Path, metadata: dict[str, Any]):
    template_name = metadata.get("template")
    if not template_name:
        return None
    config = Gallery.get(str(template_name))
    if config is not None:
        return config
    local = ka_path / f"{template_name}.yaml"
    return Template.get(str(local)) if local.is_file() else None


def _member_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(member) for member in value if member is not None]


def _members(
    relation: dict[str, Any], relation_members: Any
) -> list[tuple[str, str, str | None]]:
    members: list[tuple[str, str, str | None]] = []
    if isinstance(relation_members, dict):
        if relation_members.get("source") and relation_members.get("target"):
            endpoint_ids = sorted(
                (
                    str(relation.get(relation_members["source"], "")),
                    str(relation.get(relation_members["target"], "")),
                )
            )
            return [("endpoint", node_id, None) for node_id in endpoint_ids]
        for role, field_name in relation_members.items():
            value = relation.get(field_name)
            if value is not None:
                members.append((str(role), str(value), None))
        return members
    if isinstance(relation_members, str):
        return [
            ("member", member, None)
            for member in _member_values(relation.get(relation_members, []))
        ]
    if isinstance(relation_members, list):
        for role in relation_members:
            members.extend(
                (str(role), member, None)
                for member in _member_values(relation.get(role, []))
            )
        return members

    if "source" in relation and "target" in relation:
        return [
            ("endpoint", node_id, None)
            for node_id in sorted((str(relation["source"]), str(relation["target"])))
        ]
    values = relation.get("participants", [])
    return [("member", str(member), None) for member in values]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n"
        for row in rows
    )
    path.write_text(text, encoding="utf-8")


def export_bundle(
    ka_path: str | Path, output_path: str | Path, *, force: bool = False
) -> dict[str, Any]:
    """Normalize a KA without loading its LLM client or vector index."""
    ka = Path(ka_path).resolve()
    data_path = ka / "data.json"
    metadata_path = ka / "metadata.json"
    if not data_path.is_file():
        raise BundleExportError(f"Not a Knowledge Abstract: {ka}")

    data = json.loads(data_path.read_text(encoding="utf-8"))
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.is_file()
        else {}
    )
    if not isinstance(data, dict):
        raise BundleExportError(
            "Graph and hypergraph bundles require object-shaped data"
        )

    destination = Path(output_path).resolve()
    if destination.exists() and any(destination.iterdir()) and not force:
        raise BundleExportError(
            f"Output directory is not empty: {destination}; pass force=True to replace files"
        )
    destination.mkdir(parents=True, exist_ok=True)

    config = _resolve_template(ka, metadata)
    identifiers = getattr(config, "identifiers", None)
    display = getattr(config, "display", None)
    topology_type = str(metadata.get("type") or getattr(config, "type", "graph"))
    if topology_type not in {
        "graph",
        "hypergraph",
        "temporal_graph",
        "spatial_graph",
        "spatio_temporal_graph",
    }:
        raise BundleExportError(
            f"Unsupported graph topology: {topology_type}; use graph or hypergraph"
        )
    relation_members = getattr(identifiers, "relation_members", None)
    entity_id_expression = getattr(identifiers, "entity_id", None)
    relation_id_expression = getattr(identifiers, "relation_id", None)
    entity_label_expression = getattr(display, "entity_label", None)

    raw_nodes = data.get("nodes", data.get("entities", [])) or []
    raw_relations = data.get("edges", data.get("relations", [])) or []
    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for raw in raw_nodes:
        item = raw if isinstance(raw, dict) else {"value": raw}
        node_id = _value(item, entity_id_expression) or str(
            item.get("id") or item.get("name") or _stable_id("node", item)
        )
        label = _value(item, entity_label_expression) or str(
            item.get("label") or item.get("name") or node_id
        )
        node_ids.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "type": str(item.get("type", "entity")),
                "properties": item,
            }
        )

    assertions: list[dict[str, Any]] = []
    members: list[dict[str, Any]] = []
    unresolved = 0
    for raw in raw_relations:
        relation = raw if isinstance(raw, dict) else {"value": raw}
        assertion_id = _value(relation, relation_id_expression) or str(
            relation.get("id")
            or relation.get("name")
            or _stable_id("assertion", relation)
        )
        member_values = _members(relation, relation_members)
        topology = (
            "hyperedge"
            if topology_type == "hypergraph" or len(member_values) > 2
            else "pairwise"
        )
        predicate = str(
            relation.get("predicate")
            or relation.get("relation_type")
            or relation.get("type")
            or relation.get("name")
            or "related_to"
        )
        assertions.append(
            {
                "id": assertion_id,
                "predicate": predicate,
                "topology": topology,
                "semantics": "explicit_extraction",
                "epistemic_status": "model_extracted",
                "evidence_refs": [],
                "properties": relation,
            }
        )
        for ordinal, (role, node_id, side) in enumerate(member_values):
            resolved = node_id in node_ids
            unresolved += int(not resolved)
            member = {
                "assertion_id": assertion_id,
                "node_id": node_id,
                "role": role,
                "ordinal": ordinal,
                "resolved": resolved,
            }
            members.append(member)

    nodes.sort(key=lambda row: row["id"])
    assertions.sort(key=lambda row: row["id"])
    members.sort(key=lambda row: (row["assertion_id"], row["ordinal"]))
    sources = metadata.get("sources", [])
    bundle_id = _stable_id("bundle", {"data": data, "metadata": metadata})
    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "source_ka": str(ka),
        "source_data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "template": metadata.get("template"),
        "language": metadata.get("lang"),
        "topology_type": topology_type,
        "sources": sources,
        "counts": {
            "nodes": len(nodes),
            "assertions": len(assertions),
            "members": len(members),
            "unresolved_members": unresolved,
            "assertions_with_evidence": 0,
        },
        "limitations": [
            "This Knowledge Abstract does not contain assertion-level source spans; evidence_refs remain empty."
        ],
    }

    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_jsonl(destination / "nodes.jsonl", nodes)
    _write_jsonl(destination / "assertions.jsonl", assertions)
    _write_jsonl(destination / "members.jsonl", members)
    _write_jsonl(destination / "evidence.jsonl", [])
    report = (
        "# Hyper-Knowledge Bundle Report\n\n"
        f"- Bundle: `{bundle_id}`\n"
        f"- Nodes: {len(nodes)}\n"
        f"- Assertions: {len(assertions)}\n"
        f"- Members: {len(members)}\n"
        f"- Unresolved members: {unresolved}\n"
        "- Assertion-level evidence coverage: 0% because this Knowledge Abstract has no source spans\n\n"
        "Hyperedges are preserved through the members table and are not flattened into pairwise facts.\n"
    )
    (destination / "REPORT.md").write_text(report, encoding="utf-8")
    return manifest


def read_bundle(bundle_path: str | Path) -> dict[str, Any]:
    bundle = Path(bundle_path)

    def read_jsonl(name: str) -> list[dict[str, Any]]:
        path = bundle / name
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]

    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise BundleExportError(f"Bundle manifest not found: {bundle}")
    return {
        "manifest": json.loads(manifest_path.read_text(encoding="utf-8")),
        "nodes": read_jsonl("nodes.jsonl"),
        "assertions": read_jsonl("assertions.jsonl"),
        "members": read_jsonl("members.jsonl"),
        "evidence": read_jsonl("evidence.jsonl"),
    }


def validate_bundle(
    bundle_path: str | Path, *, quality: str = "standard"
) -> dict[str, Any]:
    """Validate topology, references, counts, and file identity for a bundle."""
    if quality not in {"standard", "showcase"}:
        raise BundleExportError("quality must be 'standard' or 'showcase'")
    bundle = Path(bundle_path).expanduser().resolve()
    required = [
        "manifest.json",
        "nodes.jsonl",
        "assertions.jsonl",
        "members.jsonl",
        "evidence.jsonl",
    ]
    checks: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    def check(
        code: str,
        passed: bool,
        subject: str,
        evidence: str,
        *,
        severity: str = "error",
        supported_fix: str | None = None,
    ) -> None:
        checks.append(
            {
                "code": code,
                "passed": passed,
                "subject": subject,
                "evidence": evidence,
            }
        )
        if not passed:
            diagnostic = {
                "code": code,
                "severity": severity,
                "subject": subject,
                "evidence": evidence,
            }
            if supported_fix:
                diagnostic["supported_fix"] = supported_fix
            diagnostics.append(diagnostic)

    for name in required:
        check(
            "bundle.required_file",
            (bundle / name).is_file(),
            name,
            "present" if (bundle / name).is_file() else "missing",
            supported_fix=f"Create {name} through hk bundle export",
        )
    if any(item["severity"] == "error" for item in diagnostics):
        return {
            "schema_version": BUNDLE_VALIDATION_SCHEMA_VERSION,
            "status": "failed",
            "quality": quality,
            "bundle": str(bundle),
            "checks": checks,
            "diagnostics": diagnostics,
        }

    data = read_bundle(bundle)
    manifest = data["manifest"]
    nodes = data["nodes"]
    assertions = data["assertions"]
    members = data["members"]
    evidence_items = data["evidence"]

    check(
        "bundle.schema",
        manifest.get("schema_version") == BUNDLE_SCHEMA_VERSION,
        "manifest.json",
        f"schema_version={manifest.get('schema_version')}",
        supported_fix=f"Export using {BUNDLE_SCHEMA_VERSION}",
    )

    def unique_ids(rows: list[dict[str, Any]], field: str) -> tuple[set[str], bool]:
        values = [str(row.get(field, "")) for row in rows]
        return set(values), bool(values) and "" not in values and len(
            set(values)
        ) == len(values)

    node_ids, nodes_unique = unique_ids(nodes, "id")
    assertion_ids, assertions_unique = unique_ids(assertions, "id")
    evidence_ids = {str(row.get("id")) for row in evidence_items if row.get("id")}
    check(
        "bundle.node_ids",
        nodes_unique,
        "nodes.jsonl",
        f"{len(node_ids)} unique ids across {len(nodes)} rows",
        supported_fix="Assign a non-empty unique id to every node",
    )
    check(
        "bundle.assertion_ids",
        assertions_unique,
        "assertions.jsonl",
        f"{len(assertion_ids)} unique ids across {len(assertions)} rows",
        supported_fix="Assign a non-empty unique id to every assertion",
    )

    member_counts: dict[str, int] = {}
    members_by_assertion: dict[str, list[dict[str, Any]]] = {}
    unresolved = 0
    for index, member in enumerate(members):
        assertion_id = str(member.get("assertion_id", ""))
        node_id = str(member.get("node_id", ""))
        member_counts[assertion_id] = member_counts.get(assertion_id, 0) + 1
        members_by_assertion.setdefault(assertion_id, []).append(member)
        assertion_found = assertion_id in assertion_ids
        node_found = node_id in node_ids
        unresolved += int(not node_found)
        check(
            "bundle.member_assertion_ref",
            assertion_found,
            f"members.jsonl:{index + 1}",
            f"assertion_id={assertion_id}",
            supported_fix="Reference an assertion id present in assertions.jsonl",
        )
        check(
            "bundle.member_node_ref",
            node_found,
            f"members.jsonl:{index + 1}",
            f"node_id={node_id}",
            severity="error" if quality == "showcase" else "warning",
            supported_fix="Add the node or correct the member reference",
        )
        check(
            "bundle.member_resolved_flag",
            bool(member.get("resolved")) == node_found,
            f"members.jsonl:{index + 1}",
            f"resolved={member.get('resolved')}, node_found={node_found}",
            supported_fix="Regenerate the resolved flag from the node table",
        )

    assertions_with_evidence = 0
    for assertion in assertions:
        assertion_id = str(assertion.get("id", ""))
        count = member_counts.get(assertion_id, 0)
        topology = assertion.get("topology")
        valid_count = count == 2 if topology == "pairwise" else count >= 2
        check(
            "bundle.topology_arity",
            topology in {"pairwise", "hyperedge"} and valid_count,
            assertion_id,
            f"topology={topology}, members={count}",
            supported_fix="Use two members for pairwise assertions and at least two for hyperedges",
        )
        refs = assertion.get("evidence_refs", []) or []
        assertions_with_evidence += int(bool(refs))
        check(
            "bundle.evidence_coverage",
            bool(refs),
            assertion_id,
            f"{len(refs)} evidence references",
            severity="warning",
            supported_fix="Link source-grounded evidence or disclose that it is unavailable",
        )
        for evidence_ref in refs:
            check(
                "bundle.evidence_ref",
                str(evidence_ref) in evidence_ids,
                assertion_id,
                f"evidence_ref={evidence_ref}",
                supported_fix="Add the referenced evidence item or remove the stale reference",
            )
        assertion_members = sorted(
            members_by_assertion.get(assertion_id, []),
            key=lambda item: int(item.get("ordinal", 0)),
        )
        roles = [str(member.get("role", "")) for member in assertion_members]
        check(
            "bundle.undirected_only",
            assertion.get("directed") is not True,
            assertion_id,
            f"directed={assertion.get('directed')}",
            supported_fix="Represent the relation as an undirected pairwise edge or hyperedge",
        )
        if topology == "hyperedge":
            check(
                "bundle.hyperedge_roles",
                all(roles),
                assertion_id,
                f"roles={roles}",
                supported_fix="Assign an explicit role to every hyperedge member",
            )
    expected_counts = manifest.get("counts", {})
    actual_counts = {
        "nodes": len(nodes),
        "assertions": len(assertions),
        "members": len(members),
        "unresolved_members": unresolved,
        "assertions_with_evidence": assertions_with_evidence,
    }
    for name, actual in actual_counts.items():
        check(
            "bundle.manifest_count",
            expected_counts.get(name) == actual,
            f"manifest.counts.{name}",
            f"declared={expected_counts.get(name)}, actual={actual}",
            supported_fix="Regenerate manifest counts from the normalized tables",
        )

    file_hashes = {
        name: hashlib.sha256((bundle / name).read_bytes()).hexdigest()
        for name in required
    }
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    return {
        "schema_version": BUNDLE_VALIDATION_SCHEMA_VERSION,
        "status": "passed" if errors == 0 else "failed",
        "quality": quality,
        "bundle": str(bundle),
        "bundle_id": manifest.get("bundle_id"),
        "summary": {
            "checks": len(checks),
            "errors": errors,
            "warnings": warnings,
            **actual_counts,
        },
        "file_sha256": file_hashes,
        "checks": checks,
        "diagnostics": diagnostics,
    }
