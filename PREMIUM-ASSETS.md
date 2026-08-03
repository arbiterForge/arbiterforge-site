# Premium asset slots

> **Status 2026-08-03: all four assets generated (by Sol / GPT-5.6) and wired in.**
> `og-image.png`, `hero-forge.webp`, `gate-phases.webp`, and `logomark.svg` are live;
> `favicon.svg` is the thickened tile variant of the logomark. This file is retained as
> the regeneration spec should any asset need to be redone.

Every slot below originally shipped a hand-authored SVG placeholder, flagged in-code with a
comment starting `🎨 PREMIUM-ASSET-SLOT`. Generate the assets described here and swap them
in per the instructions. Brand constants: void `#06080c`, gold `#f0b92f` (bright `#ffd568`,
gradient `#f3c958 → #d89920`), ember `#ed946d`, ink `#f6f7f9`. Motif: an unproven (hollow)
commit crosses a governed gate and leaves proven (filled gold). Never drop the motif.

## 1. OG / social share image (REQUIRED)
- **Placeholder:** `assets/og-image.svg` (most social scrapers ignore SVG og:images).
- **Generate:** 1200×630 PNG or WebP. Cinematic: OLED-black field with gold/ember mesh glow,
  the gate/fulcrum mark center-left catching molten forge light, wordmark `arbiterForge`
  (Space Grotesk, "Forge" gold), tagline "You decide. The gates enforce." in JetBrains Mono.
  Moody, minimal detail. Must survive a 200px-wide thumbnail.
- **Swap:** save as `assets/og-image.png`; in `index.html` update `og:image` + `twitter:image`
  and change `twitter:card` to `summary_large_image`.

## 2. Hero backdrop art
- **Placeholder:** faint oversized inline gate glyph inside `.hero-art` in `index.html`,
  over pure-CSS mesh orbs.
- **Generate:** ~2400×1350 WebP. Dark forge atmosphere: monumental gate posts + lintel
  emerging from black, molten-gold rim light, drifting ember sparks, heavy vignette to pure
  `#06080c` at every edge so it composites seamlessly. No text. Style sibling to
  codeArbiter's `hero-gates.webp`.
- **Swap:** place as an `<img>` inside `.hero-art` (absolute, `object-fit: cover`, opacity
  tuned ~0.35), delete the placeholder SVG.

## 3. Org logomark (optional, lower priority)
- **Placeholder:** `assets/favicon.svg` + the matching inline SVG in the nav and footer.
- **Generate:** professionally drawn arbiterForge mark: gate/fulcrum motif with a subtle
  forge/anvil inflection, gold gradient on dark. Deliver as SVG: a 64×64 tiled favicon
  variant and a plain no-tile variant for inline use.
- **Swap:** replace `assets/favicon.svg` 1:1; replace the inline nav/footer SVGs (structure
  is marked with `data-brand-element` attributes).

## 4. Nine-phase commit gate render (optional)
- **Placeholder:** flat 9-dot SVG phase strip in the "The gate" bento card.
- **Generate:** small premium isometric/dimensional render of a nine-phase gate: eight
  hollow stations resolving to one filled gold terminus, dark ground, gold accents.
  Roughly 5:1 aspect, transparent or `#0e141c` background.
- **Swap:** replace the `.phase-strip` SVG with the image inside the same card.
