# Follow a relationship back to its source

The graph is not the only deliverable. An `hk.bundle/v1` bundle separates entities, assertions, memberships, and evidence so that people and programs can inspect what the picture actually represents.

## Read the assertion, then its members

In the Su Shi example, `assertion:family-san-su` records San Su. Its `topology` is `hyperedge`, its `epistemic_status` is `editorial_candidate`, and `evidence_refs` points to a source record.

| Node ID | Role in this relationship |
| --- | --- |
| `person:su-shi` | Central person |
| `person:su-xun` | Father |
| `person:su-zhe` | Younger brother |
| `group:san-su` | Group designation |

Here, “father” describes Su Xun's participation in this particular context. It is not a pairwise edge label that applies to every other member.

## Follow the evidence reference

`evidence:family-san-su` identifies `source/sushi.md`, line 3, and the relevant quotation. Check it against the [source document in the repository](https://github.com/hanxiangmin/Hyper-Knowledge/blob/main/examples/sushi-local-preview/source/sushi.md).

An evidence record preserves a source location; it does not replace reading. A model can misinterpret a passage, and the passage itself can be wrong. Source coverage is not factual accuracy.

## What the bundle contains

| File | Question it answers |
| --- | --- |
| `manifest.json` | What identifies this bundle, its contract, and its files? |
| `nodes.jsonl` | Which independent entities exist, with which IDs and labels? |
| `assertions.jsonl` | Which relationships are asserted, with which topology and epistemic status? |
| `members.jsonl` | Which entity belongs to which assertion, in which role? |
| `evidence.jsonl` | Which source records do the assertions reference? |

Validation returns structural checks separately; exports may also include reports such as `REPORT.md`. File integrity and reference coverage are not measures of extraction accuracy.

## Keep three checks separate

1. **Structure:** required files, resolvable references, topology-compatible membership counts, and file identity.
2. **Sources:** whether a record locates relevant material, and whether quotations or locations are missing.
3. **Meaning:** whether entity identity, relationship scope, and member roles agree with the material. This requires semantic review.

```bash
hk bundle validate output/notes-bundle --quality showcase --json
```

The `showcase` profile applies stricter requirements to presentation data. Export cannot invent source spans that the original KA did not retain; document the gap and revisit the material.

Coordinates, hover, and selection belong to the view, not the underlying membership facts. Continue with the [three-view guide](workbench.md).
