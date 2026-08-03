# Dispositions — Fable adversarial review, 2026-08-03

Companion to `2026-08-03-adversarial-review-fable.md`. Actions by Claude Code, same date,
with user decisions where noted.

## Customer findings

| # | Finding | Disposition |
|---|---|---|
| C1 | Evidence proves the trivial gate | **Fixed (user-directed).** Captured a real block of `git push origin main` by invoking the shipped `pre-bash.py` in a sandbox repo (exit 2, BLOCKED [H-01], gate-events line, `commandExecuted: false`). Now the lead replay, stacked above the `git add -A` one. Capture manifest committed at `assets/proof/push-block.json`. |
| C2 | No install command or install inventory | **Fixed.** New install strip in `#system`: real commands (`/plugin marketplace add arbiterForge/codeArbiter`, `/plugin install ca@codearbiter`, Codex variant) plus "What it writes": hooks (Python stdlib, local-only) + `.codearbiter/`, dormant until opt-in, no network calls, no telemetry. |
| C3 | Naked AGPLv3 badge | **Fixed (user approved full line).** "AGPLv3 covers codeArbiter itself, never your code. Commercial licensing available." in the install strip. |
| C4 | Headline contradicted by arbiterIDE copy | **Fixed via candor, headline kept.** Threat-model paragraph added to the evidence panel: hooks block at the tool-call boundary; an agent cannot argue past them; a human with shell access can remove them deliberately and the removal lands in the append-only audit trail. arbiterIDE phrasing softened to design intent (see P4). |
| C5 | No maintenance signal | **Partially fixed.** "27 tagged releases · changelog" link added (count verified against GitHub tag refs). Stars/testimonials not added (none to honestly show). |
| C6 | Verification chain doesn't verify | **Fixed.** Source link pinned to immutable commit `a3a2df23…` (remote blob sha256 re-verified = `b2cf1a87…7873`, matching the invoked local file and both manifests). Full sha256 displayed. Dead "faithful replay" link replaced with the two capture manifests served from this repo (`assets/proof/*.json`). Note: `v2.11.0` tag does not exist on GitHub (newest public tag v2.8.13), so commit-pinning was used instead of tag-pinning. |
| C7 | Counts raise token-cost objection | **Fixed.** "Local and portable" card now reads: enforcement is instant, free, no model calls; reviews spend tokens only when invoked. Flagship reframed to "One policy core, expressed as 40 commands, 23 skills, and 28 agents." |
| C8 | Multi-host claim, single-host evidence | **Partially fixed.** Host status row (Claude Code Stable · Codex CLI Stable · Pi Preview) in the install strip. A `host=codex` capture was not made; open item. |
| C9 | Pi preview status omitted | **Fixed.** Flagship body and host row both mark Pi as preview. |
| C10 | Links same-tab; excess whitespace | **Fixed.** `target="_blank"` on all 15 external links; section padding compressed (clamp 6–10rem → 5–7.5rem). |

## Partner findings

| # | Finding | Disposition |
|---|---|---|
| P1 | No contact channel | **OPEN (user decision).** Domain email not yet set up. HTML TODO comment left in the footer; add the address + JSON-LD `contactPoint` when the mailbox exists. |
| P2 | Anonymous maker | **Fixed (user approved).** Footer: "Built by SUaDtL" linking to the GitHub profile; JSON-LD `founder` added. |
| P3 | Business model negatively signaled | **Fixed.** Commercial licensing line (see C3). |
| P4 | Over-claims | **Fixed.** "Every host." → "Every host you use." · arbiterIDE tag "In development" → "Pre-alpha" · hostile-client sentence rephrased as design intent ("designed so that not even a hostile client can talk past them"). Hero headline kept, backed by the new threat-model candor (C4). |
| P5 | No thought leadership / essay | **Fixed (2026-08-03, later same day).** "Why hard gates" written and published at `why-hard-gates.html`, linked from the manifesto and footer. Grounded in a four-dossier research sweep (see `.codearbiter/research/`), including a counter-evidence section per the brand's own standard. |
| P6 | Brand fragmentation; heavy og-image | **Fixed.** Footer states "Maker of codeArbiter and arbiterIDE." OG image re-encoded 772KB PNG → 62KB progressive JPEG (meta updated). |

## Verification

Real-capture provenance: sandbox repo, `.codearbiter/CONTEXT.md` `arbiter: enabled`, branch
`feat/proof`, payload `{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}`
piped to the unmodified local hook (sha256 matches the pinned GitHub blob byte-for-byte).
Post-change checks: zero horizontal overflow at mobile width (scrollWidth == clientWidth),
desktop and mobile screenshots reviewed, codeArbiter's own repo confirmed unpolluted by the
capture run.
