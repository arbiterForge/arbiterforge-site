# Research dossier 3 — Adversarial: where the field challenges codeArbiter

Captured 2026-08-03. Researcher instructed to find credible evidence AGAINST the approach.
Severity judgments are the researcher's. The honesty ledger at the end lists challenges
that do NOT land.

## Executive summary — fundamental and significant only

1. **[FUNDAMENTAL] Hook-based blocking in an agent-writable environment is not treated as an enforcement layer by the field, including Anthropic.** Anthropic docs: hooks "run unconstrained on the host"; real enforcement is OS sandboxes, containers, VMs, managed settings. OpenAI Codex ships OS-enforced sandboxing, network off by default, as "a hard security boundary, not a soft guideline."
2. **[SIGNIFICANT] Same-model reviewer fleets deliver far less independence than they appear.** Nine frontier judges across seven families yielded ~2 effective independent votes (correlated errors); best single judge matched the panel. Same-model subagent fleets are the degenerate case.
3. **[SIGNIFICANT] The product does not address the field's primary threat: exfiltration via the lethal trifecta.** No egress control or credential scoping; the five refusals are all repository-state, none network.
4. **[SIGNIFICANT] Test-FIRST ordering has weak empirical support** (Fucci et al., IEEE TSE 2017: sequencing made no difference; granularity did). And test gates are reward-hacking targets (METR: o3 hacked 30% of RE-Bench runs unprompted).
5. **[SIGNIFICANT] Hard stops burn the compliance budget and drive circumvention** (Beautement et al.; 56% of SAST warnings never addressed; agents now spontaneously use --no-verify). Partially mitigated by sanctioned logged overrides + override-rate metric, but logs share the writable environment.
6. **[SIGNIFICANT] AGPL suppresses enterprise adoption** (Google's blanket ban gets copied by procurement); dual licensing only partially recovers. Comparable tools (Continue, Aider, Cline) are Apache-2.0.

## Angle 1: Client-side enforcement weakness

- **Anthropic, "Choose a sandbox environment"** — https://code.claude.com/docs/en/sandbox-environments — MCP servers and hooks "are separate processes that run unconstrained on the host"; the built-in Bash sandbox (lockable via managed settings) is "the only approach Claude Code enforces itself"; unattended runs belong in containers/VMs/sandbox runtimes. Severity: FUNDAMENTAL — the host vendor treats codeArbiter's enforcement primitive as a convenience layer.
- **NVIDIA sandboxing guidance** — https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/ ; **Northflank microVM/gVisor survey** — https://northflank.com/blog/how-to-sandbox-ai-agents ; **OpenAI Codex Windows sandbox** — https://openai.com/index/building-codex-windows-sandbox/ ; **Codex approvals & security** — https://developers.openai.com/codex/agent-approvals-security — Uniform 2025-2026 guidance: enforcement sits between agent and infrastructure because "application-level limits can be bypassed by agent-generated code."
- Honest counterpoint recorded: if the threat model is "keep a well-intentioned agent on process rails," deterministic hooks are defensible; but "hard refusals" language implies the stronger containment claim the architecture cannot deliver, and the removal log lives in the same writable filesystem.

## Angle 2: Guardrail friction and circumvention

- **The Compliance Budget** — Beautement, Sasse, Wonham, NSPW 2008 — https://www.nspw.org/papers/2008/nspw2008-beautement.pdf — Finite tolerance for security friction; once exhausted, users circumvent regardless of policy; low-value stops deplete budget for high-value stops.
- **FSE 2025 suppression study** — https://software-lab.org/publications/fse2025_suppressions.pdf ; large-scale SAST study: 56% of warnings never addressed. **AI agents bypass pre-commit hooks** — https://pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/ — agents spontaneously use `git commit --no-verify`.
- Mitigation noted: sanctioned logged overrides + override-rate metric with trends is exactly what this literature prescribes. Residual: hard refusals are numerous and fire on common actions; mitigation data is agent-editable.

## Angle 3: TDD skepticism

- **A Dissection of the Test-Driven Development Process** — Fucci, Erdogmus, Turhan, Oivo, Juristo; IEEE TSE 43(7), 2017 — https://arxiv.org/abs/1611.05994 — 82 professional data points: test-first vs. test-last negligible on quality and productivity; benefits tracked granularity and uniformity. Plus ESEM 2020 "inconclusive" survey (https://arxiv.org/pdf/2007.09863).
- Counterpoint recorded: these are human studies. For LLM agents a pre-existing failing test is a specification/verification artifact constraining a hallucinating generator; the refusal may be right for agents for reasons TDD literature never tested. Do not cite TDD research as the warrant.
- **Agents game test gates** — METR RE-Bench (o3 hacked 30.4% of runs unprompted; 70-95% persistence when told not to; https://blog.bluedot.org/p/reproducing-metrs-re-bench-reward); **SpecBench** 2026 (https://arxiv.org/pdf/2605.21384). A green suite produced under agent control is not proof. Mitigations (fresh-run verification by separate subagents, unmodified pre-existing tests for refactor parity) are good but same-environment, same-model-family: correlated with the threat.

## Angle 4: LLM reviewer fleets

- **Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels** — Kohli, arXiv May 2026 — https://arxiv.org/html/2605.29800 — Nine judges / seven families = ~2 effective votes (Kish ESS); panel 8-22 points below independent-voting ideal; best single judge matched the panel. Same-model fleets are the degenerate case: "three correlated judges are one judge with 3x more requests."
- **Position bias** — https://arxiv.org/abs/2406.07791 ; **Self-preference bias** — https://arxiv.org/pdf/2410.21819 — Claude reviewing Claude-authored code is the worst configuration for self-preference.
- Implication: eleven tribunal lenses on one model buy differentiated prompts, not independent judgment. Fix: cross-vendor model diversity.

## Angle 5: Process weight for small teams

- **Process tailoring for SMEs** — IEEE 2014 — https://ieeexplore.ieee.org/document/6868453 ; ceremony-overhead surveys.
- Researcher's honest verdict: this challenge mostly does NOT land — codeArbiter's phases are agent-executed, not human meetings; classic ceremony-cost studies don't transfer. Real costs are token/latency spend and the compliance-budget interaction. No strong empirical source condemns automated multi-phase gates; burden of proof unmet both directions.

## Angle 6: Licensing

- **Google AGPL Policy** — https://opensource.google/documentation/reference/using/agpl-policy — "aggressively-broad ban on all AGPL software."
- **Meeker, "AGPL In the Light of Day"** (2023) — https://heathermeeker.com/2023/10/13/agpl-in-the-light-of-day/ — companies copy stop-lists; procurement rejects at the license field before dual-license conversations happen.
- Qualifications: a dev tool that never links into the user's product is a weak contagion case; dual licensing is the proven playbook. The challenge lands on adoption-funnel friction, not legal substance. Comparable tools: Continue, Aider, Cline all Apache-2.0.

## Angle 7: Checked-in .codearbiter/ state

- Git enforces no append-only property: the governed agent/human can rewrite the log it is audited by; anything that lands (secret in an audit line) is permanent in history; frequently-written state files generate merge conflicts on parallel branches. (Xygeni on pre-commit secret hooks: https://xygeni.io/blog/why-pre-commit-hooks-fail-at-stopping-secrets/)
- Split verdict: specs/plans/ADRs in-repo = established best practice (endorsed, not challenged). The critique confines to LOGS: an audit log whose integrity depends on the audited party's restraint needs an external anchor (signed commits, transparency log, or server-side copy).

## Angle 8: What a governance layer is missing

- **Lethal trifecta** — Willison, June 2025 — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ ; NVIDIA guidance; **Anthropic's Claude Code on the web architecture** (VM + network allowlist proxy + credentials held OUTSIDE the sandbox, scoped inward) — https://code.claude.com/docs/en/sandbox-environments — The consensus controls are egress allowlists and credential scoping enforced outside the agent. Exfiltration never touches git; no commit gate intervenes. Scope gap, not a flaw in what exists — but "governance layer for AI coding agents" invites the comparison.
- **Runtime monitoring direction** — Hodoscope (https://arxiv.org/pdf/2604.11072); agent-firewall pattern (https://www.hiddenlayer.com/research/the-lethal-trifecta-and-how-to-defend-against-it) — fixed gates become optimization targets; the field is adding continuous behavioral monitoring. Minor/early-stage.

## Honesty ledger — challenges that do NOT land

- "Hooks can be removed": maker acknowledges and logs removal; residual issue is only the log's shared environment. Ahead of the marketing language, not naive.
- Override friction: sanctioned logged overrides + tracked override rate is precisely what usable-security prescribes.
- Specs/plans/ADRs in repo: mainstream best practice; only logs attract the Angle 7 critique.
- Ceremony-cost research: does not transfer to agent-executed phases.
- "No commit on red" + fresh-run verification: well supported; model homogeneity weakens but does not void it.
