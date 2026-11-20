"""Homepage thumbnails must show their projects, not repeated abstract art."""
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class HomeProjectPreviewTests(unittest.TestCase):
    def test_representative_assets_are_valid_local_svg(self):
        paths = {
            "codearbiter": ROOT / "assets/project-thumb-codearbiter.svg",
            "sim": ROOT / "assets/project-thumb-sim.svg",
        }
        for name, path in paths.items():
            with self.subTest(project=name):
                data = path.read_bytes()
                self.assertLess(len(data), 40_000)
                root = ElementTree.fromstring(data)
                self.assertTrue(root.tag.endswith("svg"))
                self.assertIn('viewBox', root.attrib)
                self.assertNotIn(b'<script', data.lower())
                self.assertNotIn(b'<image', data.lower())
                self.assertNotIn(b'href="http', data)

    def test_codearbiter_shows_real_workflow_stages(self):
        text = (ROOT / "assets/project-thumb-codearbiter.svg").read_text()
        for phrase in ("Route", "Evidence", "Review", "Decision", "Regression-test-first", "Requires evidence", "Illustrative workflow"):
            self.assertIn(phrase, text)

    def test_sim_shows_actual_fictional_example(self):
        text = (ROOT / "assets/project-thumb-sim.svg").read_text()
        for phrase in ("DEMO DATASET", "FICTIONAL", "NETWORK A", "NETWORK B", "EXTERNAL", "App portal", "Identity", "Monitoring", "Consumer"):
            self.assertIn(phrase, text)

    def test_home_cards_are_different_and_game_uses_actual_capture(self):
        card = (ROOT / "_includes/project-card.html").read_text()
        self.assertIn('src="/assets/project-thumb-codearbiter.svg"', card)
        self.assertIn('src="/assets/project-thumb-sim.svg"', card)
        self.assertIn('src="/assets/meridian-project.webp"', card)
        self.assertIn('src="/assets/singedterra-game.jpg"', card)
        self.assertNotIn("material-study--codearbiter", card)
        self.assertNotIn("material-study--sim", card)
        self.assertIn('/projects/{{ project.id | escape }}/', card)
        self.assertIn('{{ project.href | escape }}', card)
        self.assertIn('{{ project.source | escape }}', card)
        self.assertEqual(card.count('loading="lazy"'), card.count('<img '))
        css = (ROOT / "assets/atelier.css").read_text()
        self.assertIn(".project-preview {", css)
        self.assertNotIn(".material-study--sim", css)


if __name__ == "__main__":
    unittest.main()
