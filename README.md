# arbiterforge-site

Organization landing page for **arbiterforge.com**.

Static site, no build step, zero external runtime requests: one `index.html` (inline CSS +
inline JS) plus locally bundled OFL-licensed fonts (Space Grotesk, Manrope, JetBrains Mono;
license texts in `assets/fonts/`). Published to GitHub Pages from the default branch;
`CNAME` binds the custom domain.

Brand tokens (void/gold surfaces, gate motif, Manrope/JetBrains Mono) are shared with the
codeArbiter documentation site so the family reads as one system.

Placeholder art slots awaiting generated premium assets are indexed in
[`PREMIUM-ASSETS.md`](PREMIUM-ASSETS.md) and flagged in-code with `🎨 PREMIUM-ASSET-SLOT`.
