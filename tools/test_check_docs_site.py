"""Regression checks for rendered-link and bilingual-source validation."""

import json
import tempfile
import unittest
from pathlib import Path

from check_docs_site import GUIDES, PageLinks, check_site, local_target


class DocsSiteTests(unittest.TestCase):
    def test_pages_subpath_and_encoded_anchor(self):
        self.assertEqual(
            local_target(
                "zh/guide/install/index.html",
                "../modeling/#%E4%BA%BA",
                "/Hyper-Knowledge/latest/",
            ),
            ("zh/guide/modeling/index.html", "人"),
        )
        self.assertEqual(
            local_target("zh/index.html", "../assets/logo.svg", "/Hyper-Knowledge/"),
            ("assets/logo.svg", ""),
        )
        self.assertIsNone(local_target("index.html", "https://github.com/", "/"))

    def test_external_root_is_not_a_site_asset(self):
        with self.assertRaises(ValueError):
            local_target("index.html", "/assets/missing.png", "/Hyper-Knowledge/")

    def test_parser_includes_media_and_fragment_targets(self):
        parsed = PageLinks(
            '<h2 id="roles">Roles</h2><video poster="cover.png" src="tour.mp4"></video>'
        )
        self.assertEqual(parsed.ids, {"roles"})
        self.assertEqual(set(parsed.links), {"cover.png", "tour.mp4"})

    def test_checker_rejects_missing_translation_stale_manual_and_broken_asset(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            site, source = root / "site", root / "docs"
            records = []
            for locale, prefix in (("en", ""), ("zh", "zh/")):
                for name in ("index", *GUIDES):
                    src = "index.md" if name == "index" else f"guide/{name}.md"
                    dest = prefix + (
                        "index.html" if name == "index" else f"guide/{name}/index.html"
                    )
                    for file, text in (
                        (source / locale / src, "# Page"),
                        (site / dest, '<h1 id="a">Page</h1>'),
                    ):
                        file.parent.mkdir(parents=True, exist_ok=True)
                        file.write_text(text, encoding="utf-8")
                    records.append({"location": dest + "#a"})
            index = site / "search/search_index.json"
            index.parent.mkdir()
            index.write_text(json.dumps({"docs": records}), encoding="utf-8")
            self.assertTrue(check_site(site, source, "/Hyper-Knowledge/")["ok"])
            (source / "zh/guide/install.md").unlink()
            (site / "cli").mkdir()
            (site / "index.html").write_text(
                '<h1 id="a">Page</h1><img src="absent.png">', encoding="utf-8"
            )
            errors = check_site(site, source, "/Hyper-Knowledge/")["errors"]
            self.assertTrue(any("translation" in error for error in errors))
            self.assertTrue(any("manual published" in error for error in errors))
            self.assertTrue(any("absent.png" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
