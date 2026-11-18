"""Contract checks for the personal project's case-study pages."""
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

class ShowcaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = json.loads((ROOT / "_data/projects.json").read_text(encoding="utf-8"))
        cls.studies = json.loads((ROOT / "_data/showcases.json").read_text(encoding="utf-8"))

    def test_every_real_project_has_a_published_case(self):
        self.assertEqual({p["id"] for p in self.projects}, set(self.studies))
        for project in self.projects:
            ident = project["id"]
            case = self.studies[ident]
            page = ROOT / "projects" / ident / "index.html"
            self.assertTrue(page.is_file(), page)
            self.assertIn(f"project: {ident}", page.read_text(encoding="utf-8"))
            self.assertEqual(case["open"], project["href"])
            self.assertEqual(case["source"], project["source"])
            self.assertGreaterEqual(len(case["features"]), 3)
            self.assertGreaterEqual(len(case["decisions"]), 2)
            self.assertGreater(len(case["summary"]), 90)

    def test_images_and_links(self):
        self.assertTrue((ROOT / "projects/index.html").is_file())
        for ident, case in self.studies.items():
            for field in ("open", "source", "guide", "proof"):
                url = case[field]
                self.assertTrue(url.startswith("/") or urlsplit(url).scheme == "https", (ident, field))
                self.assertNotIn("\\", url)
            if case["image"]:
                self.assertTrue(case["image"].startswith("/assets/"))
                self.assertTrue((ROOT / case["image"].lstrip("/")).is_file())

    def test_no_undisclosed_simulation_of_real_integrations(self):
        layout = (ROOT / "_layouts/project-showcase.html").read_text(encoding="utf-8")
        script = (ROOT / "assets/project-showcases.js").read_text(encoding="utf-8")
        self.assertIn("not an invocation", self.studies["codearbiter"]["demo_description"])
        self.assertIn("fictional", self.studies["sim"]["demo_description"].lower())
        self.assertIn("not the singedTerra engine", self.studies["singedterra"]["demo_description"])
        for ident in ("codearbiter", "sim"):
            self.assertIn(f"page.project == '{ident}'", layout)
        self.assertIn("{% else %}", layout)
        for selector in ("[data-gate-demo]", "[data-sim-demo]", "[data-trajectory-demo]"):
            self.assertIn(selector, script)
        self.assertIn('{% include theme-head.html %}', layout)
        self.assertIn('id="main"', layout)
        self.assertIn("| escape", layout)

    def test_home_keeps_direct_links_as_well_as_case_paths(self):
        card = (ROOT / "_includes/project-card.html").read_text(encoding="utf-8")
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("{{ project.href | escape }}", card)
        self.assertIn("{{ project.source | escape }}", card)
        self.assertIn("/projects/{{ project.id | escape }}/", card)
        self.assertIn("/projects/", home)
        self.assertIn("/assets/project-showcases.css", home)

if __name__ == "__main__":
    unittest.main()
