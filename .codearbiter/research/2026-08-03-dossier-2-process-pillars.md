# Research dossier 2 — Evidence for the process pillars

Captured 2026-08-03 for the "Why hard gates" essay. Covers: AI code quality and over-trust;
tests as the verification signal; code review limits; provenance and audit standards;
human-in-the-loop and ADRs; 2024-2026 agent-governance guidance. Mixed/negative findings
flagged inline; overclaim warnings at the end.

## 1. Quality of AI-generated code and over-trust

- **Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions** — Pearce et al. (NYU); arXiv Aug 2021, IEEE S&P 2022 — https://arxiv.org/abs/2108.09293 — Of 1,689 Copilot-generated programs across CWE Top-25 scenarios, ~40% contained vulnerabilities (~50% C, ~39% Python).
- **Do Users Write More Insecure Code with AI Assistants?** — Perry et al. (Stanford); arXiv Nov 2022, ACM CCS 2023 — https://arxiv.org/abs/2211.03622 — Participants with an AI assistant wrote significantly less secure code AND were more likely to believe their code was secure. Skeptical users who engaged more with prompts produced fewer vulnerabilities.
- **Security Weaknesses of Copilot-Generated Code in GitHub Projects** — Fu et al.; arXiv Oct 2023, ACM TOSEM 2025 — https://arxiv.org/abs/2310.02059 — In the wild: 29.5% (Python) / 24.2% (JS) of 733 assistant-generated snippets had security weaknesses across 43 CWEs.
- **2025 GenAI Code Security Report** — Veracode, Aug 2025 — https://www.veracode.com/wp-content/uploads/2025_GenAI_Code_Security_Report_Final.pdf — 45% of generated samples failed security tests (Java 72%); security flat over time as functional correctness improved. [Vendor report.]
- **AI Copilot Code Quality: 2025 Data Suggests 4x Growth in Code Clones** — GitClear, Feb 2025 — https://www.gitclear.com/ai_assistant_code_quality_2025_research — 211M changed lines 2020-2024: duplicated blocks up ~8x; 2024 first year copy-paste exceeded moved/refactored lines; churn ~doubled. 2026 follow-up: https://www.gitclear.com/the_ai_code_quality_maintainability_gap [Vendor analysis.]
- **Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity** — METR RCT; arXiv Jul 2025 — https://arxiv.org/abs/2507.09089 — Experienced OSS devs 19% slower with AI tools yet estimated 20% faster afterward. [Cuts against naive "AI = speed"; cite carefully.]
- **Complacency and Bias in Human Use of Automation** — Parasuraman & Manzey, Human Factors 2010 — https://journals.sagepub.com/doi/10.1177/0018720810376055 — Automation bias is robust across domains and expertise; worsens under load; not fixed by practice.
- **DORA Accelerate State of DevOps 2024** — https://dora.dev/research/2024/dora-report/ — +25% AI adoption associated with -1.5% delivery throughput and -7.2% delivery stability. [Correlational, modest.]

## 2. Tests as the strongest signal

- **Realizing Quality Improvement Through Test Driven Development** — Nagappan et al., Empirical Software Engineering 2008 — https://link.springer.com/article/10.1007/s10664-008-9062-z — Four industrial case studies: 40-90% lower pre-release defect density, 15-35% initial time cost. [Observational, not randomized.]
- **The Effects of TDD on External Quality and Productivity: A Meta-Analysis** — Rafique & Mišić, IEEE TSE 2013 — modest quality improvement, productivity loss or no gain; weaker effects in rigorous experiments. [MIXED — must cite.]
- **Why Research on Test-Driven Development is Inconclusive?** — Ghafari et al., ESEM 2020 — https://arxiv.org/pdf/2007.09863 — Test-first vs. test-last confounded with granularity/uniformity of cycles. Fucci et al. replications found no significant difference between test-first and iterative test-last (https://link.springer.com/article/10.1007/s10664-016-9490-0). Honest framing: the benefit is automated tests + short cycles, not the ordering ritual; compatible with "a failing test must exist" as an enforceable gate.
- **SWE-bench** — Jimenez et al., ICLR 2024 — https://www.swebench.com/original.html — The de facto agent benchmark grades solely by fail-to-pass + pass-to-pass tests: the field's operational "tests are the spec."
- **SWE-bench Verified** — OpenAI, Aug 2024 — https://openai.com/index/introducing-swe-bench-verified/ — 61.1% of tasks flagged for tests that could unfairly reject valid solutions; 38.3% underspecified. 2026 follow-up: OpenAI stopped using Verified after an audit found 59.4% of o3-unsolved problems had material test/spec flaws — https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- **UTBoost** — arXiv Jun 2025 — https://arxiv.org/pdf/2506.09289 — Augmenting tests changed leaderboard rankings; weak tests let ~7.8-31% of "passing" patches through. Also "Are Solved Issues Really Solved Correctly?" (https://arxiv.org/abs/2503.15223): 32.67% of successful patches involved solution leakage; 31.08% passed on weak tests. [Double-edged: tests are the gate AND test quality must itself be gated.]
- **TDFlow: Agentic Workflows for Test Driven Development** — arXiv Oct 2025 — https://arxiv.org/pdf/2510.23761 — Research frontier converging on tests as the agent's verification oracle.

## 3. Code review effectiveness and limits under AI volume

