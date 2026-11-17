"""Project destination and public-claim contracts for the personal site."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_home_build", ROOT / "scripts/check_home_build.py")
home = importlib.util.module_from_spec(spec)
spec.loader.exec_module(home)

class PublicClaimsTest(unittest.TestCase):
    def setUp(self):
        self.projects = json.loads((ROOT / "_data/projects.json").read_text(encoding="utf-8"))

    def test_project_catalog_has_safe_unique_destinations(self):
        home.validate_projects(self.projects)

    def test_required_projects_keep_their_owned_destinations(self):
        projects = {project["id"]: project for project in self.projects}
        for identifier, destination in (
            ("codearbiter", "https://codearbiter.dev/"),
            ("sim", "/SIM/"),
            ("singedterra", "https://suadtl.github.io/singedTerra/"),
        ):
            with self.subTest(project=identifier):
                self.assertEqual(projects[identifier]["href"], destination)

    def test_catalog_refuses_unsafe_links_and_duplicate_identifiers(self):
        for destination in ("javascript:alert(1)", "data:text/html,test", "//example.com/", "http://example.com/", "/../private", "/%2e%2e/private", "https://user:password@example.com/", "https://example.com/unsafe path"):
            projects = copy.deepcopy(self.projects)
            projects[0]["href"] = destination
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                home.validate_projects(projects)
        for key, value in (("id", self.projects[1]["id"]), ("id", "invalid id"), ("source", "/local-source/"), ("name", "")):
            projects = copy.deepcopy(self.projects)
            projects[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                home.validate_projects(projects)

    def test_obsolete_absolute_and_commercial_claims_do_not_return(self):
        source = ((ROOT / "index.html").read_text(encoding="utf-8") + json.dumps(self.projects)).lower()
        for phrase in ("no network calls, no telemetry", "commercial licensing available",
                       "proof is never forgeable", "makes it unforgeable",
                       "writes only to", "every time.", "40 commands", "28 agents",
                       "27 tagged releases", "v2.11.0"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, source)

if __name__ == "__main__":
    unittest.main()
