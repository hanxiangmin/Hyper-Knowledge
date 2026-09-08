# Compatibility and test status

This page separates implemented support from real-client verification.
Status recorded on **2026-09-08**, for the multi-entry source revision based on 0.8.0.
These are local verification records; see [GitHub Actions](https://github.com/hanxiangmin/Hyper-Knowledge/actions) for each commit's remote checks. This source update does not publish a PyPI release.

## Runtime and installation

| Check | Environment | Result |
| --- | --- | --- |
| Full unit/regression suite | Windows, Python 3.12.14 | 622 passed, 10 skipped; external-service skips are not passes |
| Standard Skill validation | skill-creator validator | Passed |
| sdist → wheel; package metadata | hatchling / build / twine | Passed |
| Non-editable wheel outside checkout | Clean Windows Python 3.12.14 environment | Import, validation, rendering and CLI passed |
| pip installation from sdist | Same isolated environment, non-editable | Passed |
| Codex and Kimi installers | Isolated project scopes | Repeat install, pinned launcher, deep check and local-edit protection passed |
| Notebook | New kernel in the isolated environment | All code cells executed |
| Documented no-key examples | English and Chinese Python/API guides | Executed successfully, not only syntax-checked |
| Previous venv installation tutorial | Windows PowerShell, clean environment, Unicode/spaced paths | Local-wheel installation, existing-environment guard, fresh-shell full-path invocation, both client installers and keyless demo passed; 48 examples in that revision were syntax-checked |
| Current environment branches and short chat instructions | Bilingual READMEs, homepages, installation and Agent guides | 16 documentation consistency checks and 4 runnable Python examples passed; PowerShell syntax passed |
| Conda command check | Local Conda 26.5.3 | Read-only environment listing and interpreter selection with conda run passed; no new environment/package installation, so no full Conda installation pass claimed |
| Windows / Linux, Python 3.11 / 3.12 matrix | package-test.yml | Configured; consult each commit's Actions results rather than extrapolating from one local environment |
| Live independent model extraction | No configured model service in this environment | Not run; unit tests cover the adapter, not provider availability |

Reproduce package checks after building and installing the wheel:

```bash
python -m build
python -m twine check dist/*
# Run from outside the checkout, using the installed environment:
python /path/to/Hyper-Knowledge/tools/verify_package.py --notebook /path/to/Hyper-Knowledge/examples/python/quickstart.ipynb
```

The smoke script checks packaged templates, Skill assets, Unicode paths, machine receipts, safe repeat installation and a fresh Notebook kernel. No user-level Skill is changed.

The previous venv tutorial was executed by `tools/check_install_docs.py` using a local wheel, temporary project scope, and an HTTPS dependency mirror configured only for that test process; user Skills were unchanged. The current documentation separates existing, Conda and venv environments. Its `--syntax-only` check confirms consistent Conda/runtime recipes across eight entry pages, with a complete, short copyable request for each of Codex and Kimi Code. This does not establish public GitHub installation, full Conda installation, or live-client success. macOS / Linux tutorial execution remains untested.

## Real clients and browser

| Client / surface | Attempt | Current result |
| --- | --- | --- |
| Codex CLI 0.149.1 | Fresh session; configured gpt-6-astra | Backend requires a newer CLI |
| Isolated Codex CLI 0.153.4 | Fresh session; explicit Skill request; same fixture | Model session started and read the document; Windows sandbox denied reading the project Skill. Full extraction/import not passed |
| Kimi Code 0.41.0 | Client startup and device login | Startup passed; OAuth request failed before a login code was issued. No model session or extraction pass claimed |
| Browser plugin | Local workbench connection | Runtime denied a required module; the plugin connection remains unavailable |
| Independent local Chrome | User-approved isolated browser; bilingual Su Zhe captures | Real clicks highlight Su Zhe's four hyperedges; no highlighted labels overlap highlighted nodes; source workbench unchanged |
| Documentation image viewer | Both languages, desktop and mobile sizes | 56 image interactions passed: image/background/button/Esc dismissal, restored focus and scroll position |
| Documentation search | Independent browser, both languages | Desktop search passed; mobile search results timed out and remain unresolved. The overall browser sweep is not marked as passed |
| Other agents | None | Not tested; no compatibility badge |

The Codex attempt distinguished the injected document instruction from source facts, but that alone does not establish end-to-end safety. Natural-language discovery, actual launcher execution, both-client output comparison and complete interaction checks on client-generated workbenches remain acceptance gates. We have not disabled client sandboxes or changed credentials to bypass them.

The existing visual design is unchanged. HTML generation and regression tests are not substitutes for clicking every view, node, hyperedge and hover state.

## Completing client acceptance

With working client login and appropriate file/command permissions, run the isolated harness:

```bash
python tools/run_agent_check.py --platform codex --client /path/to/codex --workspace /new/test-directory
python tools/run_agent_check.py --platform codex --client /path/to/codex --workspace /another/new-directory --natural
```

Use `--platform kimi` and its executable for Kimi. Login remains interactive and user-controlled. Logs and receipts stay in the chosen test directory. The harness requires a new directory and never installs to user scope.

A full pass must additionally check the selected model/version, loaded Skill path, pinned launcher command, Bundle roles/source spans, two-member hyperedges, absent injection marker, and browser interactions. Do not convert an installer pass into a client pass.

## Release gate

Source and documentation are distributed through GitHub. PyPI is a separate release process; source installation remains the current route.
After publication, verify `python -m pip install hyper-knowledge` in a clean environment before promoting that command as the public installation route.
