# Site review — Sol (GPT-5.6), 2026-08-03

Reviewer: Sol. Verdict: **changes required before publish.** Recorded verbatim below;
disposition notes maintained by Claude Code follow each section is NOT the case — the
review is untouched, dispositions tracked in `2026-08-03-site-review-dispositions.md`.

---

Review for Claude: arbiterForge site
Verdict: changes required before publish.
The site is polished and technically competent, but it does not yet earn the supplied skill's "$150k agency" claim. It reads as a careful implementation of a premium-SaaS recipe rather than a uniquely authored arbiterForge experience.

High-priority defects

The mobile menu covers its own close control.
.site-nav uses z-index:50, while .nav-overlay uses z-index:60: index.html:171, index.html:210.
I reproduced this in the browser: tapping the visible transformed X hits #navOverlay, leaving the menu open. Add a close button inside the overlay or deliberately elevate the toggle above it.

The mobile menu lacks modal focus management.
Opening it only changes classes and body overflow: index.html:449, index.html:658.
Focus is not moved into the menu, contained there, or restored. The obscured main page remains in the accessibility tree. Use inert on background regions, focus the first menu item, trap Tab/Shift+Tab, restore focus, and change the accessible label from "Open menu" to "Close menu."

Viewport changes can leave the entire page scroll-locked.
When the mobile menu is open and the viewport crosses to desktop, both overlay and toggle become display:none, but nav-open and body.style.overflow="hidden" remain. I reproduced this directly.
Close/reset the menu through a matchMedia('(min-width:48rem)') change listener.

Major design shortcomings

This is mostly a codeArbiter product page, not an arbiterForge organization site.
The org-level hero immediately becomes one codeArbiter card, several codeArbiter feature cards, an arbiterIDE teaser, and a repeated slogan: index.html:480, index.html:502, index.html:575.
Visitors never receive a clear portfolio thesis explaining:
- What arbiterForge itself exists to do.
- How codeArbiter and arbiterIDE form one system.
- What the organization intends to build next.
- Why this approach differs from ordinary agent tooling.

"Proof before promise" is followed by promises, not proof.
Counts, hard refusals, nine phases, reviewer fleets, audit trails, and local-only enforcement are all presented as prose: index.html:516, index.html:519, index.html:542, index.html:561.
Show authentic evidence:
- A real blocked-commit transcript.
- A real audit-log excerpt.
- A nine-gate result with pass/fail states.
- A compact compatibility matrix.
- Direct "inspect the mechanism" links.
Another atmospheric illustration cannot substitute for this.

The supplied recipe is too visible in the result.
Floating glass nav, eyebrow pills, double bezels, bento cards, nested arrow islands, black/gold gradients, and identical fade-ups appear almost one-for-one from the skill: index.html:129, index.html:139, index.html:170, index.html:265.
The commit's transformation should be the organizing design principle—not generic bezels and pills. Let a hollow commit visibly travel through governance and resolve into a proven gold decision across the page.

Double bezels are over-applied.
Every bento item receives nearly identical shell/core materials and radii: index.html:267.
Repeating the signature treatment everywhere removes hierarchy. Reserve the strongest machined enclosure for the flagship and gate. Present secondary content as diagrams, open typography, evidence excerpts, or quieter surfaces.

The project grid is text-heavy and semantically flat.
Product and feature titles are spans or paragraphs rather than headings: index.html:515, index.html:542, index.html:579.
Use article and h3 structure. The linked codeArbiter card currently gets an enormous accessible name containing its complete description and refusal list; use concise aria-labelledby relationships.

Conversion stops before conviction is established.
The hero immediately pushes users to codeArbiter or GitHub, while the final manifesto has no CTA: index.html:484, index.html:591.
A stronger sequence would be:
See the gate work → inspect evidence → install codeArbiter / read architecture / view source

Implementation and performance defects

Reveal animations violate the skill's own performance rule.
Every desktop reveal animates filter:blur(8px): index.html:366.
Remove the filter transition. Use opacity and transform only, and reserve elaborate choreography for meaningful gate-state transitions.

JavaScript failure hides most of the page.
.reveal defaults to opacity:0; JavaScript is solely responsible for revealing content: index.html:366, index.html:641.
Content should be visible by default. Add a .js class early, hide only under that class, and reveal everything if IntersectionObserver is unavailable.

There is a responsive breakpoint hole at 767px.
Mobile ends at 47.9rem while desktop begins at 48rem: index.html:381, index.html:394.
At 767px I confirmed that the desktop nav and twelve-column grid remain active. Use complementary ranges.

The long eyebrow wraps awkwardly on mobile.
"Governed autonomy for serious repositories" becomes a two-line pill. Shorten the mobile label or stop treating long descriptive copy as a microscopic badge.

Asset-integration notes

These are pending integration issues, not fair criticisms of Claude's original generation:
- Wire og-image.png, use summary_large_image, and add OG width, height, type, and alt metadata.
- Wire hero-forge.webp with responsive object-position, explicit dimensions, a text-protection gradient, and eager/high-priority loading.
- Wire gate-phases.webp with explicit dimensions and lazy loading.
- Integrate logomark.svg, but create a separate rounded-tile optical favicon variant with thicker 16–32px details.
- The OG image's sampled corners are not the contracted #06080c; they are #000203, #752107, #4B2B08, and #020205.
- The hero is strong but generic because it omits the complete hollow-node → gate → filled-node motif. Add that as a crisp SVG/HTML overlay rather than generating another background.

Problems in the skill itself

Claude followed the skill closely, but the skill partly caused the generic result:
- The "variance mandate" conflicts with prescribing the same nav, bento, bezels, pills, eyebrows, and reveal system every time.
- It mandates blur-based entry animation, then prohibits blur on scrolling content.
- Requiring double bezels on every major surface destroys the hierarchy that premium design depends on.
- "No basic fallbacks" is poor engineering guidance; progressive enhancement and resilient fallbacks are desirable.
- The checklist rewards trope accumulation rather than brand-specific concept development.

What Claude got right

Keep these:
- Locally bundled premium fonts and no banned font families.
- Thin custom SVG iconography.
- Strong desktop composition and clean mobile reflow outside the 767px gap.
- No horizontal overflow at tested desktop or mobile sizes.
- Reduced-motion handling, skip link, and visible focus treatment.
- IntersectionObserver instead of scroll handlers.
- Backdrop blur restricted to fixed layers.
- Fixed, pointer-inert grain.
- No browser console warnings.
- Custom easing and restrained color palette.

I did not create more images. The existing hero already supplies the "strong background"; the next high-value visual is authentic product evidence, not more generated atmosphere. No repository files were modified during this review.
