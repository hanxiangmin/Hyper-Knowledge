"""Self-contained graph and hypergraph demo generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hyperknowledge.visualization import render_bundle_html

DEMO_SCHEMA_VERSION = "hk.skill-demo/v1"


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _write_text(path: Path, content: str) -> None:
    candidate = path.with_suffix(path.suffix + ".candidate")
    candidate.write_text(content, encoding="utf-8")
    candidate.replace(path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_text(
        path,
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
        ),
    )


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_skill_demo(output_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    """Generate a deterministic synthetic bundle and an offline workbench view."""
    output = Path(output_dir).expanduser().resolve()
    if output.exists() and any(output.iterdir()) and not force:
        raise FileExistsError(f"Demo directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    bundle = output / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)

    nodes = [
        {
            "id": "bio:egfr-ex19del",
            "label": "EGFR exon 19 deletion",
            "type": "biomarker",
            "properties": {"synthetic": True},
        },
        {
            "id": "bio:pdl1-high",
            "label": "PD-L1 high",
            "type": "biomarker",
            "properties": {"synthetic": True},
        },
        {
            "id": "drug:osimertinib",
            "label": "Osimertinib",
            "type": "intervention",
            "properties": {"synthetic": True},
        },
        {
            "id": "drug:immunotherapy",
            "label": "Immunotherapy",
            "type": "intervention",
            "properties": {"synthetic": True},
        },
        {
            "id": "dx:advanced-nsclc",
            "label": "Advanced NSCLC",
            "type": "condition",
            "properties": {"synthetic": True},
        },
        {
            "id": "outcome:response",
            "label": "Objective response",
            "type": "outcome",
            "properties": {"synthetic": True},
        },
        {
            "id": "outcome:irae",
            "label": "Immune-related adverse event",
            "type": "outcome",
            "properties": {"synthetic": True},
        },
        {
            "id": "cohort:synthetic-a",
            "label": "Synthetic cohort A",
            "type": "cohort",
            "properties": {"synthetic": True},
        },
        {
            "id": "region:primary",
            "label": "Primary lung lesion",
            "type": "anatomy",
            "properties": {"synthetic": True},
        },
        {
            "id": "region:node",
            "label": "Mediastinal lymph node",
            "type": "anatomy",
            "properties": {"synthetic": True},
        },
    ]
    assertions = [
        {
            "id": "assertion:egfr-treatment-response",
            "predicate": "reported_association",
            "topology": "hyperedge",
            "semantics": "synthetic_demonstration",
            "epistemic_status": "synthetic_demo",
            "evidence_refs": ["evidence:synthetic-1"],
            "properties": {"synthetic": True, "note": "Interface demonstration only"},
        },
        {
            "id": "assertion:pdl1-immunotherapy",
            "predicate": "reported_association",
            "topology": "hyperedge",
            "semantics": "synthetic_demonstration",
            "epistemic_status": "synthetic_demo",
            "evidence_refs": ["evidence:synthetic-2"],
            "properties": {"synthetic": True, "note": "Interface demonstration only"},
        },
        {
            "id": "assertion:spatial-proxy",
            "predicate": "spatially_associated_with",
            "topology": "pairwise",
            "semantics": "synthetic_demonstration",
            "epistemic_status": "synthetic_demo",
            "evidence_refs": ["evidence:synthetic-3"],
            "properties": {"synthetic": True, "unit": "mm"},
        },
    ]
    members = [
        {
            "assertion_id": "assertion:egfr-treatment-response",
            "node_id": "bio:egfr-ex19del",
            "role": "biomarker",
            "ordinal": 0,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:egfr-treatment-response",
            "node_id": "drug:osimertinib",
            "role": "intervention",
            "ordinal": 1,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:egfr-treatment-response",
            "node_id": "dx:advanced-nsclc",
            "role": "condition",
            "ordinal": 2,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:egfr-treatment-response",
            "node_id": "outcome:response",
            "role": "outcome",
            "ordinal": 3,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:egfr-treatment-response",
            "node_id": "cohort:synthetic-a",
            "role": "cohort",
            "ordinal": 4,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:pdl1-immunotherapy",
            "node_id": "bio:pdl1-high",
            "role": "biomarker",
            "ordinal": 0,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:pdl1-immunotherapy",
            "node_id": "drug:immunotherapy",
            "role": "intervention",
            "ordinal": 1,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:pdl1-immunotherapy",
            "node_id": "dx:advanced-nsclc",
            "role": "condition",
            "ordinal": 2,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:pdl1-immunotherapy",
            "node_id": "outcome:irae",
            "role": "outcome",
            "ordinal": 3,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:spatial-proxy",
            "node_id": "region:primary",
            "role": "region_a",
            "ordinal": 0,
            "resolved": True,
        },
        {
            "assertion_id": "assertion:spatial-proxy",
            "node_id": "region:node",
            "role": "region_b",
            "ordinal": 1,
            "resolved": True,
        },
    ]
    evidence = [
        {
            "id": "evidence:synthetic-1",
            "type": "synthetic",
            "support": "demo_only",
            "source": "generated demo",
        },
        {
            "id": "evidence:synthetic-2",
            "type": "synthetic",
            "support": "demo_only",
            "source": "generated demo",
        },
        {
            "id": "evidence:synthetic-3",
            "type": "synthetic",
            "support": "demo_only",
            "source": "generated demo",
        },
    ]
    bundle_id = (
        "bundle_"
        + hashlib.sha256(
            _json_bytes({"nodes": nodes, "assertions": assertions, "members": members})
        ).hexdigest()[:16]
    )
    manifest = {
        "schema_version": "hk.bundle/v1",
        "bundle_id": bundle_id,
        "source_ka": None,
        "source_data_sha256": None,
        "template": "synthetic/biomedical-higher-order-graph",
        "language": "en",
        "topology_type": "mixed",
        "sources": [{"path": "generated-demo", "sha256": "synthetic", "size_bytes": 0}],
        "counts": {
            "nodes": len(nodes),
            "assertions": len(assertions),
            "members": len(members),
            "unresolved_members": 0,
            "assertions_with_evidence": len(assertions),
        },
        "limitations": [
            "All entities, assertions, and evidence are synthetic interface fixtures.",
            "No clinical or scientific conclusion may be drawn from this demo.",
        ],
    }

    _write_text(
        bundle / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    _write_jsonl(bundle / "nodes.jsonl", nodes)
    _write_jsonl(bundle / "assertions.jsonl", assertions)
    _write_jsonl(bundle / "members.jsonl", members)
    _write_jsonl(bundle / "evidence.jsonl", evidence)
    _write_text(
        bundle / "REPORT.md",
        "# Synthetic Hyper-Knowledge Demo\n\n"
        "This fixture demonstrates pairwise and role-aware hypergraph views. "
        "It is not scientific evidence.\n",
    )
    view = output / "workbench.html"
    view_result = render_bundle_html(
        bundle,
        view,
        view="contour",
        quality="showcase",
    )
    receipt = {
        "schema_version": DEMO_SCHEMA_VERSION,
        "status": "passed",
        "synthetic": True,
        "bundle_id": bundle_id,
        "bundle": str(bundle),
        "html": str(view),
        "html_sha256": _digest(view),
        "counts": manifest["counts"],
        "view": view_result,
        "claim_boundary": "Synthetic UI fixture; not clinical or scientific evidence.",
    }
    _write_text(
        output / "demo-receipt.json",
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return receipt
