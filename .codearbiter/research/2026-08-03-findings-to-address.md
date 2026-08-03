# Findings to address — consolidated from the 2026-08-03 research sweep

What current research says codeArbiter should reconsider, ranked. Each item: the finding,
the evidence anchor, and a concrete suggested action. Full sources in dossiers 1-4.

## 1. FUNDAMENTAL — Hooks are not a security boundary, and the field now says so explicitly

Anthropic's own docs place hooks outside the enforcement boundary ("run unconstrained on
the host") and locate real enforcement in OS sandboxes, containers, VMs, and org-lockable
managed settings. OpenAI ships Codex with OS-enforced sandboxing as "a hard boundary."
codeArbiter's enforcement primitive is, in the host vendor's own taxonomy, a convenience
layer. (Dossier 3, Angle 1.)

**Actions:**
- State the threat model explicitly everywhere claims are made: codeArbiter keeps a
  well-intentioned agent on process rails and keeps the record; it does not contain a
  hostile agent or a hostile human. (The site now carries this; the README/docs should too.)
- Document "run codeArbiter inside a sandbox" as the recommended pairing: the sandbox
  contains, codeArbiter governs process. Complementary, not competing.
- Investigate Claude Code managed settings as a harder anchor (org-locked hook config).
- arbiterIDE's tool-dispatch-layer enforcement is the real answer; this research justifies
  its existence better than any marketing copy.

## 2. SIGNIFICANT — The audit log's integrity depends on the audited party

Git has no append-only property; the agent (or human) can rewrite the log it is audited by.
Specs/plans/ADRs in-repo are best practice; the LOGS need an external anchor to be audit
logs in the security sense. (Dossier 3, Angle 7.)

**Actions:** signed commits over log updates; or periodic digest anchoring (e.g., publish a
hash chain to a GitHub release/gist/transparency log); or an optional server-side mirror.
Even a per-commit log digest recorded in commit messages would make tampering detectable.

## 3. SIGNIFICANT — Same-model reviewer fleets ≈ one reviewer with extra requests

Nine frontier judges across seven model families collapse to ~2 effective independent votes
(correlated errors); the best single judge matched the panel; same-model fleets are the
degenerate case, and self-preference bias makes Claude-reviews-Claude the worst pairing.
(Dossier 3, Angle 4.)

**Actions:** codeArbiter's multi-host architecture is an unexploited asset here — dispatch
review across hosts/model families (Claude author, Codex-hosted reviewer, or vice versa).
Even one cross-vendor reviewer materially raises effective independence. Reframe "reviewer
fleet" claims to emphasize differentiated lenses + deterministic gates rather than implied
independent judgment.

## 4. SIGNIFICANT — The scope gap: no egress or credential control

The field's consensus #1 agent threat (lethal trifecta: private data + untrusted content +
egress) is controlled by network allowlists and credential scoping enforced outside the
agent. All five refusals govern repository state; exfiltration never touches git.
(Dossier 3, Angle 8.)

**Actions:** at minimum, position honestly (process governance, pair with a sandbox for
containment). Possible cheap wins within the existing hook architecture: H-guards on
obvious egress shell patterns (curl/wget POST with env vars, credential file reads piped to
network commands) as advisory, clearly labeled best-effort. Do not claim exfiltration
protection.

## 5. SIGNIFICANT — Test-first ordering: right gate, wrong warrant

Fucci et al. (IEEE TSE 2017): test-first vs. test-last sequencing made no measurable
difference for humans; granularity and short cycles carried the benefit. AND agents game
test gates (METR: o3 hacked 30% of RE-Bench runs unprompted). (Dossiers 2 §2, 3 Angle 3.)

**Actions:** keep the refusal, change the justification: for a generator that hallucinates,
a pre-existing failing test is a specification artifact the generator did not write and
cannot retrofit — that argument is agent-native and honest. Never cite TDD studies as the
warrant. Keep hardening test-quality gates (coverage/obligation phases) since a gate on
test existence is not a gate on test quality (SWE-bench Verified/UTBoost). Where possible,
verify with tests the author-agent cannot edit (separate context wrote them, hook-protect
test files during green phase).

## 6. SIGNIFICANT — AGPL is a procurement stop-list item

Google's blanket AGPL ban gets copied by enterprises before any dual-license conversation.
Comparable tools (Continue, Aider, Cline) are Apache-2.0. The legal contagion case for a
dev tool is weak, but procurement does not do nuance. (Dossier 3, Angle 6.)

**Actions:** the site's new "AGPLv3 covers the tool, never your code; commercial licensing
available" line is the correct mitigation. Add the same one-liner + a short FAQ to the
codeArbiter README. Whether to relicense is a business call; the evidence says the cost is
real adoption-funnel friction, not legal risk.

## 7. MODERATE — INDEX/summary drift is silent and unmitigated

Documentation-drift literature (code-comment inconsistency at 1.3B-change scale) predicts
the 23-skill/28-agent INDEX one-liners will rot against their bodies; the failure is silent
misrouting. This was the clearest open gap in the context-architecture review. (Dossier 4,
Target 5c.)

**Actions:** make INDEX ↔ SKILL.md consistency a CI-checkable invariant (generated
one-liners, or a checksum/frontmatter-derived check), not a discipline. Same for
routing-table.md entries vs. actual skill inventory.

## 8. MODERATE — Classify which invariants get blocking hooks vs. reminder hooks

Reminder-style hooks (H-12) restate the instruction at the moment of action — better than
session-start rules per position-bias evidence, but still probabilistic. Blocking hooks are
true gates. (Dossier 4, Target 5a.)

**Actions:** audit the H-NN inventory: every invariant that MUST hold should block; reminders
are for context-loading discipline only. Document the two tiers so users know which
guarantees are hard.

## 9. MINOR — Compliance-budget hygiene

Sanctioned logged overrides + override-rate metrics are exactly right per the usable-security
literature. Residual risk: numerous hard refusals firing on common actions train reflexive
overriding. (Dossier 3, Angle 2.)

**Actions:** periodically review which gates fire most and which get overridden most (the
metrics exist); tune or demote chronic-override gates rather than letting them burn budget.

## 10. MINOR — State-file merge conflicts

Frequently-written checked-in state (task board, logs) is a merge-conflict generator on
parallel branches, stressing the "no silent conflict reconciliation" refusal on the tool's
own files. (Dossier 3, Angle 7.)

**Actions:** consider a gitattributes union merge driver for append-only logs, or
per-branch log segmentation compacted on merge.

## What the research VALIDATED (no action needed, cite with confidence)

- Deterministic enforcement at the tool boundary as the answer to instruction unreliability
  (CaMeL, AgentDojo, OWASP, Saltzer & Schroeder). The core thesis holds.
- Few hard structural gates over many soft prompts (Anthropic: 93% of permission prompts
  approved = rubber stamps).
- No merge to default without a human (SLSA Source Track two-party review).
- Durable attributed audit trails (EU AI Act Art. 12, NIST AI RMF, OpenAI attributability).
- ADRs and checked-in specs/plans (Nygard, ThoughtWorks, ECSA 2024).
- Minimal always-loaded surface + progressive disclosure + disk-backed state + short-horizon
  subagents (Lost in the Middle, RULER, NoLiMa, Agent Skills spec, MemGPT lineage, METR
  horizon curve). The context architecture pre-aligned with what became the standard.
- Logged sanctioned overrides (compliance-budget literature prescribes exactly this).
