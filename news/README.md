# Arbiter News

Public home: **https://arbiterforge.com/news/**
Archive: **https://arbiterforge.com/news/archive/**
Coverage index: **https://arbiterforge.com/news/coverage.json**
Feed: **https://arbiterforge.com/news/feed.xml**

This feature is additive to the ArbiterForge landing site. It uses the existing GitHub Pages/Jekyll branch build; no new hosting account, DNS change, external database, paid service, API credential, or browser runtime dependency is needed. The root homepage and CNAME remain untouched.

## Publish an edition

1. Read `news/EDITORIAL.md`, `news/PUBLISHING.md`, the latest `_data/arbiter_news/editions/*.json`, and the coverage index.
2. Add `_data/arbiter_news/editions/YYYY-MM-DD.json` using the latest edition's schema. Use public news only, never user emails, private projects, account data or household details.
3. Add `news/YYYY-MM-DD/index.html` containing:

```yaml
---
layout: arbiter-news
edition: "YYYY-MM-DD"
---
```

4. Run `python -m unittest discover -s tests -v`. Create one atomic commit on a new branch, open a PR, wait for successful checks, and merge through the ordinary repository rules. Do not bypass protection or approval requirements.
5. Verify GitHub Pages deployment success and fetch both the dated URL and latest page. Only then notify the reader with the site link. A merged commit is not proof of a successful deployment.

Latest, archive, RSS and coverage JSON are generated from the edition data automatically. Do not hand-edit a latest pointer, copy 300 old records into each new edition, or rebuild the presentation daily. Existing editions are never silently overwritten. Corrections must identify the changed fact and preserve Git history.

## Historical migration

The initial public edition is October 23, 2026, imported from the previously delivered HTML without a new round of reporting. Its text and source links were retained; shared illustrative art and navigation were introduced for the website. 319 earlier records from September 24–October 22 are stored in `_data/arbiter_news/history_parts/`, with import provenance in `history.json`. They are coverage evidence, not independently verified reporting. Known record gaps include September 23 and October 6. The site does not imply all prior full editions were migrated.

## Security and maintenance

Editorial data is plain text and HTTPS links, escaped by Liquid. No raw editorial HTML or remote images execute. The tabs progressively enhance ordinary anchor links; all stories remain readable without JavaScript. No analytics, cookies, ad scripts, external fonts or backend are required. Site code is MIT-licensed under `news/LICENSE`; third-party articles remain the property of their publishers.
