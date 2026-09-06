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

Do not place several times and several places in one flat hyperedge when the source defines event-specific correspondences. Create one assertion for each event and connect its person, time, place, and other participants directly in that role-aware hyperedge. Use the action or event phrase as the assertion predicate, not as an entity node: for example, model `苏轼` + `1101年` + `常州` as members of a `北归` hyperedge instead of creating a `1101年北归常州阶段` node. Store cross-event chronology in assertion metadata such as `event_year` or `trajectory_index`. Member `ordinal` orders members within one assertion, not separate events. Chronology is contextual ordering, not graph direction.

Node labels should name atomic people, places, times, objects, concepts, or official titles. Do not concatenate a time, action, place, and words such as `阶段` into one display node merely to preserve an episode. A longer official proper name or work title may remain atomic and should wrap visually rather than be semantically split. Create an event or stage node only when the source treats that episode as a reusable entity that participates independently in other assertions.

Reuse stable node IDs across independently supported events, while preserving each event's own roles and evidence. A shared topic does not make several facts one indivisible assertion: keep co-affiliation, authorship, appointment, and creation distinct and use optional `theme` metadata to group them for navigation. Repeated treatments, experiments, or transactions with different conditions or outcomes must keep distinct context-sensitive assertion identities even when their short display names match.

Prefer explicit member roles over an undifferentiated participant list when the source supports them. Do not invent roles, missing dates, episode end times, or extra shared members to make a visualization richer. Keep a verbatim evidence `quote` separate from a paraphrased `summary`; when quoting noncontiguous passages, retain separate source spans instead of silently joining them into a new sentence.

## Selection rule

Choose topology from the requested representation and assertion semantics, not member count alone. Two-member assertions can remain role-aware hyperedges in a hypergraph, alongside larger member sets. A request for a higher-order workbench does not itself impose a minimum arity of three or require a separate binary view. Only apply an arity filter when the user explicitly asks for one; preserve the source and record any such scope. Never add an arbitrary third member or combine unrelated facts under a shared theme merely to increase arity.

- Two endpoints in one symmetric relation: an undirected graph is available when requested; a two-member hyperedge is also valid in a role-aware hypergraph.
- Three or more participants in one indivisible event: hypergraph.
- Multiple semantic member groups: role-aware hypergraph.
- Time or space modifies an assertion: temporal, spatial, or spatio-temporal graph/hypergraph semantics.

When uncertain, preserve the richest lossless undirected structure first. If a downstream analysis explicitly requires a projection, create a separate derived artifact with its method and parameters recorded. If source semantics require direction, this package is not the correct representation layer.
