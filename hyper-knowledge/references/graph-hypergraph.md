# Graph and hypergraph semantics

## Pairwise graph

Use an undirected pairwise graph when an assertion connects two symmetric endpoints. Preserve:

- endpoint identity and a stable serialization order;
- predicate semantics;
- weight meaning;
- temporal or spatial context;
- extraction or inference status.

Do not merge co-occurrence, similarity, dependency, causality, and knowledge assertions merely because they connect the same nodes.

## Hypergraph

Use a hypergraph when a single assertion owns an arbitrary member set. Members may have roles such as participant, treatment, outcome, location, sovereign, minister, source, or target.

Represent the structure conceptually as:

```text
Assertion(id, predicate, topology, semantics, epistemic_status)
Member(assertion_id, node_id, role, ordinal)
```

Do not flatten a hyperedge into pairwise facts. The workbench uses enclosure and incidence representations to preserve it losslessly. Clique, star, or line-graph projections belong only in an explicitly requested downstream analysis artifact; they are not part of the default renderer.

Do not place several times and several places in one flat hyperedge when the source defines event-specific correspondences. Create one assertion for each event and connect its person, time, place, and other participants directly in that role-aware hyperedge. Use the action or event phrase as the assertion predicate, not as an entity node: for example, model `苏轼` + `1101年` + `常州` as members of a `北归` hyperedge instead of creating a `1101年北归常州阶段` node. Store chronological order in assertion metadata or member `ordinal` values. Chronology is contextual ordering, not graph direction.

Node labels should name atomic people, places, times, objects, concepts, or official titles. Do not concatenate a time, action, place, and words such as `阶段` into one display node merely to preserve an episode. A longer official proper name or work title may remain atomic and should wrap visually rather than be semantically split. Create an event or stage node only when the source treats that episode as a reusable entity that participates independently in other assertions.

## Selection rule

- Two endpoints in one symmetric relation: undirected graph.
- Three or more participants in one indivisible event: hypergraph.
- Multiple semantic member groups: role-aware hypergraph.
- Time or space modifies an assertion: temporal, spatial, or spatio-temporal graph/hypergraph semantics.

When uncertain, preserve the richest lossless undirected structure first. If a downstream analysis explicitly requires a projection, create a separate derived artifact with its method and parameters recorded. If source semantics require direction, this package is not the correct representation layer.
