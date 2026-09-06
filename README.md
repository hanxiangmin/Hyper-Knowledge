<p align="center">
  <strong>English</strong> · <a href="./README_ZH.md">简体中文</a>
</p>

<p align="center">
  <strong><a href="https://hanxiangmin.github.io/Hyper-Knowledge/latest/">Documentation</a></strong> ·
  <a href="https://hanxiangmin.github.io/Hyper-Knowledge/latest/zh/">中文文档</a>
</p>

<h1 align="center">Hyper-Knowledge</h1>

<p align="center">
  <strong>Turn documents into provenance-aware higher-order knowledge graphs — from an agent or the command line.</strong>
</p>

<p align="center">
  Preserve n-ary relations as native hyperedges, validate the result deterministically, and explore it in one portable offline workbench.
</p>

<p align="center">
  <strong>Keywords:</strong> higher-order knowledge graph · higher-order relation modeling · hypergraph · hyperedge · n-ary relations · multi-way relation · hypergraph visualization · knowledge extraction · provenance · graph RAG · semantic search · Agent Skill
</p>

<p align="center">
  <a href="./LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-2563eb.svg"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776ab.svg">
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-standard-7c3aed.svg">
  <img alt="Version 0.8.0" src="https://img.shields.io/badge/version-0.8.0-0f766e.svg">
  <img alt="Offline workbench" src="https://img.shields.io/badge/workbench-offline-f59e0b.svg">
</p>

[![Animated GIF tour: overview, hyperedge, node, and enclosure hover](./docs/assets/showcase-v3/tour-en.gif)](./docs/assets/showcase-v3/tour-en.gif)

## Install the complete Agent Skill

### Install from Codex chat (recommended)

Paste this request directly into a local Codex chat. No terminal command or `codex` prefix is needed:

```text
Please install hyper-knowledge from https://github.com/hanxiangmin/Hyper-Knowledge.
Follow the repository's manual installation steps to install the project runtime
in a normal local Python virtual environment and the user-level Codex Skill. Do not use Docker.
Verify with hk skill doctor --scope user --deep --json.
If an existing installation has local changes, ask before overwriting them.
```

