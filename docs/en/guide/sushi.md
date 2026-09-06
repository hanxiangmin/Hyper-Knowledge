# Su Shi: from a person to one event

A biographical example makes the modeling decisions easier to inspect than a complex picture alone. This case selects 18 source-traceable higher-order relationships rather than attempting exhaustive extraction.

[Read the input](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/sushi-local-preview/source/sushi.md) · [Inspect the normalized bundle](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-local-preview/bundle) · [View the workbench gallery](workbench.md)

## Step 1: identify the shared person

Su Shi participates in multiple enclosures. Reusing a node means that one entity participates in different events, not that those events mean the same thing.

Switch to incidence and select Su Shi to show only his 18 incident relationships. Select the San Su relationship to expand its four members: Su Shi, Su Xun, Su Zhe, and the Three Su group.

## Step 2: inspect roles, not just names

The four membership roles are central person, father, younger brother, and group designation. The Three Su group is not the same entity as Su Xun merely because they appear in one hyperedge. A two-member hyperedge is still preserved with roles; Hyper-Knowledge does not add a third node merely to make the picture look more uniform.

Follow `evidence:family-san-su` in the source details to line 3 of the input document. Then use the matrix to verify that all four members belong to the same column.

## Step 3: separate distinct episodes

Collecting several dates and places in one late-life trajectory makes their correspondence ambiguous. The example uses atomic nodes plus event hyperedges:

| Event hyperedge | Person | Time | Place and role |
| --- | --- | --- | --- |
| Exile to Huizhou | Su Shi / exiled person | 1094 | Huizhou / place of exile |
| Exile to Danzhou | Su Shi / exiled person | 1097 | Danzhou / place of exile |
| Return north | Su Shi / returning person | 1101 | Changzhou / destination |

This is easier to check than putting “1097 + 1101 + Danzhou + Changzhou” in one relationship. `1097` is a time node, `Changzhou` is a place node, and `Return north` is the event hyperedge; “destination”, “time”, and “returning person” are member roles. Chronological order can be recorded as an attribute without changing undirected membership semantics.

## Open the same example locally

From the repository root, in the installed environment:

```bash
hk bundle validate examples/sushi-local-preview/bundle --quality showcase --json
hk visualize examples/sushi-local-preview/bundle -o output/sushi-workbench.html --view contour --no-open --json
```

Open `output/sushi-workbench.html`. These commands read existing structure; they do not extract the document again or call a remote model.

## What this example demonstrates

The bundle contains **39 nodes, 18 native hyperedges, and 65 memberships**, with source records for all 18 hyperedges. It demonstrates entity separation, event scope, shared membership, member roles, and source tracing. The structure overview emphasizes the full shape; the matrix is for membership lookup; the selected-hyperedge highlight is for checking one relationship in context.

These structures are source-grounded higher-order relationship candidates marked `editorial_candidate`. The input is a secondary biography and has not undergone independent historical verification. This is neither a human gold standard nor an extraction-accuracy benchmark. Review entity identity and event boundaries when adapting it to your own domain.
