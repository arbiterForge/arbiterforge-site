# Historical archive backfill — October 23, 2026

The archive now distinguishes actual recovered story text from coverage-only records. It does not turn a short coverage ledger into an invented full briefing.

## Recovery scope

28 historical date pages span September 24–October 22. The previously published October 23 daily edition remains the latest.

- 7 dates have all retained story texts recovered: September 24 and October 17–22.
- September 29 is partial: 12 early-edition story texts are recovered alongside 12 later-edition coverage-only records.
- 20 other dates have retained coverage records only; their full original narrative was not recoverable through the available files.
- October 6 has no available edition and no fabricated date page. September 23 precedes the available archive.

In total, 92 original story texts were recovered from eight saved HTML sources. The 319 historical coverage records are preserved unchanged, exactly once in the historical pages. Early ledger counts may be smaller than the original issue because repeated coverage was not retained. Multiple same-day editions may be combined; record counts are not a claim that a complete original issue was recovered.

## Fidelity and provenance

The migration extracts the original story title, paragraph text and source URLs. It does not rewrite or fact-check historical claims. HTML markup, article-external labels and original illustrations are not copied; the site renders the recovered plain text in its shared accessible layout. Original errors can therefore remain, and every date page prominently warns that it is historical material, not new reporting. Source links may no longer resolve or reflect their historical state.

Each restored story includes its original HTML filename and SHA-256, plus a digest of its recovered title, paragraphs and links. The transfer payload was verified byte-for-byte before import. `_data/arbiter_news/backfill.json` records source provenance, recovery counts, and original history-part hashes. It is published at `/news/archive/status.json`.

Five September 24 cards had no event keys and were explicitly matched by title to the existing five ledger records. One September 29 Transcribe entry used `custom-resource-customer-kms-keys` where the retained ledger used `customer-managed-kms-custom-assets`; these names identify the same dated announcement. The original source key is preserved alongside the unmodified retained record.

No user email, financial-account data, private work documents, local filesystem paths or credentials are part of the published archive.

## Isolation from daily publishing

Historical data lives under `_data/arbiter_news/archive/`, not `editions/`. It uses `_layouts/arbiter-news-history.html`. The archive index combines date links from both collections, with explicit recovery labels.

The latest selector, daily coverage index, daily RSS feed and existing October 23 edition data are not changed. Backfill does not add 28 old notifications to the daily RSS feed or double-count historical developments in duplicate checking. Future daily publication continues to add only the ordinary edition JSON and dated page.

## Checks

`test_news_backfill.py` verifies recovery counts, source hashes, exact ledger preservation, category normalization, title/text/link digests, HTTPS URLs, partial recovery, absent dates, escaping and separation from daily publishing. `check_news_build.py` also checks every rendered historical page, article counts, tabs, duplicate IDs/event keys, recovery labels, links in the archive and unchanged daily feed behavior.

Run `python -X utf8 -m unittest discover -s tests -v`. The repository workflow builds with the actual GitHub Pages Jekyll toolchain and validates the rendered output before merge.
