"""Smoke-test the installed distribution from outside the repository.

Run with the clean environment's Python. Add --notebook PATH for fresh-kernel QA.
Does not call a model, update a user's Skill, or access provider credentials.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    import hyperknowledge as hk
    from hyperknowledge.skill_manager import bundled_skill_path
    from hyperknowledge.utils.template_engine import Template

    package = Path(hk.__file__).resolve()
    assert "site-packages" in package.parts, (
        f"Not a non-editable installation: {package}"
    )
    skill = bundled_skill_path()
    assert skill.is_relative_to(package.parent)
    for relative in (
        "SKILL.md",
        "references/structured-input.md",
        "assets/icon-small.svg",
        "assets/icon-large.svg",
    ):
        assert (skill / relative).is_file(), relative
    assert Template.get("general/hypergraph") is not None
    results = {
        "python": sys.version,
        "runtime": str(package),
        "package_version": hk.__version__,
        "checks": [],
    }
    with tempfile.TemporaryDirectory(prefix="hk-wheel-中文 path-") as temporary:
        root = Path(temporary)
        source = root / "notes.md"
        source.write_text("Alice and Bob collaborated in 2025.\n", encoding="utf-8")
        graph = {
            "nodes": [
                {"id": x, "label": x, "type": "entity"}
                for x in ("Alice", "Bob", "2025")
            ],
            "assertions": [
                {"id": "e", "predicate": "collaborated", "evidence_refs": ["s"]}
            ],
            "members": [
                {"assertion_id": "e", "node_id": x, "role": r}
                for x, r in (("Alice", "author"), ("Bob", "author"), ("2025", "time"))
            ],
            "evidence": [
                {
                    "id": "s",
                    "type": "source_text_span",
                    "source": "notes.md",
                    "line_start": 1,
                    "line_end": 1,
                    "quote": "Alice and Bob collaborated in 2025.",
                }
            ],
        }
        graph_path = root / "graph.json"
        graph_path.write_text(json.dumps(graph), encoding="utf-8")
        result = hk.import_graph(
            graph,
            output_dir=root / "python",
            sources={"notes.md": source},
            quality="showcase",
        )
        assert result.node_count == 3 and result.hyperedge_count == 1
        assert hk.validate_bundle(result.bundle_path)["status"] == "passed"
        hk.render_bundle_html(result.bundle_path, root / "python.html")
        assert (root / "python.html").stat().st_size > 10000
        results["checks"].append("python import / validate / packaged renderer")

        def cli(*arguments, ok=True):
            process = subprocess.run(
                [sys.executable, "-m", "hyperknowledge", *map(str, arguments)],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )
            assert (process.returncode == 0) == ok, process.stdout + process.stderr
            return json.loads(process.stdout)

        receipt = cli(
            "bundle",
            "import",
            graph_path,
            "--source",
            f"notes.md={source}",
            "-o",
            root / "cli",
            "--json",
        )
        assert receipt["node_count"] == 3
        assert (
            cli("bundle", "import", graph_path, "-o", root / "cli", "--json", ok=False)[
                "ok"
            ]
            is False
        )
        cli("visualize", root / "cli", "-o", root / "cli.html", "--no-open", "--json")
        results["checks"].append("CLI JSON / failure exit / Chinese and space paths")
        for platform in ("codex", "kimi"):
            project = root / platform
            project.mkdir()
            cli(
                "skill",
                "install",
                "--platform",
                platform,
                "--scope",
                "project",
                "--project-root",
                project,
                "--json",
            )
            cli(
                "skill",
                "install",
                "--platform",
                platform,
                "--scope",
                "project",
                "--project-root",
                project,
                "--json",
            )
            doctor = cli(
                "skill",
                "doctor",
                "--platform",
                platform,
                "--scope",
                "project",
                "--project-root",
                project,
                "--deep",
                "--json",
            )
            assert doctor["ok"], doctor
            installed = (
                project
                / (".agents" if platform == "codex" else ".kimi-code")
                / "skills/hyper-knowledge"
            )
            target = installed / "SKILL.md"
            target.write_text(
                target.read_text(encoding="utf-8") + "\nLocal edit\n", encoding="utf-8"
            )
            cli(
                "skill",
                "install",
                "--platform",
                platform,
                "--scope",
                "project",
                "--project-root",
                project,
                "--json",
                ok=False,
            )
            assert "Local edit" in target.read_text(encoding="utf-8")
            results["checks"].append(
                platform + " isolated install / repeat / deep doctor / edit protection"
            )
        # Missing independent-model configuration is checked without using host keys.
        config = root / "absent.toml"
        import hyperknowledge.utils.client as clients

        clients.DEFAULT_CONFIG_FILE = config
        with_keys = {
            key: os.environ.pop(key)
            for key in list(os.environ)
            if key.endswith("API_KEY")
        }
        try:
            try:
                hk.extract_text("Alice met Bob.", output_dir=root / "unconfigured")
            except ValueError:
                pass
            else:
                raise AssertionError("Missing model configuration must not succeed")
        finally:
            os.environ.update(with_keys)
        assert not (root / "unconfigured").exists()
        results["checks"].append("missing model config / no partial output")
        if args.notebook:
            import nbformat
            from nbclient import NotebookClient
            from jupyter_client.kernelspec import KernelSpecManager

            notebook = nbformat.read(args.notebook.resolve(), as_version=4)
            kernel_root = root / "kernels"
            kernel = kernel_root / "hk-test"
            kernel.mkdir(parents=True)
            (kernel / "kernel.json").write_text(
                json.dumps(
                    {
                        "argv": [
                            sys.executable,
                            "-m",
                            "ipykernel_launcher",
                            "-f",
                            "{connection_file}",
                        ],
                        "display_name": "Hyper-Knowledge isolated test",
                        "language": "python",
                    }
                ),
                encoding="utf-8",
            )
            client = NotebookClient(
                notebook,
                timeout=120,
                kernel_name="hk-test",
                resources={"metadata": {"path": str(root)}},
            )
            client.km = client.create_kernel_manager()
            client.km.kernel_spec_manager = KernelSpecManager(
                kernel_dirs=[str(kernel_root)]
            )
            client.execute()
            results["checks"].append("fresh notebook kernel / all code cells")
    results["ok"] = True
    text = json.dumps(results, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
