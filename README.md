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

`assets/social-card.svg` is the editable social preview; `assets/social-card.png`
is its 1200×630 raster companion. Both use the bundled Manrope and JetBrains Mono
fonts. The singedTerra project image comes from its public repository's
`docs/assets/current-battle-hud.jpg`. Other project previews are decorative SVG
illustrations, not screenshots or test evidence.

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
```

The homepage check validates project titles and destinations, personal metadata,
internal anchors, and local assets in the actual HTML. The News check verifies
latest and dated editions, the archive, coverage records, and RSS. Check the
homepage on mobile and desktop and use its links before publishing. Do not commit
generated `_site/` output.

## SIM publication

Main pushes publish the complete site. A scheduled Actions run checks SIM every
20 minutes; GitHub schedules can be delayed. Manual dispatch is also available.
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
