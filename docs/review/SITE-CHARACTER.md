# Site character review

Review record for [PR #35](https://github.com/arbiterForge/arbiterforge-site/pull/35),
November 17, 2026.

**Status:** source review, the Pages build, and the browser checks recorded below
passed. The responsive and visual review required no further layout fixes.

## Scope

This pass adds visual character across the personal site while keeping the shared
suadtl typography, palette, and remembered light/dark appearance.

- **Home:** an original layered SVG studio illustration, a more distinct Projects
  section, topic symbols, and an illustrated notebook link to the archived essay.
- **News:** compact studio artwork, topic symbols, numbered section headings,
  clearer story grouping, and a date-led archive divided into daily editions and
  historical records.
- **Archived essay:** a full editorial layout using the shared theme, a compact
  gate illustration, numbered sections, a contents rail, and a bounded reading
  column. The former inline styling and reveal script are removed.
- **Shared enhancements:** finite artwork and heading entry effects, small
  pointer and hover responses, a remembered motion control, and a reading-position
  rule on daily News, historical News, and the essay.

The SVG artwork and icons are repository-owned assets. The shared theme include
loads the new artwork stylesheet and optional motion controller consistently.

## Preserved contracts

- The site remains a personal suadtl home with codeArbiter linked to
  `codearbiter.dev`, SIM under Projects, and News at `/news/`. Project content and
  destinations still come from `_data/projects.json`.
- Existing News edition data, source links, dates, analysis labels, recovery
  disclosures, coverage records, RSS behavior, and publication workflows are not
  modified. The template changes add presentation wrappers and symbols around the
  existing content fields.
- News category IDs, fragment links, panel relationships, and the existing
  category controller are retained. Daily and historical material remain clearly
  distinguished in the archive.
- The essay keeps its archive caveat, original body wording, source links, and
  current product-documentation link. Its `main` anchor is retained; the new
  contents links point to unique section IDs.
- SIM source and its publication contract are outside this change.
- Review documents and screenshots remain excluded from the published site by
  `_config.yml`.

## Source-reviewed accessibility and motion

These findings come from HTML, CSS, and JavaScript inspection. They are not a
substitute for the browser results below.

- Content and artwork are visible without JavaScript. Entry effects translate
  elements without an initially hidden or transparent text state. Motion and
  replay controls remain hidden until their controller is available.
- System `prefers-reduced-motion` overrides a saved motion-on preference. The
  footer control reports that state and is disabled while the system preference
  applies.
- A user's motion choice is stored under `suadtl-motion` when storage is available.
  Storage access is guarded, so a storage failure does not block the page.
- Turning motion off removes entry and artwork animation classes, cancels queued
  artwork pointer frames, and resets pointer offsets. Spatial hover effects apply
  only when `data-motion="on"`; reduced-motion and off styles suppress remaining
  animation and transitions.
- Artwork entry animations are finite. Pointer movement is limited to devices
  reporting both hover and a fine pointer, is bounded to small offsets, and is
  scheduled through `requestAnimationFrame`.
- Decorative artwork, symbols, duplicate date numerals, and the reading-position
  rule are hidden from assistive technology. Motion buttons expose their state
  through `aria-pressed`; the replay action has a text label.
- The existing skip links, focusable `main` targets, semantic headings, native
  links, and appearance controls remain. Small-text contrast on the homepage
  Projects band and archive historical band was corrected during source review.
- IntersectionObserver can reveal category headings when their News panel is
  displayed. ResizeObserver recalculates the reading-position rule after content
  height changes; scroll and resize updates are batched in animation frames.
- Print styles hide motion controls, replay actions, and the reading-position
  rule. The essay includes print and forced-colors adaptations.

No concrete blocker remained at the end of the combined source review.

## Confirmed source checks

- `node --check assets/motion.js` passed.
- `git diff --check` passed before the application commit.
- A one-off HTML-parser comparison of the original and redesigned essay confirmed
  that all 29 original non-eyebrow paragraphs, all 6 section headings, and all 39
  article links retained their text or destinations and their original order.
- The essay's local fragment links resolved to unique IDs.
- Inspection confirmed that every spatial hover transform in the changed shared,
  homepage, News, and essay styles is gated on motion being enabled.

The paragraph and link comparison is a content-preservation check, not a browser
or assistive-technology test. No additional unit-suite result is asserted here
without its execution evidence.

## CI build evidence

- Application commit: `cb82246849ce3f54431164d9ee17d0cec4613712`.
- [Successful Pages build](https://github.com/arbiterForge/arbiterforge-site/actions/runs/44183506228).
- Run ID: `44183506228`.
- Rendered artifact ID: `14373212471`.
- ZIP SHA-256: `cc45cf909ccfa5c472c9877409be8b240fc3aeaca680bd67b672c2a8b20bdc1e`.
- Exact extracted output supplied for browser review:
  `/workspace/scratch/321fb1ac161c/site-character-rendered`.

The primary reviewer supplied the green build result, artifact identity, and
browser observations below. Browser review used this unmodified CI output.

## Browser verification

The unmodified CI artifact was served through the managed preview. Responsive
checks used iframe viewports at 320 × 740, 390 × 844, 768 × 1024, and 1024 × 768
CSS pixels for each of Home, News, the archive index, and the essay.

All 16 page/viewport combinations had no horizontal overflow. Their content
widths were 305, 375, 753, and 1009 pixels because the browser reserved 15 pixels
for the vertical scrollbar. The desktop page root measured 1363 pixels wide with
the same 1363-pixel `scrollWidth`. These are responsive browser checks, not
physical-device certification.

| Area | Result |
| --- | --- |
| Desktop visual review | Full Home screenshot, the first 1600 pixels of News, the first 1300 pixels of the archive, and the first 1500 pixels of the essay inspected |
| Mobile visual review | Full Home at 390 pixels, News at 320 and 390 pixels, and the essay at 390 pixels inspected; layouts were clean and needed no fixes |
| Home without JavaScript | Sandboxed preview retained all 3 project cards and the artwork; Replay and Motion controls stayed hidden |
| News without JavaScript | All 4 category panels had computed `display: block` and `hidden: false`; all 12 story headings remained present |
| News keyboard category navigation | ArrowRight from `#tab-ai` activated `#tab-cloud`; only `#panel-cloud` remained visible |
| Motion off | Removed `art-running` and artwork CSS offsets, and disabled Replay |
| Motion preference persistence | Turning motion off on Home persisted when navigating to News, where `data-motion` remained `off` |
| Artwork replay | Computed paper-layer animation durations were 1.8, 2.0, and 2.2 seconds; trace effects were 2.8 and 0.6 seconds; iteration counts were 1 |
| Artwork pointer response | Real pointer movement set `--art-x: 2.84px` and `--art-y: -1.03px`, with corresponding transforms on all 3 layers |
| Appearance persistence | Dark appearance selected on the essay persisted when navigating to Home |
| Essay contents and reading position | The Enforcement link set `#enforcement`, placed the target 63.9 pixels from the viewport top, and updated reading progress to `0.4268` |

System reduced motion remains source-reviewed only: native browser emulation was
unavailable. Print and forced-colors behavior were reviewed in the stylesheets;
this record does not assert a browser exercise of either mode.

## Screenshots

Screenshots from the identified CI artifact:

- [Home](site-character-home.jpg): full desktop homepage.
- [Home preview](site-character-home-preview.jpg): desktop preview.
- [Home mobile](site-character-home-mobile.jpg): full homepage at the 390-pixel
  review viewport.
- [Home dark](site-character-home-dark.jpg): homepage with dark appearance.
- [News](site-character-news.jpg): desktop introduction and reading layout.
- [News mobile](site-character-news-mobile.jpg): mobile briefing layout.
- [Archive](site-character-archive.jpg): desktop archive index.
- [Essay](site-character-essay.jpg): desktop editorial layout.
