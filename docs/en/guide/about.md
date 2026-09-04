# About the project

Hyper-Knowledge addresses a specific task: helping an agent turn domain documents into higher-order knowledge graphs that can be inspected, traced, and explored.

The primary entry point is a local Agent Skill. Deliverables include normalized structure, membership roles, source records, and validation receipts—not only a picture. The workbench makes those structures easier to read.

## Where this project concentrates its work

- **Modeling conventions:** keep people, places, and times separate; represent events as hyperedges and roles as membership attributes.
- **Normalized delivery:** use `hk.bundle/v1` to separate nodes, assertions, memberships, and evidence, with topology, reference, and file-identity checks.
- **Skill operations:** managed installation, environment checks, a no-model demo, and task-oriented instructions.
- **Offline exploration:** enclosure, focused incidence, a membership matrix, and a details panel for following sources.

These are the project's product and implementation priorities, not claims to have invented hypergraphs, event roles, or provenance.

## Open-source foundations and acknowledgements

This project draws on and reuses parts of [Hyper-Extract](https://github.com/yifanfeng97/hyper-extract), including foundations for template-based extraction, model invocation, and Knowledge Abstract processing. We thank its authors and contributors.

Hyper-Knowledge builds its workflow and implementation around higher-order modeling, normalized bundles, Skill management, and an interactive workbench. This handbook follows those tasks. The inherited extraction foundation is not presented as independently original work. Reuse follows applicable licenses, with required copyright and attribution notices retained.

## Where to read the code

| Entry point | Contents |
| --- | --- |
| [`hyper-knowledge/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyper-knowledge) | Skill instructions and reference contracts |
| [`hyperknowledge/bundle.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/bundle.py) | Bundle export and validation |
| [`hyperknowledge/skill_manager.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/skill_manager.py) | Managed installation, checks, and runtime binding |
| [`hyperknowledge/visualization/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyperknowledge/visualization) | Visualization and offline HTML export |
| [`examples/sushi-document-test/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-document-test) | Source material, bundle, and workbench example |

## Contribute

Domain examples, modeling counterexamples, better source location, and reproducible interaction reports are welcome. Explain the expected relationship and how the output differs, rather than supplying only a complex screenshot.

The project uses the [Apache-2.0 license](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/LICENSE).

Keywords: agent skill, knowledge graph, higher-order knowledge graph, hypergraph, hyperedge, relation extraction, event modeling, membership roles, provenance, incidence matrix, offline visualization.