- **Expectations, Outcomes, and Challenges of Modern Code Review** — Bacchelli & Bird (MSR), ICSE 2013 — https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/ — Review found fewer defects than practitioners expected; realized value is knowledge transfer/awareness; understanding is the binding constraint.
- **Code Review at Cisco Systems** — Cohen/SmartBear 2006 — https://static0.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf — Detection best at 200-400 LOC/session, degrades sharply beyond; 60-90 min fatigue limit. [Old, vendor-linked; standard citation.]
- **These Aren't the Reviews You're Looking For** — arXiv May 2026 (EASE 2026) — https://arxiv.org/abs/2605.02273 — Most AI-generated PRs receive no human review; when reviewed, dominated by other AI agents; review metrics cannot be read as human oversight.
- **Reliability without Validity: LLM-as-a-Judge at scale** — arXiv Jun 2026 — https://arxiv.org/abs/2606.19544 — 21 judges, ~541k judgments: high consistency coexists with severe systematic bias. Companion: position bias (https://arxiv.org/abs/2406.07791).
- **Resolving Code Review Comments with Machine Learning** — Frömmgen et al. (Google), ICSE-SEIP 2024 — https://research.google/pubs/resolving-code-review-comments-with-machine-learning/ — ML-suggested edits resolve 7.5% of reviewer comments at Google.
- **CodeRabbit State of AI-assisted PRs** — Dec 2025 — AI-assisted PRs ~1.7x more issues, concentrated in logic/security/edge cases. [Vendor; industry color only.]

## 4. Provenance and audit

- **SLSA v1.x** — OpenSSF — https://slsa.dev/spec/v1.2/source-requirements — Verifiable machine-generated provenance; Source Track highest level requires two-party review of changes to protected branches. Standards anchor for "no merge without a human."
- **in-toto** — Torres-Arias et al., USENIX Security 2019; CNCF graduated 2025 — https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias — Cryptographic attestation of every supply-chain step; evaluated against 30 real compromises.
- **NTIA Minimum Elements for an SBOM** — 2021 (EO 14028) — https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom
- **EU AI Act, Article 12 (Record-keeping)** — high-risk obligations from Aug 2, 2026 — https://artificialintelligenceact.eu/article/12/ — Automatic event recording over the system lifetime for traceability. Strongest legal citation for durable audit trails of autonomous decisions.
- **NIST AI RMF 1.0** — Jan 2023 — https://www.nist.gov/itl/ai-risk-management-framework — GOVERN function: systematic documentation, accountability, traceability.
- **ISO/IEC 42001:2023** — certifiable AI management systems: designated accountability, decision records, audit trails.

## 5. Human-in-the-loop, accountability, ADRs

- **Meaningful Human Control over Autonomous Systems** — Santoni de Sio & van den Hoven, Frontiers 2018 — https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2018.00015/pdf — Control requires the system to "track" human reasons and actions to "trace" to a responsible human. Backbone for user attribution + human merge authority.
- **Documenting Architecture Decisions** — Michael Nygard, Nov 15, 2011 — https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — Origin of ADRs; superseded decisions marked, not deleted.
- **Lightweight ADRs** — ThoughtWorks Technology Radar "Adopt" (2017-2018) — https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records; ecosystem: https://adr.github.io/
- **ADRs in Practice: An Action Research Study** — Aakvik et al., ECSA 2024 — https://link.springer.com/chapter/10.1007/978-3-031-70797-1_22 — Measurable improvement in documentation culture and knowledge transfer. [Single-company; empirical ADR evidence thin overall.]

## 6. Governing autonomous coding agents (2024-2026)

- **Practices for Governing Agentic AI Systems** — Shavit et al. (OpenAI), Dec 2023 — https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf — Constraining action space, approval for high-stakes actions, legibility, monitoring, attributability, interruptibility: maps nearly 1:1 onto gates/audit/attribution.
- **Our Framework for Developing Safe and Trustworthy Agents** — Anthropic, 2025 — https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents — Humans retain control before high-stakes actions; limit blast radius.
- **Measuring AI Agent Autonomy in Practice** — Anthropic research, 2026 — https://www.anthropic.com/research/measuring-agent-autonomy — Users approve ~93% of permission prompts: per-action interactive confirmation is behaviorally unreliable as a sole mechanism. [Supports few hard structural gates over many soft prompts; also critiques prescriptive approval requirements.]
- **Levels of Autonomy for AI Agents** — Feng, McDonald, Zhang; arXiv Jun 2025 — https://arxiv.org/abs/2506.12469 — Autonomy level is a deliberate design decision separable from capability.
- **DORA State of AI-assisted Software Development 2025** — Sep 2025 — https://dora.dev/dora-report-2025/ — AI amplifies existing strengths/weaknesses; gains accrue to teams with strong version control, small batches, robust testing.

## Overclaim warnings

1. TDD: rigorous experiments show null-to-modest effects; Nagappan's 40-90% is non-randomized. Safest claim: automated tests + short cycles carry the benefit; test-first is the enforceable proxy.
2. Tests as oracle: SWE-bench's own history shows weak tests give false "solved" signals. A gate on test existence is not a gate on test quality.
3. Review: humans find fewer defects than assumed; single LLM judges systematically biased; multi-perspective review is a hedge, not a proven fix.
4. HITL: 93% approval means per-action prompts approximate rubber stamps; defensible position is few hard structural gates with durable attribution.
5. Vendor data (GitClear, Veracode, CodeRabbit) labeled as industry reports; DORA's stability effect is correlational.
