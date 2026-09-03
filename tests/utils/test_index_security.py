"""Vector-index manifests gate pickle-backed index loading."""

import pytest

from hyperknowledge.utils.index_security import (
    INDEX_MANIFEST,
    UntrustedIndexError,
    verify_index_manifest,
    write_index_manifest,
)


def test_index_manifest_round_trip(tmp_path):
    index = tmp_path / "index"
    index.mkdir()
    (index / "index.faiss").write_bytes(b"faiss")
    (index / "index.pkl").write_bytes(b"metadata")

    manifest = write_index_manifest(index)

    assert manifest == index / INDEX_MANIFEST
    verify_index_manifest(index)


def test_index_manifest_rejects_tampering(tmp_path):
    index = tmp_path / "index"
    index.mkdir()
    target = index / "index.pkl"
    target.write_bytes(b"trusted")
    write_index_manifest(index)
    target.write_bytes(b"tampered")

    with pytest.raises(UntrustedIndexError, match="integrity check"):
        verify_index_manifest(index)


def test_index_manifest_rejects_missing_manifest(tmp_path):
    index = tmp_path / "index"
    index.mkdir()
    (index / "index.pkl").write_bytes(b"unknown")

    with pytest.raises(UntrustedIndexError, match="manifest is missing"):
        verify_index_manifest(index)
