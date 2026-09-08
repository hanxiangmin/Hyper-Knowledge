"""No model key required. Run from any directory; output must be new or empty."""

import argparse
import json
from pathlib import Path

from hyperknowledge import (
    import_graph,
    read_bundle,
    render_bundle_html,
    validate_bundle,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/tutorial"))
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    result = import_graph(
        here / "graph.json",
        sources={"notes.md": here / "notes.md"},
        output_dir=args.output / "bundle",
        quality="showcase",
    )
    tables = read_bundle(result.bundle_path)
    assert len(tables["nodes"]) == 4 and result.hyperedge_count == 2
    assert validate_bundle(result.bundle_path)["status"] == "passed"
    page = args.output / "workbench.html"
    render_bundle_html(result.bundle_path, page)
    print(
        json.dumps(
            {**result.to_dict(), "html": str(page.resolve())}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
