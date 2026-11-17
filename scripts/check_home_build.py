"""Check the personal homepage and its destinations in the complete Pages output."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("id", "name", "kind", "description", "href", "action", "source", "accent", "visual")
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]*\Z")


def valid_destination(value, *, local=True):
    """Project destinations must be a site-root path or an ordinary HTTPS URL."""
    if not isinstance(value, str) or not value or re.search(r"[\s\\\x00-\x1f\x7f]", value):
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme == "https":
            return bool(parsed.hostname) and parsed.username is None and parsed.password is None
        path = unquote(parsed.path)
        return (local and not parsed.scheme and not parsed.netloc
                and path.startswith("/") and not path.startswith("//")
                and "\\" not in path and not any(part in (".", "..") for part in path.split("/")))
    except ValueError:
        return False


def validate_projects(projects):
    if not isinstance(projects, list) or not projects:
        raise ValueError("Project data must be a nonempty array")
    identifiers = set()
    destinations = set()
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("Each project must be an object")
        for key in FIELDS:
            if not isinstance(project.get(key), str) or not project[key].strip():
                raise ValueError(f"Missing project field: {key}")
        for key in ("id", "accent", "visual"):
            if not IDENTIFIER.fullmatch(project[key]):
                raise ValueError(f"Invalid project {key}: {project[key]}")
        if project["id"] in identifiers or project["href"] in destinations:
            raise ValueError("Duplicate project identifier or destination")
        identifiers.add(project["id"])
        destinations.add(project["href"])
        if not valid_destination(project["href"]) or not valid_destination(project["source"], local=False):
            raise ValueError(f"Invalid destination for {project['id']}")
    return projects


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.resources = []
        self.stylesheets = []
        self.cards = []
        self.structured = []
        self._articles = []
        self._heading = None
        self._link = None
        self._json = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "article":
            card = None
            if "data-project" in attrs:
                card = {"id": attrs["data-project"], "headings": [], "links": []}
                self.cards.append(card)
            self._articles.append(card)
        card = next((item for item in reversed(self._articles) if item is not None), None)
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = {"tag": tag, "text": [], "card": card}
        if tag == "a":
            self._link = {"href": attrs.get("href", ""), "text": []}
            self.links.append(self._link)
            if card is not None:
                card["links"].append(self._link)
        if tag in ("img", "script", "source") and attrs.get("src"):
            self.resources.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.resources.append(attrs["href"])
            if "stylesheet" in attrs.get("rel", "").split():
                self.stylesheets.append(attrs["href"])
        if tag == "meta" and (attrs.get("property") == "og:image" or attrs.get("name") == "twitter:image"):
            self.resources.append(attrs.get("content", ""))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json = []

    def handle_endtag(self, tag):
        if tag == "article" and self._articles:
            self._articles.pop()
        if self._heading and tag == self._heading["tag"]:
            if self._heading["card"] is not None:
                self._heading["card"]["headings"].append(" ".join("".join(self._heading["text"]).split()))
            self._heading = None
        if tag == "a":
            self._link = None
        if tag == "script" and self._json is not None:
            self.structured.append(json.loads("".join(self._json)))
            self._json = None

    def handle_data(self, data):
        if self._heading:
            self._heading["text"].append(data)
        if self._link is not None:
            self._link["text"].append(data)
        if self._json is not None:
            self._json.append(data)


def objects(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from objects(item)


def local_path(url, root, relative_to):
    """Resolve same-site links without allowing a reference outside the output."""
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        if (parsed.scheme, parsed.netloc) != ("https", "arbiterforge.com"):
            return None
    path = unquote(parsed.path)
    target = (root / path.lstrip("/")) if path.startswith("/") else (relative_to.parent / path if path else relative_to)
    target = target.resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Reference escapes the published site: {url}")
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        raise ValueError(f"Missing local destination: {url}")
    return target


def verify(output):
    root = output.resolve()
    home = root / "index.html"
    source = home.read_text(encoding="utf-8")
    if "{%" in source or "{{" in source or source.startswith("---"):
        raise ValueError("Homepage contains unrendered Jekyll content")
    page = Page()
    page.feed(source)
    if len(page.ids) != len(set(page.ids)):
        raise ValueError("Homepage has duplicate HTML identifiers")

    projects = validate_projects(json.loads((ROOT / "_data/projects.json").read_text(encoding="utf-8")))
    if len(page.cards) != len(projects) or {card["id"] for card in page.cards} != {p["id"] for p in projects}:
        raise ValueError("Rendered project cards do not match project data")
    for project in projects:
        card = next(card for card in page.cards if card["id"] == project["id"])
        if project["name"] not in card["headings"]:
            raise ValueError(f"Missing rendered project title: {project['id']}")
        for href in (project["href"], project["source"]):
            if href not in {link["href"] for link in card["links"]}:
                raise ValueError(f"Missing rendered destination for {project['id']}: {href}")
        if not any(link["href"] == project["href"] and project["action"] in " ".join("".join(link["text"]).split()) for link in card["links"]):
            raise ValueError(f"Missing descriptive project action: {project['id']}")

    destinations = {link["href"] for link in page.links}
    for required in ("/news/", "/SIM/", "https://codearbiter.dev/", "https://github.com/SUaDtL"):
        if required not in destinations:
            raise ValueError(f"Homepage is missing a required destination: {required}")
    people = [item for item in objects(page.structured) if item.get("@type") == "Person" or "Person" in item.get("@type", [])]
    if not any(person.get("name", "").casefold() == "suadtl" for person in people):
        raise ValueError("Homepage lacks the suadtl Person identity in JSON-LD")

    parsed_pages = {home: page}
    for link in page.links:
        href = link["href"]
        if not href or urlsplit(href).scheme.lower() in ("javascript", "data"):
            raise ValueError(f"Empty or unsafe homepage link: {href}")
        target = local_path(href, root, home)
        fragment = unquote(urlsplit(href).fragment)
        if target is not None and fragment:
            if target not in parsed_pages:
                target_page = Page()
                target_page.feed(target.read_text(encoding="utf-8"))
                parsed_pages[target] = target_page
            if fragment not in parsed_pages[target].ids:
                raise ValueError(f"Broken homepage anchor: {href}")
    for url in page.resources:
        local_path(url, root, home)
    for url in page.stylesheets:
        stylesheet = local_path(url, root, home)
        if stylesheet is not None:
            for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", stylesheet.read_text(encoding="utf-8")):
                local_path(match[2], root, stylesheet)
    print(f"Homepage output OK: {len(projects)} project cards, personal identity, destinations, anchors and local assets")


if __name__ == "__main__":
    verify(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
