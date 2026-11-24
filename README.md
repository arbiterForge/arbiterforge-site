# suadtl at arbiterforge.com

A personal home for the things I build: developer tools, infrastructure projects,
and browser experiments. The site links to [codeArbiter](https://codearbiter.dev/),
hosts [Service Integration Map](https://arbiterforge.com/SIM/), links to
[singedTerra](https://suadtl.github.io/singedTerra/), and publishes
[Arbiter News](https://arbiterforge.com/news/).

The domain and repository name remain `arbiterforge.com` and
`arbiterForge/arbiterforge-site`. The homepage represents **suadtl**.

## Site structure

| Path | Purpose |
| --- | --- |
| `index.html` | Personal homepage; Jekyll renders its project list |
| `lab/index.html` | Generative Studio, a seeded interactive sculpture at `/lab/` |
| `assets/generative-studio.*` | Shared procedural animation and studio controls |
| `_data/projects.json` | Project names, descriptions, links, and display choices |
| `_includes/project-card.html` | Shared project card markup |
| `assets/` | Locally served styles, artwork, icons, and fonts |
| `news/` | News routes, publishing instructions, feed, and shared assets |
| `_data/arbiter_news/` | Current editions and preserved historical records |
| `_layouts/arbiter-news*.html` | News and historical archive layouts |
| `scripts/stage_sim.py` | Receives the verified public SIM application for deployment |
| `scripts/check_home_build.py` | Checks the rendered homepage and its destinations |

The site uses the existing GitHub Pages Jekyll toolchain. Project cards and News
content render at build time; visitors do not need JavaScript to follow project
links or read the briefing. Fonts are bundled locally with their license texts
under `assets/fonts/`.

The homepage defaults to a light appearance. Its appearance button offers a dark
option and remembers the choice locally when browser storage is available.
Project navigation and content remain available with JavaScript disabled.

Each section has its own 1200×630 sharing image at `assets/social-*.png`, with
editable vector compositions under `assets/social/`. The native vector artwork
uses the same palette, typography, and contour forms as the site. It is not a
set of application screenshots. `scripts/generate_social_cards.py` regenerates
all eight cards offline with FontTools (including Brotli), Pillow, Inkscape,
the bundled Manrope/JetBrains Mono fonts, and Debian's `fonts-liberation` serif.
Text is outlined in the SVG output so the files render without installed fonts.
The build checks their dimensions, local URLs, alt descriptions, and size.

The singedTerra homepage project image comes from its public repository's
`docs/assets/current-battle-hud.jpg`. codeArbiter and SIM homepage previews are
source-grounded workflow and fictional network illustrations. Sharing artwork
and explanatory diagrams are not live application screenshots or test evidence.

## Generative Studio

The homepage draws three interactive contour sculptures (Weave, Orbit, and
Bloom) in Canvas2D, with matching static vector artwork when scripting or Canvas
is unavailable. The separate [playground](/lab/) renders kinetic geometry locally
from a seed, with Foundry, Filaments, Bloom, and Orbit systems. Visitors can
adjust movement and density, regenerate, pause, export a still, and share a seed
via URL. No external rendering service or third-party JavaScript is required.

The same motion preference applies across pages. System reduced-motion, Save-Data, hidden tabs, and offscreen observation suspend animation. Canvas resolution and frame rate are bounded. The homepage samples fewer curve points, then fewer contours, when consecutive frames show sustained rendering pressure; paused artwork always uses full detail. Form and pulse controls briefly yield the canvas so their feedback can paint promptly. Keep the base artwork and semantic links available if JavaScript or Canvas is unavailable. Run `tests/test_generative_studio.py` alongside the existing tests.

## Add or update a project

Edit `_data/projects.json`. Array order determines display order. Every entry has
these fields:

| Field | Value |
| --- | --- |
| `id` | Unique lowercase identifier, using letters, numbers, and hyphens |
| `name` | Project name as it should appear on the site |
| `kind` | A short category, such as `Developer tooling` or `Browser game` |
| `description` | A plain-language description of what someone can do with it |
| `href` | The working destination: an HTTPS URL or a site-root path such as `/SIM/` |
| `action` | Descriptive link text, such as `Open SIM` |
| `source` | An HTTPS link to the project's source repository |
| `accent` | A visual accent: `olive`, `blue`, or `clay` |
| `visual` | `codearbiter`, `sim`, `singedterra`, or `generic` for a new project |

Use a real destination that is ready to visit. Leave unpublished ideas out of the
public list until they have a useful destination. Adding a linked project does
not require changing the homepage layout or adding another deployment.

To host a new static project here, add its published files under a distinct
directory with an `index.html`, then use that directory's path in `href`.
Check its asset paths and verify the rendered output before publishing. Reserve
`/news/` for the briefing and `/SIM/` for the existing SIM publication pipeline.
A separate repository can remain independently hosted and use its HTTPS URL.

## Build and preview

The `ArbiterForge Pages` workflow builds a complete preview on pull requests. It
runs the source checks, renders Jekyll, receives SIM, and checks the composed
output. Download its `site-preview-<commit>` artifact to inspect the same site
that would be published. Serve the extracted directory with an HTTP server, for
example:

```sh
python -m http.server 8000 --directory /path/to/extracted-preview
```

Open `http://localhost:8000/`. Opening `index.html` directly as a file does not
resolve the site's root-relative links correctly. Serving the source checkout
without Jekyll also leaves Liquid unrendered and does not include generated SIM.

Run source checks from the repository root:

```sh
python -m unittest discover -s tests -v
```

After Jekyll has rendered the site and SIM has been composed into `_site/SIM/`,
validate the complete output:

```sh
python scripts/check_home_build.py _site
python tests/check_news_build.py _site
python tests/check_metadata_build.py _site
```

The homepage check validates project titles and destinations, personal metadata,
internal anchors, and local assets in the actual HTML. The News check verifies
latest and dated editions, the archive, coverage records, and RSS. Check the
homepage on mobile and desktop and use its links before publishing. Do not commit
generated `_site/` output.

## Sharing and discovery

`_includes/page-meta.html` owns canonical URLs, descriptions, Open Graph,
Twitter cards, and structured data. Standalone pages set their title,
description, `social_image`, and `social_image_alt` in front matter; shared
layouts pass the equivalent values. The structured identity is a person and a
personal website. News editions and historical records do not invent newsroom
or publication-time claims.

The generated `sitemap.xml` lists the canonical site pages, including `/news/`
and each dated edition. New standalone pages opt in with `sitemap: true`;
News and showcase layouts are included automatically. `robots.txt` advertises
the sitemap. The custom 404 provides useful destinations and is marked
`noindex`. SIM keeps the metadata delivered by its independent publication.

Browser regression and mobile laboratory checks are documented in
[`tests/browser/README.md`](tests/browser/README.md). The browser job uses the
exact composed preview and gates every changed deployment, including scheduled
SIM refreshes. An unchanged polling run skips the build and browser suite.
Baselines are reviewed assets, not automatically accepted screenshots. These
checks measure a throttled Chromium mobile profile; they do not replace a
physical-phone run or field Core Web Vitals collected from real visitors.

## SIM publication

Main pushes publish the complete site. A scheduled Actions run checks SIM every
10 minutes; GitHub schedules can be delayed. Manual dispatch is also available.
An unchanged site commit and SIM source/digest skip the build and deployment.
`scripts/stage_sim.py` selects the latest successful `SUaDtL/SIM` main Pages run,
requires passing push CI for that exact source, and checks the public HTML's clean
build stamp, standalone resources, and offline CSP. It copies those published
bytes unchanged. It does not rebuild SIM or embed another origin in an iframe.
Using the stable public preview avoids dependence on expiring CI artifacts.
An upstream mismatch or failed check prevents deployment; the previous published
site remains live.

Jekyll builds the homepage and News first. The workflow then installs the received
SIM HTML at `_site/SIM/index.html`; GitHub Pages provides the `/SIM` to `/SIM/`
directory redirect. `/SIM/publication.json` records the site commit, SIM commit,
SHA-256, and upstream CI/publication links. This is a main preview, not a versioned
SIM release or native, screen-reader, or participant qualification. SIM keeps
dataset work local.

Builds and pull requests have read-only repository permissions. Only the isolated
main deployment job has Pages and OIDC write permissions; no PAT or cross-repository
writer is needed. Post-deploy checks receive the exact SIM bytes and verify News
after Pages finishes. Keep the workflow name `ArbiterForge Pages`: the separate
News live-verification workflow listens for that name.

The repository Pages setting must be **GitHub Actions** (`build_type: workflow`),
with the existing `arbiterforge.com` custom domain retained in `CNAME`. To roll
back, redeploy a previous good artifact. Restoring legacy Pages from main can
serve the source-controlled site and News, but omits the generated SIM path.

## News and historical material

Follow [the News guide](news/README.md) and
[publishing contract](news/PUBLISHING.md) for daily editions. Keep editorial data,
archive dates, feed addresses, and coverage history independent of homepage
design changes. The old `why-hard-gates.html` essay and proof captures retain
their URLs for existing readers; current codeArbiter details belong on
[codearbiter.dev](https://codearbiter.dev/).

## Meridian publication

[Meridian](https://arbiterforge.com/Meridian/) follows the same receiving workflow as
SIM. It also keeps its [independent Pages preview](https://suadtl.github.io/Meridian/).
Meridian's successful main Pages run includes its source, browser, visual and
artifact checks. The site matches that run to the public `build.json` receipt and
verifies the SHA-256 and byte count of every listed file. GitHub Pages supplies the
`/Meridian` to `/Meridian/` directory redirect. Other capitalizations of the
Meridian entry route, including `/meridian`, open `/Meridian/` and preserve
the query string and fragment in browsers with JavaScript enabled.

The site copies the verified split build into `_site/Meridian/` after Jekyll.
The app keeps its relative asset URLs and local-only content policy.
`/Meridian/publication.json` records the source and site commits, manifest digest
and upstream workflow run. Meridian has one source of releases: push to
`SUaDtL/Meridian` on `main`. The consumer reads the live upstream build stamp
and requires a successful Pages publication for that exact commit before copying
the release. Users can stay on `arbiterforge.com/Meridian/` across releases,
including when reopening projects stored in their browser. The shared 10-minute schedule publishes when either
app changes. The composed preview must pass browser checks before deployment,
and the receiving job checks the actual public paths and hashes.
