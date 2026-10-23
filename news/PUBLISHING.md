# Scheduled publishing protocol

Repository: `arbiterForge/arbiterforge-site`; default branch: `main`.
Permanent site: `https://arbiterforge.com/news/`.
Dated edition: `https://arbiterforge.com/news/YYYY-MM-DD/`.

The ChatGPT Arbiter News schedule performs research and submits edition data. GitHub Pages builds the site after a normal merge. The repository does not independently call an AI model or contain model credentials. Task authorization, connector write permissions and repository rules still apply; report a publishing block instead of claiming success.

## Tool-compatible write path

Use the GitHub connector to read current main and relevant source files. Create a date-specific branch from the observed current main. Stage the edition JSON and dated page in one Git tree with `base_tree_sha` from that commit, then create a commit with that parent and update only the feature branch. Alternatively, use equivalent authenticated Git commands when available. Open a PR against main, inspect checks and review requirements, then merge using the expected head SHA after checks succeed. Never force-update main or use administrative bypasses. If the head moved, re-read and reconcile rather than overwriting.

Only two paths ordinarily change:
- `_data/arbiter_news/editions/YYYY-MM-DD.json`
- `news/YYYY-MM-DD/index.html`

Do not edit workflows, layouts, scripts, tests, licenses or historical records during a normal daily publishing run. A failure to retrieve old coverage must be disclosed, not replaced with an invented claim of deduplication. Do not fill missing files with reconstructed unseen news.

## JSON schema

Root: `schema_version: 1`, `edition_date: "YYYY-MM-DD"`, `title: "Arbiter News"`, `intro`, `overview`, `history_note`, `stories` array. Optional `shortfalls` object maps category IDs to explicit research shortfall explanations. Migration-only fields must not be copied onto new editions.

Story: `category` (`ai|cloud|security|money`), `event_key`, `status` (`new|material-update`), `topic`, `title`, `publisher`, `publication_date`, `event_date` (string or null), `freshness`, `highlights`, `implications`, `takeaway`, `development_summary`, and `sources` (`[{"label":"Original source","url":"https://..."}]`). Strings contain plain text, not HTML. A material update additionally needs `updates_event_key` and `change_summary`.

For a rerun on an already published date, do not silently replace the edition. Prefer a no-op if nothing substantive changed. For a justified correction or additional reporting, update with explicit revision metadata and a visible correction note through a fresh PR, preserving the existing stories and Git history.

## Verification and delivery

Inspect source-contract checks and rendered-page checks. After merge, inspect the actual Pages run, then open the live dated URL and homepage and verify the date and story count. Return the live site link plus a compact description. If only the PR is ready, say so and link it. If publishing fails or requires approval, preserve the last good live edition and report the blocker. A downloadable HTML can be an explicitly labeled fallback, never the normal delivery or a purported live publication.
