# Changelog

All notable changes to Hyper-Knowledge are documented here.

## [0.8.0] - 2026-09-03

### Added

- Standalone `hyper-knowledge` distribution, `hyperknowledge` import, and `hk` CLI.
- Standard `hyper-knowledge` Agent Skill with OpenAI metadata, icons, references, version contract, managed install, doctor, and no-provider demo.
- Provenance-aware `hk.bundle/v1` export and deterministic standard/showcase validation.
- Offline `hk.view/v29` workbench with incidence matrix, focused incidence, regularized enclosure, native pairwise view when available, bilingual UI, drag reflow, and fit-to-content reset.
- Auditable Su Shi biography example with atomic person/time/place nodes and ten undirected native hyperedges.
- English and Chinese GitHub READMEs plus six real 1920×1080 promotional captures and a SHA256 manifest.

### Changed

- Higher-order modeling is explicitly undirected; endpoint order is no longer presented as relation direction.
- Dense node focus shows only incident hyperedges instead of the full incidence graph.
- Enclosure layout uses circle-first, ellipse-fallback geometry and fixed thick contours.
- Incidence views label roles directly on edges without repeating them in a footer legend.
- CI, packaging, documentation, examples, and tests now target Hyper-Knowledge alone.

### Removed

- Directed-hypergraph presentation, arrow semantics, clique expansion, projection helper nodes, and the redundant group-expansion view.
- Previous product aliases, compatibility launchers, and the unrelated multi-Skill pack.
- Machine-specific JUnit artifacts from the public example.
