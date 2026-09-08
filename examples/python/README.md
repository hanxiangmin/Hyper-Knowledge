# Python / Notebook tutorial

No Hyper-Knowledge model key is required for this structured-data example.
The four nodes and two hyperedges come from the short tutorial fixture, not an independent historical review.

Install the runtime in a retained Python environment, then run:

```bash
python examples/python/quickstart.py --output output/tutorial
```

Or use the same input through the CLI:

```bash
hk bundle import examples/python/graph.json --source notes.md=examples/python/notes.md -o output/cli-bundle --json
hk bundle validate output/cli-bundle --quality showcase --json
hk visualize output/cli-bundle -o output/cli-workbench.html --no-open --json
```

Open [quickstart.ipynb](quickstart.ipynb) in Jupyter. Select the kernel belonging to
the environment where Hyper-Knowledge is installed. Its code runs without network
access; its optional `%pip` installation instruction is in Markdown.

The notebook constructs its own input and uses a new temporary output directory
on every execution. The script protects existing output; choose a new
`--output` directory on subsequent runs.
