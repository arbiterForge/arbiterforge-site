# Browser quality checks

These checks run against the complete Jekyll artifact, after the existing SIM publication checks. Nothing under this directory is shipped to the public site. JavaScript production pages remain buildless and have no new dependencies.

## What is checked

- Nine core routes at 320, 768 and 1440 CSS pixels: successful loads, one main heading, canonical addresses, no horizontal overflow or script/asset errors.
- axe-core WCAG A/AA checks, including detectable text contrast, for both appearances at 320 and 1440 pixels on every core route. Automated checks do not replace keyboard, screen-reader or visual review.
- Actual keyboard navigation for the skip link, sculpture controls, project examples and News tabs; theme persistence, reduced motion, no-script fallback, seed links and a real 404 response.
- Fifteen reviewed viewport and project-section screenshots, rendered by pinned Chromium. Motion is disabled through the site's own preference, local fonts are loaded, and the News screenshots use an immutable edition address. The newest edition still gets functional and accessibility checks. Whole-project-section captures preserve the selected width and use a viewport at least as tall as the section, avoiding fixed-element artifacts from capturing beyond the viewport; no interface elements are masked or hidden.
- Three cold 390×844 mobile browser laboratory runs with touch input, 4× CPU slowdown relative to the CI runner, 150 ms network latency and 1.6 Mbps download. The report records LCP, CLS, observed interaction duration, long tasks and resource sizes. The animated hero stays enabled while changing its form and sending a pulse. Playwright tracing and screenshots are disabled only for these timing trials to avoid recorder overhead; each completed trial and a final diagnostic journal are attached even when a later step fails. A small CDP binding streams early observer values and a once-per-second timer/hero-state heartbeat into a Node-side progress file, preserving evidence if a renderer call later stalls. This probe is test-only and sends no visitor data anywhere.

Performance budgets are median LCP ≤2500 ms, no LCP sample >4000 ms, CLS ≤0.1 and no observed scripted interaction >200 ms. See [Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds). These are regression signals for this laboratory configuration, **not** physical-phone measurements, an accessibility certification, field INP or the site's real-user 75th percentile. Event Timing does not report durations below 16 ms. No analytics or visitor telemetry is added.

## Running checks

Use Node 22.12+ and `npm ci --ignore-scripts` in this directory. Run with Playwright **1.64.1** and its Chromium build. CI uses `mcr.microsoft.com/playwright:v1.64.1-noble` so browser, OS and font rendering remain consistent.

`npm test` serves the composed repository `_site/` on a loopback port. Set `SITE_ROOT` to a different built output directory when needed. Set `SITE_BASE_URL` to an already running preview URL to reuse it without starting a server. In a managed Sites workspace, start its supported `sites-preview` and use the exact returned URL through `SITE_BASE_URL`.

The Pages workflow runs browser checks whenever the composed output changes, including changes discovered by the existing twenty-minute SIM polling schedule. Publishing on main always requires their success. Unchanged scheduled polls skip the Jekyll build, browser checks and deployment. A scheduled run cannot bypass a failed check on a main-branch change. Browser checks never write back to the repository or update their own expected results.

## Reviewing intentional visual changes

Normal CI uses `updateSnapshots: 'none'`: a missing or different baseline fails. Download the `browser-quality-<commit>` artifact to inspect its Playwright report, expected/actual/diff images and accessibility/performance JSON attachments.

For an intentional design change, generate candidates with `npm run visual:update` in the **same pinned Playwright container** used by CI, against the exact newly built output. Inspect every changed image and commit only the approved files under `snapshots/`. Do not add `--update-snapshots` to normal CI. When a baseline is missing, an explicitly captured `candidate-<name>.png` is retained in `test-results/`, using the same target and screenshot options as the comparison. Inspect that candidate, then remove the `candidate-` prefix when promoting it to `snapshots/`. A generic `test-failed-1.png` is diagnostic and must not be used as a clipped section baseline. Run normal checks again after the review.

Keep Playwright's npm version and container tag synchronized. Changing either can change rendering; review the resulting baseline changes. See [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) and [Docker guidance](https://playwright.dev/docs/docker).
