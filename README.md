# arbiterforge-site

Organization landing page for **arbiterforge.com**.

Static site, zero external runtime requests: one `index.html` (inline CSS +
inline JS) plus locally bundled OFL-licensed fonts (Space Grotesk, Manrope, JetBrains Mono;
license texts in `assets/fonts/`). Published to GitHub Pages from the default branch;
`CNAME` binds the custom domain. The `ArbiterForge Pages` workflow uses the existing
GitHub Pages Jekyll toolchain for the home page and news, then includes the actual
standalone SIM application at **https://arbiterforge.com/SIM/** (`/SIM` redirects there).

## SIM publication

Main pushes publish the complete site. A scheduled Actions run checks SIM every
20 minutes (GitHub schedules can be delayed), with manual dispatch available.
An unchanged site commit and SIM source/digest skip the build and deployment.
`scripts/stage_sim.py` selects the latest successful `SUaDtL/SIM` main Pages run,
requires passing push CI for that exact source, and checks the public HTML's clean
build stamp, standalone resources and offline CSP. It copies those published bytes
unchanged, rather than rebuilding SIM or embedding another origin in an iframe.
This uses the stable public preview, so seven-day CI artifact expiry does not break
future news publications. An upstream mismatch or failed check prevents deployment;
the previous published site remains live.

`/SIM/publication.json` records the site commit, SIM commit, SHA-256 and upstream
CI/publication links. This is a main preview, not a versioned SIM release or native,
screen-reader or participant qualification. The app still keeps dataset work local.

Builds and pull requests have read-only repository permissions. Only the isolated
main deployment job has Pages and OIDC write permissions; no PAT or cross-repository
writer is needed. PR artifacts contain the full rendered preview. Post-deploy checks
receive exact SIM bytes and verify the existing news pages after Pages finishes.

The repository Pages setting must be **GitHub Actions** (`build_type: workflow`),
with the existing `arbiterforge.com` custom domain retained. To roll back, redeploy
a previous good artifact or restore legacy Pages from main; legacy mode excludes
the generated SIM path but continues to build the source-controlled site/news.

Brand tokens (void/gold surfaces, gate motif, Manrope/JetBrains Mono) are shared with the
codeArbiter documentation site so the family reads as one system.

Placeholder art slots awaiting generated premium assets are indexed in
[`PREMIUM-ASSETS.md`](PREMIUM-ASSETS.md) and flagged in-code with `🎨 PREMIUM-ASSET-SLOT`.

## Product claims

Current codeArbiter installation, compatibility, release and policy facts are
linked to their product-owned sources rather than copied into a second catalog.
Historical proof captures retain their original identities and remain labeled.
This site change does not qualify a package or change any product maturity label.

Run `python -m unittest discover -s tests -v` for the source-contract regressions.
The workflow checks wording and owner links, not live host behavior or legal scope.
