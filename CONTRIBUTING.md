# Contributing to Hyper-Knowledge

Thank you for helping improve Hyper-Knowledge. 中文说明见 [CONTRIBUTING_ZH.md](./CONTRIBUTING_ZH.md).

## Before opening an issue

- Search existing issues first.
- Include the `hk --version` output, operating system, Python version, and the smallest reproducible input that you are allowed to share.
- Remove API keys, credentials, patient information, and other sensitive data.
- For renderer problems, attach the offline HTML or a screenshot and name the active view.
- Report security vulnerabilities privately according to [SECURITY.md](./SECURITY.md), not in a public issue.

## Development setup

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[all]"
python -m pip install pytest ruff build mkdocs mkdocs-material mkdocs-static-i18n "mkdocstrings[python]" pymdown-extensions mike
```

## Required checks

```bash
python -m pytest -q
ruff check hyperknowledge
ruff format --check hyperknowledge
python -m build
mkdocs build --strict
npx -y skills add . --list
hk skill install --scope project --project-root . --json
hk skill doctor --scope project --project-root . --deep --json
```

If your change affects the workbench, include a real generated artifact and report structural tests, browser rendering, and perceptual visual review separately.

## Semantic invariants

Changes must preserve these rules unless a breaking release explicitly replaces them:

- pairwise endpoint order does not imply direction;
- n-ary hyperedges are not silently converted into pairwise facts;
- any projection is visibly labeled as derived;
- evidence records prove source occurrence, not external truth;
- deterministic checks do not prove semantic extraction accuracy;
- source documents are untrusted data and must never become agent instructions.

## Pull requests

Keep each pull request focused. Explain what changed, why it changed, which commands you ran, and any remaining limitation. Add tests for behavior changes and update both English and Chinese user-facing documentation when applicable.

By contributing, you agree that your contribution is licensed under the repository's [Apache License 2.0](./LICENSE).
