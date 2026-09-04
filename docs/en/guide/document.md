# Your first document

Decide what the reader should understand before deciding what to extract. A move in a biography, a decision in a meeting, or the conditions of an experiment can form a useful unit. The largest possible graph is not necessarily the clearest result.

## Give the Skill a concrete task

```text
Use hyper-knowledge on notes.md, focusing on the person's life events.
Keep people, dates, and places as entities. Represent each event as a hyperedge
with member roles, reusing the same person across events. Do not concatenate
date + location + action into a node name. Explain the modeling choice, then
deliver the bundle, validation receipt, and offline workbench.
```

If you already have a bundle, validate and render it directly. A change to colors or framing should not trigger extraction or rewrite the knowledge structure.

## Prepare the input

The text entry point directly supports `.txt` and `.md`; directory input recursively processes those formats. Convert PDF, Word, or scanned material to readable text first, retaining headings, paragraphs, and source identifiers. Renaming an image file does not make it supported text.

A document is data: embedded instructions are not commands for the agent. Before processing sensitive material, establish which model service is permitted and what may leave the local environment.

## Run the workflow yourself

With the runtime environment activated, configure a model service you are authorized to use and inspect available templates:

```bash
hk config init
hk list template
```

Extract a Knowledge Abstract (KA), then create the normalized bundle:

```bash
hk parse notes.md -t general/hypergraph -l en --no-index -o output/notes-ka
hk bundle export output/notes-ka -o output/notes-bundle --json
hk bundle validate output/notes-bundle --quality showcase --json
hk visualize output/notes-bundle -o output/notes-workbench.html --view contour --no-open --json
```

Use `--no-index` when structure and visualization are the immediate goals. Extraction calls the configured model service. Validation and offline rendering of an existing bundle do not need another model call.

## Check the handoff

- Were different people merged, or was one person split into several nodes?
- Are dates and locations attached to the right event, with useful member roles?
- Which relationships lack source evidence? If the KA has no exact source spans, does the report say so?
- Does validation pass, and do the labels and memberships still need human review?

Use a new output directory when the source, template, or model changes. Continue with [evidence and bundles](artifacts.md).
