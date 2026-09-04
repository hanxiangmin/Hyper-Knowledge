# Su Shi: from a person to one event

A biographical example makes the modeling decisions easier to inspect than a complex picture alone. This case selects ten representative relationships rather than attempting exhaustive extraction.

[Read the input](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/sushi-document-test/source/sushi.md) · [Inspect the normalized bundle](https://github.com/hanxiangmin/Hyper-Knowledge/tree/main/examples/sushi-document-test/bundle)

## Step 1: identify the shared person

Su Shi participates in multiple enclosures. Reusing a node means that one entity participates in different events, not that those events mean the same thing.

Switch to incidence and select Su Shi to show only his ten incident relationships. Select the Three Su family and literary group relationship to expand its four members: Su Shi, Su Xun, Su Zhe, and the Three Su group.

## Step 2: inspect roles, not just names

The four membership roles are central person, father, younger brother, and group designation. The Three Su group is not the same entity as Su Xun merely because they appear in one hyperedge.

Follow `evidence:family-san-su` in the source details to line 3 of the input document. Then use the matrix to verify that all four members belong to the same column.

## Step 3: separate distinct episodes

Collecting several dates and places in one late-life trajectory makes their correspondence ambiguous. The example now uses separate event contexts:

| Event hyperedge | Person | Time | Place and role |
| --- | --- | --- | --- |
| Exile to Huizhou | Su Shi / exiled person | 1094 | Huizhou / place of exile |
| Exile to Danzhou | Su Shi / exiled person | 1097 | Danzhou / place of exile |
| Return north | Su Shi / returning person | 1101 | Changzhou / destination |

This is easier to check than putting “1097 + 1101 + Danzhou + Changzhou” in one relationship. Chronological order can be recorded as an attribute without changing undirected membership semantics.

## Open the same example locally

From the repository root, in the installed environment:

```bash
hk bundle validate examples/sushi-document-test/bundle --quality showcase --json
hk visualize examples/sushi-document-test/bundle -o output/sushi-workbench.html --view contour --no-open --json
```

Open `output/sushi-workbench.html`. These commands read existing structure; they do not extract the document again or call a remote model.

## What this example demonstrates

The bundle contains **38 nodes, 10 hyperedges, and 49 memberships**, with source records for all ten hyperedges. It demonstrates entity separation, event scope, shared membership, and source tracing.

Codex generated the structure, marked `model_predicted`. The input is a secondary biography and has not undergone independent historical verification. This is neither a human gold standard nor an extraction-accuracy benchmark. Review entity identity and event boundaries when adapting it to your own domain.
