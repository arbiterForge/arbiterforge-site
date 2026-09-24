"""Source-level checks for the codeArbiter derivative claims, not live qualification."""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = "index.html"

class PublicClaimsTest(unittest.TestCase):
    def test_current_claims_link_to_their_product_owners(self):
        source = (ROOT / TARGET).read_text(encoding="utf-8")
        for destination in (
            "https://codearbiter.dev/getting-started/install/",
            "https://codearbiter.dev/getting-started/compatibility/",
            "https://github.com/arbiterForge/codeArbiter/blob/main/PRIVACY.md",
            "https://github.com/arbiterForge/codeArbiter/blob/main/SECURITY.md",
            "https://github.com/arbiterForge/codeArbiter/blob/main/LICENSE",
        ):
            with self.subTest(destination=destination):
                self.assertIn(destination, source)

    def test_obsolete_absolute_and_commercial_claims_do_not_return(self):
        source = (ROOT / TARGET).read_text(encoding="utf-8").lower()
        for phrase in ("no network calls, no telemetry", "commercial licensing available",
                       "proof is never forgeable", "makes it unforgeable",
                       "writes only to", "every time.", "40 commands", "28 agents",
                       "27 tagged releases", "v2.11.0"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, source)

    def test_install_instructions_are_linked_not_another_copied_catalog(self):
        source = (ROOT / TARGET).read_text(encoding="utf-8")
        self.assertNotIn("plugin marketplace add", source)
        self.assertIn("qualified", source.lower())
        self.assertIn("preview", source.lower())

if __name__ == "__main__":
    unittest.main()
