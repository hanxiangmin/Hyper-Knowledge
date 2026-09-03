"""Integrity checks for local vector-index artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


INDEX_MANIFEST = ".hyperknowledge-index.json"
INDEX_SCHEMA_VERSION = "hk.index/v1"


class UntrustedIndexError(ValueError):
    """Raised when an index cannot be verified before deserialization."""


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _index_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise UntrustedIndexError(f"Index contains a symbolic link: {path}")
        if path.is_file() and path.name != INDEX_MANIFEST:
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(folder).as_posix())


def write_index_manifest(folder_path: str | Path) -> Path | None:
    """Write a SHA-256 manifest after Hyper-Knowledge creates an index."""
    folder = Path(folder_path)
    if not folder.is_dir():
        return None

    files = _index_files(folder)
    if not files:
        return None

    payload = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "files": [
            {
                "path": path.relative_to(folder).as_posix(),
                "size": path.stat().st_size,
                "sha256": _digest(path),
            }
            for path in files
        ],
    }
    manifest = folder / INDEX_MANIFEST
    manifest.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def verify_index_manifest(folder_path: str | Path) -> None:
    """Verify an index before any pickle-backed loader is allowed to run."""
    folder = Path(folder_path)
    manifest = folder / INDEX_MANIFEST
    if not manifest.is_file():
        raise UntrustedIndexError(
            "Index integrity manifest is missing. Rebuild the index with this "
            "Hyper-Knowledge version before loading it."
        )

    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UntrustedIndexError(f"Index manifest is unreadable: {exc}") from exc

    if payload.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise UntrustedIndexError("Unsupported index manifest version")

    expected = {
        entry["path"]: entry
        for entry in payload.get("files", [])
        if isinstance(entry, dict) and "path" in entry
    }
    actual_files = _index_files(folder)
    actual = {path.relative_to(folder).as_posix(): path for path in actual_files}
    if set(actual) != set(expected):
        raise UntrustedIndexError("Index file set does not match its manifest")

    for relative_path, path in actual.items():
        entry = expected[relative_path]
        if path.stat().st_size != entry.get("size") or _digest(path) != entry.get(
            "sha256"
        ):
            raise UntrustedIndexError(
                f"Index file failed integrity check: {relative_path}"
            )
