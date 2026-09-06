# Changelog

All notable changes to Hyper-Knowledge are documented here.

## [0.8.0] - 2026-09-06

### Added

- Standalone `hyper-knowledge` distribution, `hyperknowledge` import, and `hk` CLI.
- Standard `hyper-knowledge` Agent Skill with OpenAI metadata, icons, references, version contract, managed install, doctor, and no-provider demo.
- Provenance-aware `hk.bundle/v1` export and deterministic standard/showcase validation.
- Offline `hk.view/v29` workbench with incidence matrix, focused incidence, capsule-based structure overview, regularized enclosure, native pairwise view when available, bilingual UI, drag reflow, and fit-to-content reset.
- Auditable Su Shi biography examples, including the current 39-node / 18-hyperedge / 65-membership role-aware showcase.
- English and Chinese GitHub READMEs plus real-browser GIF tours, MP4 previews, full-size screenshot galleries, and SHA256 manifests.

### Changed

- Higher-order modeling is explicitly undirected; endpoint order is no longer presented as relation direction.
- Dense node focus shows only incident hyperedges instead of expanding the full incidence graph.
- Enclosure layout uses circle/ellipse geometry, fixed thick contours, capsule hyperedge labels, hover fill, and selection-aware fading.
- Incidence views label roles directly on edges without repeating them in a footer legend.
- CI, packaging, documentation, examples, and tests now target Hyper-Knowledge alone.
- Configuration and logging use the canonical `.hk` directory and `HYPER_KNOWLEDGE_*` environment variables.
- Installation examples use the verified GitHub source distribution.
- The project acknowledges Hyper-Extract as an open-source inspiration without retaining legacy runtime aliases.

### Removed

- Directed-hypergraph presentation, arrow semantics, clique expansion, projection helper nodes, and the redundant group-expansion view.
- Previous product aliases, compatibility launchers, and the unrelated multi-Skill pack.
- Machine-specific JUnit artifacts from the public example.
