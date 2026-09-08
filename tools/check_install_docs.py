"""Exercise the copied installation recipe without modifying user installations.

The public GitHub source is replaced with a locally built wheel, and user Skill
scope is replaced with isolated project scope. No real client session is claimed.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
SOURCE = "git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
PAGES = [
    REPO / name
    for name in (
        "README.md",
        "README_ZH.md",
        "docs/en/index.md",
        "docs/zh/index.md",
        "docs/en/guide/install.md",
        "docs/zh/guide/install.md",
        "docs/en/guide/agents.md",
        "docs/zh/guide/agents.md",
    )
]


def recipe(text: str, platform: str) -> str:
    pattern = (
        rf"<!-- hk-install-{platform}:start -->\s*```\w+\n"
        rf"(.*?)```\s*<!-- hk-install-{platform}:end -->"
    )
    matches = re.findall(pattern, text, re.S)
    if len(matches) != 1:
        raise AssertionError(f"Expected one {platform} recipe")
    return matches[0].strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Check docs without installing anything",
    )
    parser.add_argument(
        "--index-url", help="Optional HTTPS dependency index for this test only"
    )
    args = parser.parse_args()
    if not args.syntax_only and args.wheel is None:
        parser.error("--wheel is required unless --syntax-only is used")
    wheel = args.wheel.resolve(strict=True) if args.wheel else None
    if sys.platform != "win32":
        parser.error("The execution phase requires Windows PowerShell.")
    shell = shutil.which("powershell")
    if not shell:
        parser.error("PowerShell was not found.")
    documents = [p.read_text(encoding="utf-8") for p in PAGES]
    windows = recipe(documents[4], "windows")
    posix = recipe(documents[4], "posix")
    runtime_recipe = recipe(documents[4], "runtime")
    conda_recipe = recipe(documents[4], "conda")
    for document in documents:
        if "hk-install-windows:start" in document:
            assert recipe(document, "windows") == windows
            assert recipe(document, "posix") == posix
        assert recipe(document, "runtime") == runtime_recipe
        assert recipe(document, "conda") == conda_recipe
        assert "--platform codex --scope user" in document
        assert "--platform kimi --scope user" in document
        assert "```bash\nhk skill install" not in document
    checks = ["8 bilingual entry pages share consistent Conda and runtime recipes"]
    report = {"checks": checks, "source_substitution": str(wheel) if wheel else None}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        PYTHON_DOTENV_DISABLED="1",
        OPENAI_API_KEY="",
        PYTHONIOENCODING="utf-8",
    )
    if args.index_url:
        if not args.index_url.startswith("https://"):
            parser.error(
                "Use an HTTPS package index without disabling certificate checks."
            )
        env["PIP_INDEX_URL"] = args.index_url
        report["dependency_index"] = args.index_url
    with tempfile.TemporaryDirectory(prefix="hk-install-中文 path-") as temporary:
        root = Path(temporary)
        runtime = root / "retained environment"
        report["isolated_root"] = str(root)

        def run(command: str, *, success: bool = True) -> str:
            command = (
                "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
                "$OutputEncoding = [Console]::OutputEncoding; " + command
            )
            completed = subprocess.run(
                [shell, "-NoProfile", "-NonInteractive", "-Command", command],
                cwd=root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=600,
            )
            output = completed.stdout.decode("utf-8-sig", errors="strict")
            if success != (completed.returncode == 0):
                stderr = completed.stderr.decode("utf-8-sig", errors="replace")
                raise AssertionError((output + stderr)[-12000:])
            if not success:
                output += completed.stderr.decode("utf-8-sig", errors="replace")
            return output

        # Parse every PowerShell example; this does not execute uninstall commands.
        blocks = {
            block
            for document in documents
            for block in re.findall(r"```powershell\n(.*?)```", document, re.S)
        }
        for block in blocks:
            literal = "'" + block.replace("'", "''") + "'"
            run(
                "$tokens=$null; $errors=$null; "
                "[void][System.Management.Automation.Language.Parser]::ParseInput("
                f"{literal}, [ref]$tokens, [ref]$errors); "
                "if ($errors.Count) { $errors; exit 1 }"
            )
        checks.append("all PowerShell examples parse successfully")
        print("Documentation consistency and PowerShell syntax passed.", flush=True)

        bash = Path(r"C:\Program Files\Git\bin\bash.exe")
        if bash.is_file():
            subprocess.run([str(bash), "-n", "-c", posix], check=True, timeout=30)
            checks.append("POSIX setup syntax checked (not a Linux install pass)")

        if args.syntax_only:
            report["ok"] = True
            report["execution"] = (
                "documentation/syntax only; no package or Skill installed"
            )
            args.report.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(json.dumps(report, ensure_ascii=True, indent=2))
            return

        candidate = (
            (windows + "\n" + runtime_recipe)
            .replace(
                'Join-Path $env:USERPROFILE ".venvs\\hyper-knowledge"',
                "'" + str(runtime).replace("'", "''") + "'",
            )
            .replace("python -m venv", f'& "{sys.executable}" -m venv')
            .replace(SOURCE, str(wheel))
        )
        assert SOURCE not in candidate
        print("Installing into a new isolated environment...", flush=True)
        output = run(candidate)
        assert "visualize" in output and "skill" in output
        checks.append(
            "first-install recipe creates a clean environment and installs the wheel"
        )
        print("Clean installation and full-path CLI help passed.", flush=True)
        marker = runtime / "pyvenv.cfg"
        original = marker.read_bytes()
        again = run(candidate, success=False)
        assert "Environment already exists" in again
        assert marker.read_bytes() == original
        checks.append("repeat setup stops without overwriting the existing environment")

        python = runtime / "Scripts/python.exe"
        runtime_help = run(f'& "{python}" -m hyperknowledge --help')
        assert "bundle" in runtime_help
        checks.append(
            "fresh PowerShell invokes the CLI by full Python path, without activation"
        )
        for platform in ("codex", "kimi"):
            project = root / platform
            project.mkdir()
            full_command = (
                f'& "{python}" -m hyperknowledge skill install '
                f'--platform {platform} --scope project --project-root "{project}" --json'
            )
            installed = json.loads(run(full_command))
            assert installed["ok"] is True, installed
            installed_path = Path(installed["path"])
            assert installed_path.is_relative_to(project)
            assert (installed_path / "SKILL.md").is_file()
            print(f"Isolated {platform} Skill installation passed.", flush=True)
        checks.append(
            "both client installers execute in isolated project scope; user Skills unchanged"
        )
        demo = json.loads(
            run(
                f'& "{python}" -m hyperknowledge skill demo -o "{root / "demo"}" --json'
            )
        )
        assert demo["ok"] is True and Path(demo["html"]).is_file()
        checks.append("documented keyless demo generates an HTML workbench")
    report["ok"] = True
    report["not_tested"] = [
        "installation from the public GitHub revision",
        "Linux/macOS runtime execution",
        "user-level Skill mutations",
        "live client discovery or model execution",
    ]
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
