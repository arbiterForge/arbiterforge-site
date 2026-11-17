# Verification commands

Source-backed baseline, 2026-11-17. Static HTML/CSS/JS and bundled fonts; the
existing Pages Jekyll action renders news. Python tests use the standard library.

- Tests: `python -m unittest discover -s tests -v`.
- Syntax: `python -m compileall -q scripts tests`. No separate style linter,
  type checker or local Ruby toolchain is declared.
- Rendered news: `python tests/check_news_build.py _site` after the pinned
  actions/jekyll-build-pages action builds the complete source tree.
- Live SIM: `python scripts/check_sim_live.py <site-commit> <SIM-commit> <HTML-SHA256>`.
- Live news: `python tests/check_news_live.py <site-commit>`.
- Secrets: `gitleaks dir <staged-payload-directory> --redact --no-banner --exit-code 1`.
  Export every staged file to that private temporary directory first.

Coverage: no percentage tooling or threshold exists here. Use named behavioral
tests and negative cases for the changed boundary. Do not report unmeasured
percentages. Hosted Jekyll, PR CI and live receiving are separate from local tests.
