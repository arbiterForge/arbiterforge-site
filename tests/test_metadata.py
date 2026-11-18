"""Negative cases for the rendered metadata release check."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_metadata_build", ROOT / "tests/check_metadata_build.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


def page():
    url = metadata.ORIGIN + "/projects/"
    title = "Projects · suadtl"
    values = {
        "description": "Tools, maps & experiments.", "author": "suadtl", "robots": "max-image-preview:large",
        "og:type": "website", "og:site_name": "suadtl", "og:title": title,
        "og:description": "Tools, maps & experiments.", "og:url": url,
        "og:image": metadata.ORIGIN + "/assets/social-projects.png", "og:image:alt": "Projects by suadtl.",
        "og:image:width": "1200", "og:image:height": "630", "og:image:type": "image/png",
        "twitter:card": "summary_large_image", "twitter:title": title,
        "twitter:description": "Tools, maps & experiments.", "twitter:image": metadata.ORIGIN + "/assets/social-projects.png",
        "twitter:image:alt": "Projects by suadtl.",
    }
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "name": "suadtl", "url": metadata.ORIGIN + "/"},
        {"@type": "WebSite", "url": metadata.ORIGIN + "/"},
        {"@type": "CollectionPage", "url": url, "name": title, "description": values["description"]},
    ]}
    tags = "".join(f'<meta {"property" if key.startswith("og:") else "name"}="{key}" content="{value}">' for key, value in values.items())
    return f'<!doctype html><html><head><title>{title}</title><link rel="canonical" href="{url}">{tags}<script type="application/ld+json">{json.dumps(graph)}</script></head><body>Projects</body></html>'


class MetadataTest(unittest.TestCase):
    def test_accepts_one_consistent_rendered_head(self):
        head = metadata.check_head(page(), metadata.ORIGIN + "/projects/")
        self.assertEqual(head.one("description"), "Tools, maps & experiments.")

    def test_rejects_duplicate_metadata_stale_canonical_and_accidental_noindex(self):
        source = page()
        cases = [
            source.replace("</head>", '<meta property="og:title" content="Old company"></head>'),
            source.replace('rel="canonical" href="https://arbiterforge.com/projects/"', 'rel="canonical" href="https://arbiterforge.com/"'),
            source.replace('content="max-image-preview:large"', 'content="noindex, follow"'),
            source.replace('name="twitter:image" content="https://arbiterforge.com/assets/social-projects.png"', 'name="twitter:image" content="https://arbiterforge.com/assets/social-home.png"'),
            source.replace('"@type": "Person"', '"@type": "Corporation"'),
        ]
        for source in cases:
            with self.subTest(source=source[:100]), self.assertRaises(ValueError):
                metadata.check_head(source, metadata.ORIGIN + "/projects/")

    def test_404_is_noindex_without_structured_page_claims(self):
        source = page().replace('content="max-image-preview:large"', 'content="noindex, follow"')
        start = source.index('<script type="application/ld+json">')
        stop = source.index("</script>", start) + len("</script>")
        source = source[:start] + source[stop:]
        metadata.check_head(source, metadata.ORIGIN + "/projects/", noindex=True)
        with self.assertRaises(ValueError):
            metadata.check_head(page(), metadata.ORIGIN + "/projects/", noindex=True)

    def test_checks_image_pixels_and_rejects_missing_external_or_escaping_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            image = root / "assets/card.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 1200, 630))
            metadata.check_image(root, metadata.ORIGIN + "/assets/card.png")
            for url in (metadata.ORIGIN + "/assets/missing.png", "https://example.com/card.png", metadata.ORIGIN + "/%2e%2e/card.png"):
                with self.subTest(url=url), self.assertRaises(ValueError):
                    metadata.check_image(root, url)
            image.write_bytes(image.read_bytes()[:16] + struct.pack(">II", 600, 315))
            with self.assertRaises(ValueError):
                metadata.check_image(root, metadata.ORIGIN + "/assets/card.png")


if __name__ == "__main__":
    unittest.main()
