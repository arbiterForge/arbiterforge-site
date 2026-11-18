"""Validate metadata and discovery documents in the actual Jekyll output.

SIM is composed from its own separately verified publication, so its HTML is
intentionally outside this site's metadata contract.
"""
from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ORIGIN = "https://arbiterforge.com"


class Head(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.meta = defaultdict(list)
        self.canonicals = []
        self.titles = []
        self.structured = []
        self._in_head = False
        self._title = None
        self._json = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self._in_head = True
        if not self._in_head:
            return
        if tag == "title":
            self._title = []
        if tag == "meta":
            key = attrs.get("property", attrs.get("name"))
            if key:
                self.meta[key].append(attrs.get("content", ""))
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json = []

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.titles.append("".join(self._title).strip())
            self._title = None
        if tag == "script" and self._json is not None:
            self.structured.append(json.loads("".join(self._json)))
            self._json = None
        if tag == "head":
            self._in_head = False

    def handle_data(self, value):
        if self._title is not None:
            self._title.append(value)
        if self._json is not None:
            self._json.append(value)

    def one(self, key):
        values = self.meta[key]
        if len(values) != 1 or not values[0].strip():
            raise ValueError(f"Expected one nonempty {key}, got {values!r}")
        return values[0]


def check_head(source, expected_url, *, noindex=False):
    if "{%" in source or "{{" in source or source.startswith("---"):
        raise ValueError("Unrendered Jekyll content")
    head = Head(source)
    if len(head.titles) != 1 or not head.titles[0]:
        raise ValueError("Expected one nonempty document title")
    if head.canonicals != [expected_url]:
        raise ValueError(f"Incorrect or duplicate canonical: {head.canonicals!r}")
    for key in ("description", "author", "og:type", "og:site_name", "og:image:alt", "twitter:image:alt"):
        head.one(key)
    if head.one("og:title") != head.titles[0] or head.one("twitter:title") != head.titles[0]:
        raise ValueError("Document and sharing titles disagree")
    if head.one("og:description") != head.one("description") or head.one("twitter:description") != head.one("description"):
        raise ValueError("Document and sharing descriptions disagree")
    if head.one("og:url") != expected_url:
        raise ValueError("Open Graph URL disagrees with canonical")
    if head.one("og:image") != head.one("twitter:image"):
        raise ValueError("Open Graph and Twitter images disagree")
    if head.one("og:image:alt") != head.one("twitter:image:alt"):
        raise ValueError("Open Graph and Twitter image descriptions disagree")
    if (head.one("og:image:width"), head.one("og:image:height"), head.one("og:image:type")) != ("1200", "630", "image/png"):
        raise ValueError("Incorrect sharing-image dimensions or type")
    if head.one("twitter:card") != "summary_large_image":
        raise ValueError("Sharing image card is missing")
    robots = {value.strip() for value in head.one("robots").lower().split(",")}
    if noindex:
        if "noindex" not in robots or head.structured:
            raise ValueError("404 must be noindex and omit page structured data")
    else:
        if robots & {"noindex", "none"}:
            raise ValueError("Public page accidentally excluded from indexing")
        if len(head.structured) != 1:
            raise ValueError("Expected one JSON-LD graph")
        structured = head.structured[0]
        if structured.get("@context") != "https://schema.org":
            raise ValueError("Unknown structured-data vocabulary")
        graph = structured.get("@graph", [])
        people = [item for item in graph if item.get("@type") == "Person"]
        websites = [item for item in graph if item.get("@type") == "WebSite"]
        pages = [item for item in graph if item.get("url") == expected_url and item.get("@type") in ("WebPage", "ProfilePage", "CollectionPage", "Article")]
        if len(people) != 1 or people[0].get("name") != "suadtl" or people[0].get("url") != ORIGIN + "/":
            raise ValueError("Missing personal-site identity")
        if len(websites) != 1 or websites[0].get("url") != ORIGIN + "/":
            raise ValueError("Missing WebSite identity")
        if len(pages) != 1 or pages[0].get("name") != head.titles[0]:
            raise ValueError("Structured page identity disagrees with document")
        if pages[0].get("description") != head.one("description"):
            raise ValueError("Structured description disagrees with document")
        if any(item.get("@type") in ("Corporation", "Organization", "NewsMediaOrganization") for item in graph):
            raise ValueError("Personal site must not invent a company or newsroom")
    return head


def check_image(root, image_url):
    parsed = urlsplit(image_url)
    if (parsed.scheme, parsed.netloc) != ("https", "arbiterforge.com") or parsed.query or parsed.fragment:
        raise ValueError(f"Sharing image must be an absolute local HTTPS URL: {image_url}")
    path = (root / unquote(parsed.path).lstrip("/")).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Missing local sharing image: {image_url}")
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR" or len(data) < 24:
        raise ValueError(f"Sharing image is not a PNG: {image_url}")
    if struct.unpack(">II", data[16:24]) != (1200, 630):
        raise ValueError(f"Sharing image pixels disagree with metadata: {image_url}")
    if len(data) > 1_000_000:
        raise ValueError(f"Sharing image exceeds the 1 MB budget: {image_url}")


def verify(output):
    root = output.resolve()
    indexed = set()
    images = set()
    titles = set()
    count = 0
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("SIM/"):
            continue
        route = "/" + relative.removesuffix("index.html") if path.name == "index.html" else "/" + relative
        noindex = relative == "404.html"
        expected_url = ORIGIN + route
        try:
            head = check_head(path.read_text(encoding="utf-8"), expected_url, noindex=noindex)
            image = head.one("og:image")
            if image not in images:
                check_image(root, image)
                images.add(image)
            if head.titles[0] in titles:
                raise ValueError("Duplicate page title")
            titles.add(head.titles[0])
        except (ValueError, KeyError) as error:
            raise ValueError(f"{relative}: {error}") from error
        if not noindex:
            indexed.add(expected_url)
        count += 1

    if count < 9 or not (root / "404.html").is_file():
        raise ValueError("Site shell routes or the custom 404 are missing")
    sitemap = ET.parse(root / "sitemap.xml").getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if sitemap.tag != ns + "urlset":
        raise ValueError("Incorrect sitemap root")
    urls = [node.text for node in sitemap.findall(f"{ns}url/{ns}loc")]
    if len(urls) != len(set(urls)) or set(urls) != indexed:
        raise ValueError(f"Sitemap does not match indexable canonical pages; missing={indexed - set(urls)}, unexpected={set(urls) - indexed}")
    # No build-time lastmod values: the source has edition dates, not reliable
    # modification timestamps for every page or recovered historical record.
    if sitemap.findall(f"{ns}url/{ns}lastmod"):
        raise ValueError("Sitemap must not invent last-modified timestamps")
    robots = (root / "robots.txt").read_text(encoding="utf-8")
    rules = [line.strip() for line in robots.splitlines() if line.strip() and not line.startswith("#")]
    if "User-agent: *" not in rules or "Allow: /" not in rules or f"Sitemap: {ORIGIN}/sitemap.xml" not in rules or "Disallow: /" in rules:
        raise ValueError("robots.txt does not allow the public site and identify its sitemap")
    print(f"Metadata output OK: {count} pages, {len(images)} sharing images, {len(indexed)} sitemap URLs, personal identity and noindex 404")


if __name__ == "__main__":
    verify(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
