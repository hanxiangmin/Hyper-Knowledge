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

Some ideas in this project were inspired by the open-source [Hyper-Extract](https://github.com/yifanfeng97/hyper-extract) project. We thank its authors and contributors.

Hyper-Knowledge independently organizes its own higher-order graph model, normalized bundle contract, Skill workflow, and interactive workbench. This handbook follows those tasks and does not present general concepts such as hypergraphs, event roles, or provenance as independent inventions.

## Where to read the code

| Entry point | Contents |
| --- | --- |
| [`hyper-knowledge/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyper-knowledge) | Skill instructions and reference contracts |
| [`hyperknowledge/bundle.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/bundle.py) | Bundle export and validation |
| [`hyperknowledge/skill_manager.py`](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/hyperknowledge/skill_manager.py) | Managed installation, checks, and runtime binding |
| [`hyperknowledge/visualization/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/hyperknowledge/visualization) | Visualization and offline HTML export |
| [`examples/sushi-local-preview/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-local-preview) | Current Su Shi showcase bundle and capsule overview workbench |
| [`examples/sushi-document-test/`](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-document-test) | Earlier source material, bundle, and workbench example |

## Contribute

Domain examples, modeling counterexamples, better source location, and reproducible interaction reports are welcome. Explain the expected relationship and how the output differs, rather than supplying only a complex screenshot.

The project uses the [Apache-2.0 license](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/LICENSE).

Keywords: agent skill, knowledge graph, higher-order knowledge graph, hypergraph, hyperedge, relation extraction, event modeling, membership roles, provenance, incidence matrix, offline visualization.
