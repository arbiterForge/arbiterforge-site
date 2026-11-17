# News theme review

Reviewed November 17, 2026, for [PR #34](https://github.com/arbiterForge/arbiterforge-site/pull/34).

## Design

News now shares the personal homepage's local Manrope and JetBrains Mono fonts,
cream and olive palette, and remembered light/dark appearance. Shared appearance
tokens live in `assets/theme.css`; `_includes/theme-head.html` loads them and the
existing theme controller for both the homepage and News.

The reading layout replaces the old gradients, neon category colors, oversized
statistics, and repeated conceptual illustrations. Stories use a numbered margin,
a bounded text column, labeled analysis, and plain source links. All four category
links are visible in a two-column grid on small screens. The archive is a date-led
index, with the existing recovery labels retained.

No edition data, coverage data, feed source, publishing workflow, or SIM source was
changed. Arbiter News remains the briefing name, under the personal suadtl header.

## Build evidence

- Reviewed code commit: `3a014c8f853c26fc72fcbc88b25ef4dd425eaabc`.
- [Successful Pages build](https://github.com/arbiterForge/arbiterforge-site/actions/runs/44178586701).
- Rendered artifact: `site-preview-2ceab0520195f2bc32e846f43f830229ed36b3d2`.
- Artifact ID: `14371830199`.
- ZIP SHA-256: `a79b20de0d95845489702ae56b69bd3de759ad692caf39e97034ed633403a5fb`.
- All 33 unit tests passed; News and public-claim workflows also passed.
- Both the homepage and News output checkers passed against the downloaded,
  hash-verified Jekyll artifact.
- Rendered checks covered 25 daily editions and 28 historical pages, including
  319 retained historical records and 92 recovered original texts.

The strengthened News checker compares visible article content and source links
with source-verified edition data, rather than relying on story counts. It also
checks category placement, tab/panel relationships, shared appearance assets, and
historical paragraphs and recovery labels. Deliberate missing-summary,
missing-source, broken-category-link, and missing-restored-paragraph mutations
were rejected during checker verification.

## Browser review

The unmodified CI output was served through the managed local preview. A separate
QA-only wrapper supplied responsive iframe widths; it is not in this repository
or the deployment.

| Area | Result |
| --- | --- |
| Latest edition, light and dark | Visually reviewed; source arrows use the shared SVG icons |
| Responsive widths | No horizontal overflow at nominal 320, 390, 768, and 1024 px widths, or the desktop browser width |
| Category navigation | Click selection, ArrowLeft/ArrowRight wrapping, Home/End, selected state, focus, and panel visibility passed |
| Direct category link | `/news/#panel-money` selected the Markets panel |
| No JavaScript | All four panels and all 12 current stories remained visible; appearance control stayed hidden |
| Shared appearance | Dark persisted from News to Home; switching Home to light persisted back to News |
| Skip link | First keyboard target was the skip link; Enter moved focus to `main` |
| Permanent edition | The visible link opened November 17 with the correct canonical URL and 12 stories |
| Archive index | 53 entries, reviewed on desktop and mobile |
| Restored historical page | September 24 retained 5 restored articles; provenance disclosure opened |
| Mixed historical page | September 29 retained 12 restored articles and 12 coverage-only records |
| Coverage-only historical page | October 1 retained 12 records and the missing-text disclosure; mobile had no overflow |
| Homepage | Shared-theme extraction retained its layout and three project cards |

Iframe content widths were 15 px narrower where the browser reserved a vertical
scrollbar. These are responsive browser checks, not physical-device certification.
Print panel visibility and paper colors were reviewed in the stylesheet; a native
print dialog was not exercised. Browser logs included extension-origin metadata
errors, so this review does not claim a completely empty browser console.

## Screenshots

- [Desktop](news-theme-desktop.jpg): masthead through the first complete story.
- [Mobile](news-theme-mobile.jpg): 390 × 844 viewport, introduction and all topics.
- [Mobile reading](news-theme-mobile-reading.jpg): story typography and analysis.
- [Dark](news-theme-dark.jpg): the same desktop view with dark appearance.
- [Archive](news-theme-archive.jpg): desktop archive index.

Review artifacts are excluded from the published site by `_config.yml`.