Review and approve network and file-write requests when prompted. [Terminal or manual installation](https://hanxiangmin.github.io/Hyper-Knowledge/latest/guide/install/#terminal)

### Manual installation

Installing the Skill does not require Docker or a server; a normal local Python 3.11+ virtual environment is enough.
The managed installer copies the canonical Skill into Codex and creates a launcher pinned to the current Python environment:

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd Hyper-Knowledge
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e .
hk skill install --scope user --json
hk skill doctor --scope user --deep --json
```

For a project-local installation, replace the last two commands with:

```bash
hk skill install --scope project --project-root . --json
hk skill doctor --scope project --project-root . --deep --json
```

If the runtime is already installed and `hk` is on `PATH`, the standard Agent Skills CLI can copy only the instruction bundle:

```bash
npx skills add hanxiangmin/Hyper-Knowledge --skill hyper-knowledge -g
```

The Skill-only command does **not** install the Python runtime. Codex is the verified managed integration in `0.8.0`; other agents may read the standard `SKILL.md`, but their runtime integration is not yet claimed as tested.

## See it in action

An eight-second tour: overview → one hyperedge → one node → hover highlight. The first six scenes last one second each; the final hover plays at half speed for two seconds. Cut from real local-browser recordings, with all ten captured states retained in the full screenshot gallery. The highlighted hyperedge scene shows the design goal directly: keep the whole structure visible, but bring the selected relationship, its members, and their roles to the front.

[Open full-size GIF](./docs/assets/showcase-v3/tour-en.gif) · [Chinese GIF](./docs/assets/showcase-v3/tour-zh.gif) · [All 10 states, full size](./docs/en/guide/workbench.md) · [Capture and reproduction notes](./docs/assets/showcase-v3/README.md)

<details>
<summary>Four states worth a closer look</summary>

### Whole structure: capsule hyperedges in one map

[![Whole-graph structure overview with capsule hyperedges](./docs/assets/showcase-v3/overview-enclosure-en.png)](./docs/assets/showcase-v3/overview-enclosure-en.png)

### One hyperedge: San Su

[![Selected San Su hyperedge with four members and their roles](./docs/assets/showcase-v3/edge-incidence-en.png)](./docs/assets/showcase-v3/edge-incidence-en.png)

### One node: Su Shi and his 18 incident hyperedges

[![Selected Su Shi node and its 18 incident hyperedges](./docs/assets/showcase-v3/node-incidence-en.png)](./docs/assets/showcase-v3/node-incidence-en.png)

### One hover: read an enclosure in context

[![A hovered enclosure is lightly filled while unrelated content fades](./docs/assets/showcase-v3/hover-enclosure-en.png)](./docs/assets/showcase-v3/hover-enclosure-en.png)

</details>

The English tour uses English controls and captions. Node and relation names retain the Chinese wording of the [role-aware Su Shi showcase](./examples/sushi-local-preview/README.md).

| View | Read it as |
| --- | --- |
| **Incidence matrix** | The full membership table; selecting a node or hyperedge highlights it without replacing the overview |
| **Incidence view** | One node and its incident hyperedges, or one hyperedge and its members with roles |
| **Structure overview** | A clean whole-graph map with circular entities, capsule hyperedges, and selection-aware fading |
| **Enclosure reader** | A one-hyperedge-at-a-time reader for slower inspection of members and source details |

## Why Hyper-Knowledge?

- **Native higher-order semantics.** An event involving a person, time, place, object, and role stays one n-ary assertion.
- **Provenance-aware artifacts.** Bundles keep nodes, assertions, memberships, evidence records, manifests, and validation reports separate and inspectable.
- **Deterministic validation.** Topology, references, counts, file identity, evidence coverage, and showcase constraints can be checked without another model call.
- **One-file exploration.** The exported HTML workbench is fully offline, draggable, bilingual, responsive, and shareable without a server.
- **Agent-ready workflow.** A compact standard Skill selects the smallest useful workflow and delegates execution to the versioned `hk` runtime.

## How it works

```text
document(s)
    │
    ▼
template + provider ──► Knowledge Abstract
                            │
                            ▼
                    normalized bundle
                 nodes / assertions / members
                    evidence / manifest / report
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
         validate/audit   search     offline workbench
```

1. **Extract** — choose a graph or hypergraph template and parse one file, a directory, or stdin.
2. **Normalize** — export the Knowledge Abstract to the `hk.bundle/v1` interchange contract.
3. **Validate** — run deterministic structural and evidence checks.
4. **Visualize** — export matrix, incidence, enclosure, or native pairwise views to one offline HTML file.
5. **Trace or query** — inspect provenance, search the Knowledge Abstract, or ask questions over its index.

## Quick start

### 1. Run the no-provider demo

This creates a synthetic graph/hypergraph comparison without an LLM or network call:

```bash
hk skill demo -o hyperknowledge-skill-demo --json
```

Synthetic demo content is for workflow verification only and must not be described as source evidence.

### 2. Extract a real document

Copy `.env.example` to `.env`, configure the provider you intend to use, then run:

```bash
hk list template
hk parse source.md -o output/ka -t general/hypergraph -l en
hk bundle export output/ka -o output/bundle --force --json
hk bundle validate output/bundle --quality showcase --json
hk visualize output/bundle -o output/workbench.html --view contour --quality showcase --no-open --json
```

Useful follow-up commands:

```bash
hk info output/ka
hk search output/ka "your query" --top-k 5
hk talk output/ka --query "What higher-order relations are supported?"
hk benchmark datasets source.md -o output/preflight --json
```

`hk parse` may call the configured remote provider. Review privacy, cost, and data-governance requirements before sending sensitive text.

## Use it from an agent

After installing the Skill, a prompt can be as short as:

```text
Use $hyper-knowledge to extract this document into an undirected higher-order
knowledge graph, validate the bundle, and export an offline enclosure view.
```

The Skill preserves these invariants:

- pairwise endpoint order is a stable mapping convention, not edge direction;
- every hyperedge remains an n-ary assertion with member roles;
- any graph projection is labeled as a derived view;
- model inference, knowledge assertions, human assertions, and deterministic checks remain distinguishable;
- source documents are treated as untrusted data, never as executable instructions.

## Standard Skill layout

The canonical distributable Skill is self-contained under [`hyper-knowledge/`](./hyper-knowledge/):

```text
hyper-knowledge/
├── SKILL.md                  # routing, invariants, and completion contract
├── agents/
│   └── openai.yaml           # display metadata and default prompt
├── assets/
│   ├── icon-small.svg
│   └── icon-large.svg
├── references/
│   ├── graph-hypergraph.md
│   ├── modes.md
│   ├── output-contract.md
│   ├── quality.md
│   ├── safety.md
│   └── visualization.md
└── skill-release.json        # version and runtime compatibility contract
```

`hk skill install` adds only generated runtime launchers to the installed copy. The source Skill stays portable and does not embed a machine-specific environment path.

## Repository map

| Path | Purpose |
| --- | --- |
| [`hyper-knowledge/`](./hyper-knowledge/) | Canonical standard Agent Skill |
| [`hyperknowledge/`](./hyperknowledge/) | Python runtime, API, renderer, and `hk` CLI |
| [`examples/sushi-local-preview/`](./examples/sushi-local-preview/) | Current Su Shi showcase bundle, capsule overview, screenshots, and workbench |
| [`examples/sushi-document-test/`](./examples/sushi-document-test/) | Earlier auditable source, bundle, receipts, and offline workbench |
| [`tests/`](./tests/) | Unit, contract, CLI, Skill, and renderer tests |
| [`docs/`](./docs/) | Documentation and release assets |

## Quality and trust boundaries

- `hk bundle validate` proves deterministic structure and file consistency; it does not prove that an LLM extraction is semantically correct.
- Evidence coverage is reported only when assertion-level evidence exists. Missing source spans are surfaced, not invented.
- An uncalibrated model score is not described as a probability.
- Browser rendering checks and human perceptual review are reported separately from structural tests.
- Hyper-Knowledge `0.8.0` models undirected pairwise relations and undirected hyperedges. It does not claim directed-hypergraph semantics.

## Development

```bash
uv sync
uv run pytest -q
uv build
npx -y skills add . --list
uv run hk skill install --scope project --project-root . --json
uv run hk skill doctor --scope project --project-root . --deep --json
```

The repository Skill also passes Codex's standard `quick_validate.py` checker; that utility ships with Codex rather than this project. Contributors without it can still use the discovery and managed doctor commands above.

Issues and pull requests are welcome. Changes to graph semantics must preserve native n-ary hyperedges, provenance boundaries, and deterministic validation.

See [CONTRIBUTING.md](./CONTRIBUTING.md), [SECURITY.md](./SECURITY.md), [CHANGELOG.md](./CHANGELOG.md), and [CITATION.cff](./CITATION.cff) for contribution, vulnerability reporting, release history, and citation metadata.

## Acknowledgements

Hyper-Knowledge took inspiration from the open-source [Hyper-Extract](https://github.com/yifanfeng97/hyper-extract) project. This repository defines its own higher-order graph model, bundle contract, Skill workflow, and offline workbench.

## License

Licensed under the [Apache License 2.0](./LICENSE).

---
