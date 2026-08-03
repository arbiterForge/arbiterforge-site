# Image generation briefs — arbiterforge.com

Instructions for generating the premium art assets for the arbiterForge org landing page.
Each brief below is self-contained: give the generator the prompt as written, then save the
output to the exact path listed. After saving, follow the "Wire-in" note (or hand it back to
Claude Code to wire in).

## Shared brand language (applies to every image)

- **Palette:** void black `#06080c` (backgrounds must resolve to this exact hex at the
  edges), brand gold `#f0b92f`, bright gold `#ffd568`, gold gradient `#f3c958 → #d89920`,
  deep gold `#9b6811`, ember orange `#ed946d` (sparingly), slate line-gray `#465565`,
  muted gray-blue `#91a0b2`.
- **Motif (never drop it):** a horizontal "commit line" on which a hollow, unfilled dot
  (an unproven commit) approaches a monumental gate — two upright posts topped by a
  lintel/beam, with a small downward chevron or fulcrum above — and leaves on the far side
  as a solid, filled gold dot (a proven decision). The gate is the brand; gold means
  decision/proof.
- **Mood:** premium, cinematic, restrained. Dark forge atmosphere — think machined metal,
  molten rim light, deep shadow. NOT: busy sci-fi, neon cyberpunk, glossy 3D plastic,
  lens flares, text of any kind (unless the brief explicitly includes text).

---

## 1. OG / social share image — REQUIRED (highest priority)

- **Save to:** `assets/og-image.png`
- **Size / format:** exactly 1200 × 630, PNG (or WebP if the pipeline prefers; PNG is safest
  for scrapers).
- **Prompt:**
  > A 1200×630 social-share banner. Near-black background (#06080c) with a soft radial
  > golden glow rising from the lower left and a faint ember-orange bloom in the upper
  > right — subtle, moody, no banding. Left-of-center: a minimal geometric emblem of a
  > gate — two vertical gold posts (#f0b92f, gradient toward #d89920 at the base) topped
  > by a horizontal gold beam, with a small gold chevron floating above — standing on a
  > thin horizontal gray line (#465565) that runs the width of the image. On the line, to
  > the left of the gate, one small hollow circle outlined in gray; to the right of the
  > gate, one small solid gold circle. The emblem catches warm forge light with a gentle
  > rim glow. Right of the emblem, set in clean type: the wordmark "arbiterForge" — the
  > word "arbiter" in off-white (#f6f7f9), the word "Forge" in gold (#f0b92f), in a modern
  > geometric grotesk (Space Grotesk-like). Below it, smaller, in a monospaced font, in
  > gold: "You decide. The gates enforce." Composition must stay bold and legible when
  > shrunk to a 200px-wide thumbnail. No other text, no logos, no watermark.
- **Wire-in:** in `index.html` change the two meta tags `og:image` and `twitter:image` from
  `assets/og-image.svg` to `assets/og-image.png`, and change `twitter:card` from `summary`
  to `summary_large_image`. The placeholder `assets/og-image.svg` can then be deleted.

## 2. Hero backdrop art

- **Save to:** `assets/hero-forge.webp`
- **Size / format:** 2400 × 1350 (16:9), WebP, quality ~80 (target ≤ 300 KB).
- **Prompt:**
  > A dark, cinematic wide establishing image, 2400×1350. Out of near-total blackness
  > (#06080c), a monumental minimalist gate emerges right-of-center: two colossal vertical
  > posts and a horizontal lintel beam, forms simple and geometric like machined obsidian
  > monoliths. The gate's inner edges catch molten-gold rim light (#f0b92f into #ffd568 at
  > the hottest points), as if lit by an unseen forge below. A few faint ember sparks
  > (#ed946d) drift upward near the base — sparse, small, subtle. A thin, barely-visible
  > horizontal line of light passes through the gate at ground level. Heavy vignette: every
  > edge and corner of the frame fades to pure #06080c so the image composites seamlessly
  > onto a matching page background. Atmosphere over detail — deep shadow, restrained
  > highlights, no fog banks, no stars, no people, no text, no watermark.
- **Wire-in:** in `index.html`, inside the `<div class="hero-art">` (flagged with a
  🎨 PREMIUM-ASSET-SLOT comment), replace the placeholder `<svg>` with
  `<img src="assets/hero-forge.webp" alt="" loading="eager" decoding="async">` and add CSS
  `.hero-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.35}`
  (tune opacity so the headline stays dominant).

## 3. Org logomark (optional — lower priority)

- **Save to:** `assets/logomark.svg` (vector strongly preferred; if the generator can only
  produce raster, save `assets/logomark.png` at 1024×1024 and note it needs vectorizing).
- **Prompt:**
  > A minimal vector logomark for "arbiterForge," a company that builds enforcement gates
  > for AI coding agents. The mark: a stylized gate — two upright posts and a lintel beam
  > in a gold gradient (#f3c958 to #d89920) — standing on a thin horizontal baseline
  > (#465565). On the baseline, left of the gate, a small hollow outlined circle; right of
  > the gate, a small solid gold circle. Above the lintel, a small downward-pointing
  > chevron in bright gold, evoking both a terminal prompt and a scale's fulcrum. Very
  > subtle forge/anvil weight to the silhouette: the posts may thicken slightly at the
  > base like anvil feet. Flat vector style, crisp geometry, no gradients other than the
  > gold, works at 16px favicon size, on a near-black background (#06080c). Two
  > deliverables if possible: the bare mark, and the mark centered on a rounded-square
  > dark tile. No text.
- **Wire-in:** replace `assets/favicon.svg` (keep the rounded-tile version there) and the
  two inline SVG marks in `index.html` (nav brand + footer wordmark — both structured with
  `data-brand-element` attributes for a 1:1 swap).

## 4. Nine-phase commit gate strip (optional)

- **Save to:** `assets/gate-phases.webp`
- **Size / format:** 1600 × 320 (5:1 strip), WebP, transparent background preferred —
  otherwise solid `#0e141c`.
- **Prompt:**
  > A wide 5:1 dimensional illustration of a nine-station gauntlet, dark and premium.
  > A thin metallic track runs left to right across a near-black field (#0e141c). Along
  > it, eight evenly spaced small stations rendered as hollow, unlit rings of dark
  > gunmetal with faint gray edge light (#91a0b2) — and at the far right, a ninth, final
  > station: a solid, glowing gold node (#f0b92f with a warm #ffd568 core) beneath a small
  > gold gate (two miniature posts and a beam). Subtle depth: soft isometric perspective
  > or gentle top-down light, restrained reflections on the track. The story reads
  > left-to-right as "unproven until the last gate." No text, no people, minimal glow, no
  > lens flares.
- **Wire-in:** in `index.html`, in the "The gate" bento card (flagged with a
  🎨 PREMIUM-ASSET-SLOT comment), replace the `.phase-strip` placeholder `<svg>` with
  `<img class="phase-strip" src="assets/gate-phases.webp" alt="" loading="lazy">`.
