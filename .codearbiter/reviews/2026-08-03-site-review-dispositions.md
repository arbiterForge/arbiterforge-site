# Dispositions — Sol site review, 2026-08-03

Companion to `2026-08-03-site-review-sol.md`. Every finding, what was done, by whom (Claude
Code, same date).

## High-priority defects

| Finding | Disposition |
|---|---|
| Overlay covers the toggle (z 50 vs 60) | **Fixed.** `.site-nav` raised to z-index 65, deliberately above the overlay (60) so the morphed X stays tappable; comment added at the rule. |
| No modal focus management | **Fixed.** Open: saves `activeElement`, focuses first overlay link, sets `inert` on `#main` + `footer`, swaps `aria-label` to "Close menu". Tab/Shift+Tab trapped among overlay links + toggle. Close: restores focus, removes inert. |
| Viewport crossing leaves scroll lock | **Fixed.** `matchMedia('(min-width: 48rem)')` change listener closes the menu (clears `nav-open`, body overflow, inert, focus). |

## Major design shortcomings

| Finding | Disposition |
|---|---|
| Product page, not an org site | **Accepted.** New `#system` section head carries the org thesis: why arbiterForge exists (trust at the commit), how codeArbiter and arbiterIDE form one system (plugin gates today → same gates in the IDE's tool-dispatch layer next), one policy core / one portable record. Nav renamed Evidence / System / Principles. |
| "Proof before promise" followed by promises | **Accepted.** New `#evidence` section directly after the hero: authentic replay of the shipped `pre-bash.py` hook blocking `git add -A` (verbatim from codeArbiter's `hook-proof.json`: BLOCKED [H-03], exit 2, command not executed, gate-events.log line, source sha256 `b2cf1a87…`), plus "inspect the mechanism" links to the hook source on GitHub and the faithful replay on codearbiter.dev. Compatibility matrix deferred — host list already stated on flagship card. |
| Recipe too visible; commit transformation should organize the design | **Accepted in part.** The hollow→gate→gold journey now structures the page: hero carries a crisp motif overlay (hollow node approaching the gate, ghost ring where the proven node will be), the evidence section is the gate holding, and `#principles` closes with the filled gold node crossing. Hero CTA sequence now runs see-it-work → inspect → install. A deeper bespoke redesign (abandoning the pill/bezel vocabulary entirely) was not taken — partial acceptance. |
| Double bezels over-applied | **Fixed.** Machined shell/core reserved for the flagship card, the gate card, and the evidence terminal. Audit / local / arbiterIDE demoted to quiet single-hairline surfaces (`.card-quiet`). |
| Text-heavy, semantically flat grid | **Fixed.** Cards are `article`s with `h3` headings. Linked cards (`codeArbiter`, `arbiterIDE`) use `aria-labelledby` pointing at their name heading, so accessible names are concise. |
| Conversion stops before conviction | **Fixed.** Hero primary CTA is now "See a gate hold" → `#evidence`; manifesto gains a closing CTA row ("Install codeArbiter" / "View the source"). |

## Implementation & performance

| Finding | Disposition |
|---|---|
| Blur in reveal animations | **Fixed.** Reveals are opacity + transform only. |
| JS failure hides the page | **Fixed.** `<html>` gets a `js` class from an inline head script; `.reveal` is hidden only under `.js`. IntersectionObserver absence reveals everything immediately. |
| 767px breakpoint hole | **Fixed.** Complementary range syntax: `(width < 48rem)` / `(width >= 48rem)`. |
| Eyebrow wraps awkwardly on mobile | **Fixed.** Hero eyebrow swaps to a short label ("Governed autonomy") below 48rem via paired spans. |

## Asset integration

| Finding | Disposition |
|---|---|
| Wire og-image.png | **Done.** `og:image` → png with width/height/type/alt meta; `twitter:card` → `summary_large_image`. Placeholder `og-image.svg` deleted. |
| Wire hero-forge.webp | **Done.** `<img>` with explicit 2400×1350, `loading="eager"`, `fetchpriority="high"`, `object-position: 72%` (66% mobile), and a two-axis text-protection gradient over the copy column. |
| Wire gate-phases.webp | **Done.** Explicit 1600×320, `loading="lazy"`, descriptive alt, in the gate card. |
| Integrate logomark.svg + thicker favicon tile | **Done.** Logomark geometry inlined in nav + footer (and referenced by JSON-LD). `assets/favicon.svg` rebuilt as a rounded-tile variant with thickened 16–32px details. |
| OG corners not #06080c | **Acknowledged, not blocking.** The OG image renders standalone in link unfurls; it never composites against page background. No regeneration requested. |
| Hero omits complete motif | **Fixed.** Crisp SVG motif overlay added at the hero's base (hollow node → gate → dashed ghost of the proven node). |

## Skill critique

**Recorded** (review file + Claude's persistent memory): variance-vs-recipe conflict, blur
mandate contradiction, bezel over-application, "no basic fallbacks" being poor engineering
guidance, checklist rewarding trope accumulation. Applied here as: progressive enhancement
restored, bezel hierarchy enforced, brand motif made the organizing principle.
