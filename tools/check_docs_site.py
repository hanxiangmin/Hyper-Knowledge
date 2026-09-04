"""Check the bilingual handbook and its built links before Pages deployment."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

GUIDES = (
    "install",
    "document",
    "modeling",
    "artifacts",
    "workbench",
    "sushi",
    "commands",
    "faq",
    "about",
)
RETIRED = (
    "getting-started",
    "cli",
    "python",
    "concepts",
    "templates",
    "tutorials",
    "resources",
    "mcp",
)


class PageLinks(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("name"):
            self.ids.add(values["name"])
        for attr in ("href", "src", "poster"):
            if attr in values and values[attr] is not None:
                self.links.append(values[attr])


def local_target(page: str, link: str, base_path: str) -> tuple[str, str] | None:
    """Resolve a rendered URL at a Pages subpath without consulting the network."""
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc:
        return None
    base = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"
    resolved = urlsplit(urljoin("https://docs.invalid" + base + page, link))
    path = unquote(resolved.path)
    if not path.startswith(base):
        raise ValueError(f"Link escapes site base {base}: {page} -> {link}")
    relative = path[len(base) :]
    if ".." in Path(relative).parts:
        raise ValueError(f"Link escapes site directory: {link}")
    if not relative or relative.endswith("/"):
        relative += "index.html"
    return relative, unquote(resolved.fragment)


def check_site(site: Path, source: Path, base_path: str) -> dict:
    errors: list[str] = []
    expected: set[str] = set()
    for locale, prefix in (("en", ""), ("zh", "zh/")):
        for name in ("index", *GUIDES):
            src = "index.md" if name == "index" else f"guide/{name}.md"
            dest = "index.html" if name == "index" else f"guide/{name}/index.html"
            expected.add(prefix + dest)
            if not (source / locale / src).is_file():
                errors.append(f"Missing authored translation: {locale}/{src}")
        for retired in RETIRED:
            if (site / prefix / retired).exists():
                errors.append(f"Historical manual published: {prefix}{retired}")

    pages = {
        file.relative_to(site).as_posix(): PageLinks(file.read_text(encoding="utf-8"))
        for file in site.rglob("*.html")
        if file.name != "404.html"
    }
    if set(pages) != expected:
        errors.append(f"Missing pages: {sorted(expected - set(pages))}")
        errors.append(f"Unexpected pages: {sorted(set(pages) - expected)}")

    checked = 0

    def check_link(page: str, link: str) -> str | None:
        nonlocal checked
        try:
            target = local_target(page, link, base_path)
        except ValueError as exc:
            errors.append(str(exc))
            return None
        if target is None:
            return None
        checked += 1
        path, fragment = target
        if not (site / path).is_file():
            errors.append(f"Missing local target: {page} -> {link} ({path})")
        elif fragment and path in pages and fragment not in pages[path].ids:
            errors.append(f"Missing anchor: {page} -> {link}")
        return path

    for page, parsed in pages.items():
        for link in parsed.links:
            check_link(page, link)

    search_file = site / "search/search_index.json"
    indexed: set[str] = set()
    if not search_file.is_file():
        errors.append("Missing search index")
    else:
        search = json.loads(search_file.read_text(encoding="utf-8"))
        for entry in search["docs"]:
            path = check_link("index.html", entry["location"])
            if path:
                indexed.add(path)
        if indexed != expected:
            errors.append(
                f"Search coverage differs from handbook: {sorted(indexed ^ expected)}"
            )

    return {
        "ok": not errors,
        "authored_pages": len(expected),
        "built_pages": len(pages),
        "indexed_pages": len(indexed),
        "local_links_checked": checked,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--source", type=Path, default=Path("docs"))
    parser.add_argument("--base-path", default="/Hyper-Knowledge/")
    args = parser.parse_args()
    result = check_site(args.site.resolve(), args.source.resolve(), args.base_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
