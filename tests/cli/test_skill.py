"""Codex skill installer tests."""

import os
from pathlib import Path

import pytest
from hyperknowledge.cli.cli import app
from hyperknowledge.skill_manager import (
    SkillInstallError,
    bundled_skill_path,
    doctor_skill,
    install_root,
    install_skill,
    uninstall_skill,
)
from typer.testing import CliRunner

runner = CliRunner()


def test_user_skill_install_doctor_and_uninstall(tmp_path):
    installed = install_skill(scope="user", user_home=tmp_path)
    target = tmp_path / ".codex" / "skills" / "hyper-knowledge"

    assert installed["ok"] is True
    assert (target / "SKILL.md").is_file()
    assert (target / "agents" / "openai.yaml").is_file()
    metadata = (target / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for name in ("icon-small.svg", "icon-large.svg"):
        assert (target / "assets" / name).read_bytes() == (
            bundled_skill_path() / "assets" / name
        ).read_bytes()
        assert f"./assets/{name}" in metadata
    assert (target / ".hyperknowledge-runtime.json").is_file()
    launcher = "hk.cmd" if os.name == "nt" else "hk"
    assert (target / "runtime" / launcher).is_file()
    assert any((target / "runtime").iterdir())
    assert doctor_skill(scope="user", user_home=tmp_path)["status"] == "healthy"

    removed = uninstall_skill(scope="user", user_home=tmp_path)
    assert removed["status"] == "uninstalled"
    assert not target.exists()
    assert not (tmp_path / ".agents").exists()


def test_installer_refuses_modified_managed_skill(tmp_path):
    install_skill(scope="user", user_home=tmp_path)
    target = tmp_path / ".codex" / "skills" / "hyper-knowledge"
    (target / "SKILL.md").write_text("modified", encoding="utf-8")

    with pytest.raises(SkillInstallError, match="drifted"):
        install_skill(scope="user", user_home=tmp_path)

    with pytest.raises(SkillInstallError, match="drifted"):
        uninstall_skill(scope="user", user_home=tmp_path)


def test_user_install_root_prefers_codex_home(monkeypatch, tmp_path):
    codex_home = tmp_path / "configured-codex-home"
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    assert install_root("user") == codex_home / "skills"


def test_user_install_root_falls_back_to_default_codex_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    assert install_root("user") == tmp_path / ".codex" / "skills"


def test_cli_accepts_codex_platform_and_rejects_unknown_platform(tmp_path):
    installed = runner.invoke(
        app,
        [
            "skill",
            "install",
            "--platform",
            "codex",
            "--scope",
            "project",
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert installed.exit_code == 0
    assert '"status": "installed"' in installed.stdout

    rejected = runner.invoke(
        app,
        ["skill", "doctor", "--platform", "other", "--scope", "project"],
    )
    assert rejected.exit_code != 0
    assert "Only the 'codex' platform is supported" in rejected.stderr


def test_doctor_fails_when_skill_is_not_installed(tmp_path):
    result = runner.invoke(
        app,
        [
            "skill",
            "doctor",
            "--scope",
            "project",
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )
    assert result.exit_code == 1
    assert '"status": "not_installed"' in result.stdout


def test_deep_doctor_probes_runtime_and_synthetic_demo(tmp_path):
    install_skill(scope="user", user_home=tmp_path)
    result = doctor_skill(scope="user", user_home=tmp_path, deep=True)
    assert result["ok"] is True
    assert all(check["ok"] for check in result["checks"])


def test_skill_demo_command_creates_offline_artifacts(tmp_path):
    output = tmp_path / "demo"
    result = runner.invoke(
        app,
        ["skill", "demo", "--output", str(output), "--json"],
    )
    assert result.exit_code == 0, result.output
    assert (output / "workbench.html").is_file()
    assert (output / "bundle" / "manifest.json").is_file()
    assert (output / "demo-receipt.json").is_file()


def test_public_api_and_cli_expose_only_undirected_structures():
    import hyperknowledge

    assert not hasattr(hyperknowledge, "DirectedHypergraph")
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "directed" not in result.stdout.lower()
