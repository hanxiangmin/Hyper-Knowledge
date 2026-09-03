"""Install and verify the bundled Hyper-Knowledge Codex skill."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

SKILL_NAME = "hyper-knowledge"
OWNERSHIP_MANIFEST = ".hyperknowledge-skill.json"
RUNTIME_MANIFEST = ".hyperknowledge-runtime.json"
MANIFEST_SCHEMA = "hyperknowledge.skill-install/v1"
RUNTIME_SCHEMA = "hyperknowledge.skill-runtime/v1"


class SkillInstallError(RuntimeError):
    """Raised when a skill installation cannot be completed safely."""


def bundled_skill_path() -> Path:
    packaged = Path(__file__).resolve().parent / "skill"
    if (packaged / "SKILL.md").is_file():
        return packaged
    return Path(__file__).resolve().parent.parent / SKILL_NAME


def _package_version() -> str:
    try:
        return version("hyper-knowledge")
    except PackageNotFoundError:
        return "source"


def _hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _managed_files(skill_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(skill_dir).as_posix(): _hash_file(path)
        for path in sorted(skill_dir.rglob("*"))
        if path.is_file() and path.name != OWNERSHIP_MANIFEST
    }


def _write_runtime(skill_dir: Path) -> dict[str, object]:
    runtime_dir = skill_dir / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    python = Path(sys.executable).resolve()
    if os.name == "nt":
        launcher = runtime_dir / "hk.cmd"
        launcher.write_text(f'@"{python}" -m hyperknowledge %*\r\n', encoding="utf-8")
    else:
        launcher = runtime_dir / "hk"
        launcher.write_text(
            f'#!/bin/sh\nexec "{python}" -m hyperknowledge "$@"\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)

    payload = {
        "schema_version": RUNTIME_SCHEMA,
        "python_executable": str(python),
        "module": "hyperknowledge",
        "launcher": launcher.relative_to(skill_dir).as_posix(),
        "package_version": _package_version(),
    }
    (skill_dir / RUNTIME_MANIFEST).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload


def _runtime_checks(skill_dir: Path, *, deep: bool) -> tuple[list[dict], list[str]]:
    checks: list[dict] = []
    issues: list[str] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})
        if not ok:
            issues.append(detail)

    runtime_path = skill_dir / RUNTIME_MANIFEST
    if not runtime_path.is_file():
        record("runtime.manifest", False, f"runtime manifest missing: {runtime_path}")
        return checks, issues
    try:
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record("runtime.manifest", False, f"runtime manifest unreadable: {exc}")
        return checks, issues

    record(
        "runtime.schema",
        runtime.get("schema_version") == RUNTIME_SCHEMA,
        f"runtime schema={runtime.get('schema_version')}",
    )
    python = Path(str(runtime.get("python_executable", "")))
    record(
        "runtime.python",
        python.is_file(),
        f"python executable {'found' if python.is_file() else 'missing'}: {python}",
    )
    launcher = skill_dir / str(runtime.get("launcher", ""))
    record(
        "runtime.launcher",
        launcher.is_file(),
        f"launcher {'found' if launcher.is_file() else 'missing'}: {launcher}",
    )

    if deep and python.is_file():
        try:
            probe = subprocess.run(
                [str(python), "-m", "hyperknowledge", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            record(
                "runtime.version_probe",
                probe.returncode == 0 and _package_version() in probe.stdout,
                f"version probe exit={probe.returncode}",
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            record("runtime.version_probe", False, f"version probe failed: {exc}")

        try:
            from hyperknowledge.demo import create_skill_demo

            with tempfile.TemporaryDirectory(prefix="hyperknowledge-doctor-") as temp:
                receipt = create_skill_demo(Path(temp) / "demo")
                record(
                    "runtime.synthetic_demo",
                    receipt.get("status") == "passed"
                    and Path(str(receipt.get("html"))).is_file(),
                    f"synthetic demo status={receipt.get('status')}",
                )
        except Exception as exc:
            record("runtime.synthetic_demo", False, f"synthetic demo failed: {exc}")

    return checks, issues


def _find_project_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def install_root(
    scope: str, *, project_root: str | Path | None = None, user_home: Path | None = None
) -> Path:
    if scope == "user":
        # ``user_home`` is an explicit override used by embedders and tests.  For
        # normal CLI use, honour Codex's configured home before falling back to
        # the standard per-user Codex directory.
        if user_home is not None:
            return user_home / ".codex" / "skills"
        codex_home = os.environ.get("CODEX_HOME", "").strip()
        if codex_home:
            return Path(codex_home).expanduser() / "skills"
        return Path.home() / ".codex" / "skills"
    if scope == "project":
        root = Path(project_root) if project_root else _find_project_root(Path.cwd())
        return root.resolve() / ".agents" / "skills"
    raise SkillInstallError("scope must be 'user' or 'project'")


def _read_manifest(skill_dir: Path) -> dict[str, object] | None:
    path = skill_dir / OWNERSHIP_MANIFEST
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def inspect_installation(target: Path) -> dict[str, object]:
    if not target.is_dir():
        return {"ok": False, "status": "not_installed", "path": str(target)}

    manifest = _read_manifest(target)
    if not manifest or manifest.get("schema_version") != MANIFEST_SCHEMA:
        return {
            "ok": False,
            "status": "unmanaged",
            "path": str(target),
            "issues": ["ownership manifest is missing or invalid"],
        }

    expected = manifest.get("files", {})
    expected = expected if isinstance(expected, dict) else {}
    actual = _managed_files(target)
    issues: list[str] = []
    if set(actual) != set(expected):
        issues.append("managed file set changed")
    for relative_path in sorted(set(actual) & set(expected)):
        if actual[relative_path] != expected[relative_path]:
            issues.append(f"modified file: {relative_path}")

    installed_version = manifest.get("package_version")
    current_version = _package_version()
    if installed_version != current_version:
        issues.append(
            f"version mismatch: installed={installed_version}, package={current_version}"
        )

    return {
        "ok": not issues,
        "status": "healthy" if not issues else "drifted",
        "path": str(target),
        "package_version": current_version,
        "installed_version": installed_version,
        "issues": issues,
    }


def install_skill(
    *,
    scope: str = "user",
    project_root: str | Path | None = None,
    force: bool = False,
    user_home: Path | None = None,
) -> dict[str, object]:
    source = bundled_skill_path()
    if not (source / "SKILL.md").is_file():
        raise SkillInstallError(f"Bundled skill is incomplete: {source}")

    root = install_root(scope, project_root=project_root, user_home=user_home)
    root.mkdir(parents=True, exist_ok=True)
    target = root / SKILL_NAME
    previous = inspect_installation(target)
    if (
        target.exists()
        and previous.get("status") in {"unmanaged", "drifted"}
        and not force
    ):
        raise SkillInstallError(
            f"Refusing to overwrite {previous.get('status')} skill at {target}; "
            "inspect it first or pass --force."
        )

    staging_root = Path(tempfile.mkdtemp(prefix=".hyper-knowledge-install-", dir=root))
    staged = staging_root / SKILL_NAME
    backup: Path | None = None
    try:
        shutil.copytree(source, staged)
        runtime = _write_runtime(staged)
        manifest = {
            "schema_version": MANIFEST_SCHEMA,
            "skill": SKILL_NAME,
            "package_version": _package_version(),
            "installed_at": datetime.now(UTC).isoformat(),
            "scope": scope,
            "runtime": runtime,
            "files": _managed_files(staged),
        }
        (staged / OWNERSHIP_MANIFEST).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if target.exists():
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            backup = root / f".{SKILL_NAME}.backup-{stamp}"
            if backup.exists():
                raise SkillInstallError(f"Backup path already exists: {backup}")
            target.replace(backup)
        staged.replace(target)
    except Exception:
        if backup and backup.exists() and not target.exists():
            backup.replace(target)
        raise
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)

    result = inspect_installation(target)
    result.update(
        {
            "status": "installed",
            "scope": scope,
            "backup_path": str(backup) if backup else None,
        }
    )
    return result


def doctor_skill(
    *,
    scope: str = "user",
    project_root: str | Path | None = None,
    user_home: Path | None = None,
    deep: bool = False,
) -> dict[str, object]:
    source = bundled_skill_path()
    bundled_issues = []
    for required in ("SKILL.md", "agents/openai.yaml"):
        if not (source / required).is_file():
            bundled_issues.append(f"bundled file missing: {required}")

    target = (
        install_root(scope, project_root=project_root, user_home=user_home) / SKILL_NAME
    )
    result = inspect_installation(target)
    result["scope"] = scope
    result["bundled_skill_path"] = str(source)
    result["deep"] = deep
    if bundled_issues:
        result["ok"] = False
        result["issues"] = [*bundled_issues, *result.get("issues", [])]
    if target.is_dir() and result.get("status") not in {"unmanaged"}:
        checks, runtime_issues = _runtime_checks(target, deep=deep)
        result["checks"] = checks
        if runtime_issues:
            result["ok"] = False
            result["status"] = "broken"
            result["issues"] = [*result.get("issues", []), *runtime_issues]
    return result


def uninstall_skill(
    *,
    scope: str = "user",
    project_root: str | Path | None = None,
    force: bool = False,
    user_home: Path | None = None,
) -> dict[str, object]:
    target = (
        install_root(scope, project_root=project_root, user_home=user_home) / SKILL_NAME
    )
    state = inspect_installation(target)
    if state.get("status") == "not_installed":
        return {"ok": True, "status": "not_installed", "path": str(target)}
    if state.get("status") in {"unmanaged", "drifted"} and not force:
        raise SkillInstallError(
            f"Refusing to remove {state.get('status')} skill at {target}; "
            "inspect it first or pass --force."
        )
    shutil.rmtree(target)
    return {"ok": True, "status": "uninstalled", "path": str(target)}
