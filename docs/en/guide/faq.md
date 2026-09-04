# Questions and troubleshooting

## Do I need my own server?

The local Skill and exported workbench do not require a website server. Extracting a new document requires a model: use a configured remote service or host and configure a compatible model locally. Remote-service costs and data-handling policies belong to the provider.

This GitHub Pages site documents and demonstrates the project. It does not offer document upload or hosted parsing.

## Do I need to parse again if I already have a bundle?

No. Validate it, then render it. Changing views, inspecting memberships, moving nodes, and reframing the graph do not require another extraction. [Bundle command recipes](commands.md)

## Why is hk unavailable after installing the Skill?

The instruction package and Python runtime are separate. Check that `hk --version` works in the intended environment, then run `hk skill doctor --deep --json` with the matching scope. Moving the virtual environment requires regenerating the managed launcher.

Do not conceal environment problems by disabling validation or arbitrarily editing generated path files.

## Can I pass a PDF or scan directly?

The current text entry point handles `.txt` and `.md`. Convert PDF, Word, and image inputs first, preserving paragraphs and source locations. Review OCR errors before extraction because they can affect both entities and relationships.

## Why review a relationship that already has evidence?

Source coverage means that a reference record exists. It does not establish that the passage supports the entire assertion, or that the input itself is reliable. Structural validity, traceability, and semantic correctness require different checks. [Read more](artifacts.md)

## What if dates and places are mixed together?

Revisit event scope. Represent separate episodes as separate hyperedges sharing a person node; distinguish start and end roles when multiple times really belong to one event. Moving circles cannot repair ambiguous modeling. [Modeling examples](modeling.md)

## Should I hide nodes when the graph becomes dense?

Use the matrix for membership lookup, then focus one node or hyperedge in incidence. Fading or temporarily hiding other elements does not remove data. Enclosure is useful for shared structure; it need not handle every item-by-item check.

## How should I report a problem?

Include the command, version, error receipt, and a minimal reproducible input. Use de-identified material for private documents. For layout issues, include the view, selected node or hyperedge, and window size. Remove credentials and unrelated personal information first.

[Open an issue](https://github.com/hanxiangmin/Hyper-Knowledge/issues)
