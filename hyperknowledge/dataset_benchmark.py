"""Deterministic preflight checks for Hyper-Knowledge text datasets."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "hk.dataset-benchmark/v1"
SUPPORTED_SUFFIXES = {".md", ".txt"}
KNOWN_LANGUAGES = {"en", "zh"}
KNOWN_DOMAINS = {"finance", "general", "industry", "legal", "medicine", "tcm"}


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _display_path(path: Path, cwd: Path) -> str:
    try:
        return path.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()


def _discover(inputs: list[Path]) -> list[tuple[Path, Path | None]]:
    discovered: dict[Path, Path | None] = {}
    for input_path in inputs:
        path = input_path.expanduser().resolve()
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_SUFFIXES:
                discovered[path] = None
            continue
        if path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if (
                    candidate.is_file()
                    and candidate.suffix.lower() in SUPPORTED_SUFFIXES
                ):
                    discovered[candidate.resolve()] = path
    return sorted(discovered.items(), key=lambda item: item[0].as_posix())


def inspect_dataset(path: Path, *, root: Path | None = None) -> dict[str, Any]:
    """Inspect one dataset without invoking a model or network service."""
    path = path.resolve()
    checks: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    def check(
        code: str,
        passed: bool,
        evidence: str,
        *,
        severity: str = "error",
        supported_fix: str | None = None,
    ) -> None:
        checks.append({"code": code, "passed": passed, "evidence": evidence})
        if not passed:
            diagnostic = {
                "code": code,
                "severity": severity,
                "subject": path.as_posix(),
                "evidence": evidence,
            }
            if supported_fix:
                diagnostic["supported_fix"] = supported_fix
            diagnostics.append(diagnostic)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        check("dataset.readable", False, str(exc), supported_fix="Restore the file")
        return {
            "path": path.as_posix(),
            "status": "failed",
            "checks": checks,
            "diagnostics": diagnostics,
        }

    try:
        text = raw.decode("utf-8")
        utf8 = True
        decode_error = ""
    except UnicodeDecodeError as exc:
        text = ""
        utf8 = False
        decode_error = str(exc)

    check(
        "dataset.utf8",
        utf8,
        "valid UTF-8" if utf8 else decode_error,
        supported_fix="Convert the source to UTF-8 without data loss",
    )
    check(
        "dataset.non_empty",
        bool(text.strip()),
        f"{len(text.strip())} non-whitespace characters",
        supported_fix="Provide non-empty source text",
    )
    check(
        "dataset.no_nul",
        "\x00" not in text,
        "no NUL bytes" if "\x00" not in text else "NUL byte found",
        supported_fix="Remove binary content from the text dataset",
    )
    check(
        "dataset.no_replacement_character",
        "\ufffd" not in text,
        "no Unicode replacement characters"
        if "\ufffd" not in text
        else "Unicode replacement character found",
        supported_fix="Recover the original characters before extraction",
    )
    if path.suffix.lower() == ".md":
        has_heading = any(line.lstrip().startswith("#") for line in text.splitlines())
        check(
            "dataset.markdown_heading",
            has_heading,
            "Markdown heading found" if has_heading else "no Markdown heading found",
            severity="warning",
            supported_fix="Add a descriptive Markdown heading or document the exception",
        )
    credential_pattern = re.compile(
        r"(?i)(?:sk-[a-z0-9_-]{16,}|(?:api[_-]?key|secret|password)\s*[:=]\s*\S+)"
    )
    credential_match = credential_pattern.search(text)
    check(
        "dataset.no_credential_like_text",
        credential_match is None,
        "no credential-like text"
        if credential_match is None
        else f"credential-like text at character {credential_match.start()}",
        supported_fix="Remove or replace credentials before committing or sending data",
    )
    check(
        "dataset.not_symlink",
        not path.is_symlink(),
        "regular file" if not path.is_symlink() else "symbolic link",
        severity="warning",
        supported_fix="Use a regular file or explicitly review the resolved target",
    )

    language = None
    domain = None
    relative = None
    if root is not None:
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = None
        if relative and len(relative.parts) >= 3:
            language, domain = relative.parts[0], relative.parts[1]
            check(
                "dataset.known_language",
                language in KNOWN_LANGUAGES,
                f"language={language}",
                supported_fix=f"Use one of: {', '.join(sorted(KNOWN_LANGUAGES))}",
            )
            check(
                "dataset.known_domain",
                domain in KNOWN_DOMAINS,
                f"domain={domain}",
                supported_fix=f"Use one of: {', '.join(sorted(KNOWN_DOMAINS))}",
            )

            if language in KNOWN_LANGUAGES:
                peer_language = "zh" if language == "en" else "en"
                peer = root / peer_language / Path(*relative.parts[1:])
                check(
                    "dataset.bilingual_peer",
                    peer.is_file(),
                    f"peer={peer.relative_to(root).as_posix()}",
                    severity="warning",
                    supported_fix="Add the matching bilingual fixture or document the exception",
                )

    failed = any(item["severity"] == "error" for item in diagnostics)
    return {
        "path": path.as_posix(),
        "relative_path": relative.as_posix() if relative else path.name,
        "language": language,
        "domain": domain,
        "status": "failed" if failed else "passed",
        "size_bytes": len(raw),
        "character_count": len(text),
        "line_count": len(text.splitlines()),
        "sha256": _sha256(raw),
        "checks": checks,
        "diagnostics": diagnostics,
    }


def benchmark_datasets(inputs: list[str | Path]) -> dict[str, Any]:
    """Run deterministic checks for every discovered text dataset."""
    resolved_inputs = [Path(item).expanduser().resolve() for item in inputs]
    missing = [path for path in resolved_inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Dataset input does not exist: " + ", ".join(str(path) for path in missing)
        )

    discovered = _discover(resolved_inputs)
    if not discovered:
        raise ValueError("No supported .md or .txt datasets were discovered")
    records = [inspect_dataset(path, root=root) for path, root in discovered]
    cwd = Path.cwd().resolve()
    for record in records:
        record["path"] = _display_path(Path(record["path"]), cwd)
        for diagnostic in record["diagnostics"]:
            diagnostic["subject"] = record["path"]

    failures = sum(record["status"] == "failed" for record in records)
    warnings = sum(
        diagnostic["severity"] == "warning"
        for record in records
        for diagnostic in record["diagnostics"]
    )
    digest_input = "\n".join(
        f"{record['path']}:{record.get('sha256', '')}" for record in records
    ).encode("utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_preflight",
        "status": "failed" if failures else "passed",
        "dataset_manifest_sha256": _sha256(digest_input),
        "inputs": [_display_path(path, cwd) for path in resolved_inputs],
        "summary": {
            "total": len(records),
            "passed": len(records) - failures,
            "failed": failures,
            "warnings": warnings,
            "live_semantic_extraction": "not_run",
        },
        "claim_boundary": (
            "Offline preflight validates files and dataset contracts only; it does not "
            "measure extraction accuracy or model quality."
        ),
        "datasets": records,
    }


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    candidate = path.with_suffix(path.suffix + ".candidate")
    candidate.write_text(content, encoding="utf-8")
    candidate.replace(path)


def write_dataset_benchmark(
    report: dict[str, Any], output_dir: str | Path
) -> dict[str, Any]:
    """Write machine-readable and human-readable benchmark receipts."""
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "dataset-report.json"
    markdown_path = output / "dataset-report.md"

    _atomic_write(
        json_path,
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    summary = report["summary"]
    lines = [
        "# Hyper-Knowledge Dataset Benchmark",
        "",
        f"- Status: `{report['status']}`",
        f"- Mode: `{report['mode']}`",
        f"- Datasets: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Warnings: {summary['warnings']}",
        f"- Manifest SHA-256: `{report['dataset_manifest_sha256']}`",
        "",
        f"> {report['claim_boundary']}",
        "",
        "| Dataset | Language | Domain | Bytes | Status |",
        "|---|---:|---:|---:|---:|",
    ]
    for record in report["datasets"]:
        lines.append(
            "| {path} | {language} | {domain} | {size} | {status} |".format(
                path=record["path"],
                language=record.get("language") or "-",
                domain=record.get("domain") or "-",
                size=record.get("size_bytes", 0),
                status=record["status"],
            )
        )
    diagnostics = [
        diagnostic
        for record in report["datasets"]
        for diagnostic in record.get("diagnostics", [])
    ]
    if diagnostics:
        lines.extend(
            [
                "",
                "## Diagnostics",
                "",
                "| Severity | Dataset | Check | Evidence | Supported fix |",
                "|---|---|---|---|---|",
            ]
        )
        for diagnostic in diagnostics:
            values = {
                key: str(diagnostic.get(key, "-")).replace("|", "\\|")
                for key in (
                    "severity",
                    "subject",
                    "code",
                    "evidence",
                    "supported_fix",
                )
            }
            lines.append(
                "| {severity} | {subject} | {code} | {evidence} | "
                "{supported_fix} |".format(**values)
            )
    _atomic_write(markdown_path, "\n".join(lines) + "\n")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": report["status"],
        "report_json": str(json_path),
        "report_markdown": str(markdown_path),
        "dataset_manifest_sha256": report["dataset_manifest_sha256"],
        "summary": summary,
    }
