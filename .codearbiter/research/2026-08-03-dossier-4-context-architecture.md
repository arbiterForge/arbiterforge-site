# Research dossier 4 — Context management: reference cards and routing chains

Captured 2026-08-03. Evaluates codeArbiter's context architecture: ~186-line always-loaded
orchestrator; surface-scan INDEXes ("skill bodies load on routing only"); reference cards
loaded on scope-touch (reference-map.md, routing-table.md, includes/); command → skill →
agent routing chains with fresh subagents; durable state externalized to checked-in disk.

## Target 1 — Long-context degradation ("context rot") — VERDICT: SUPPORTS

- **Lost in the Middle** — Liu et al. (Stanford); TACL 2024 — https://arxiv.org/abs/2307.03172 — U-shaped performance: accuracy highest at context start/end, degrades sharply in the middle. Foundational, heavily replicated.
- **RULER** — Hsieh et al. (NVIDIA); Apr 2024 — https://arxiv.org/abs/2404.06654 — "Effective context length": models degrade on realistic tasks as length grows; of models claiming ≥32K, only four handled 32K effectively. Claimed window ≠ usable window.
- **NoLiMa** — Modarressi et al.; Feb 2025 — https://arxiv.org/abs/2502.05167 — With minimal lexical overlap, 10 of 12 models claiming ≥128K fall below 50% of short-context baseline at 32K; GPT-4o 99.3% → 69.7%. Worst when retrieval requires inference, not matching.
- **Context Rot** — Hong, Troynikov, Huber (Chroma); July 2025 — https://research.trychroma.com/context-rot — 18 SOTA models: reliability decreases non-uniformly with input length even on trivial tasks. [Vendor report; methodology published; consistent with NoLiMa/RULER.]
- **Effective context engineering for AI agents** — Anthropic, Sept 29, 2025 — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — Finite "attention budget"; the goal is "the smallest possible set of high-signal tokens"; just-in-time retrieval preferred over pre-loading.
- Caveat: these studies measure retrieval/QA, not policy adherence; "less context → better rule-following" is a well-supported inference, not directly measured.

## Target 2 — Progressive disclosure as the emerging standard — VERDICT: SUPPORTS

- **Agent Skills** — Anthropic, Oct 2025 — https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills ; spec: https://agentskills.io — Three-level disclosure: metadata always loaded; SKILL.md body on trigger; bundled files on reference. codeArbiter's INDEX + bodies-on-routing is structurally identical (pre-alignment with what became the open standard).
- **Code execution with MCP** — Anthropic, Nov 2025 — https://www.anthropic.com/engineering/code-execution-with-mcp — Loading all tool definitions upfront bloats context; filesystem-explored on demand cut one workload ~150K → ~2K input tokens (98.7%).
- **Tool Search Tool / deferred loading** — https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool — Load-on-demand is now a platform primitive (~85%+ token reduction cited).
- **RAG vs. Long-Context (Self-Route)** — Li et al. (DeepMind); EMNLP 2024 — https://arxiv.org/abs/2407.16833 — LC stuffing outperforms RAG on average when affordable; RAG dramatically cheaper; hybrid routing retains near-LC quality at fraction of cost. [Partial counter-evidence: selective loading trades a small accuracy ceiling for cost/reliability; routing quality becomes the crux.]
- **Manus context-engineering lessons** — Ji, July 2025 — https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus — Mutating tool definitions mid-episode breaks KV-cache; mask instead. codeArbiter discloses via file reads (append-only), avoiding that failure. [Experience report.]

## Target 3 — Externalized memory / disk-backed state — VERDICT: SUPPORTS

- **MemGPT** — Packer et al. (Berkeley); Oct 2023 — https://arxiv.org/abs/2310.08560 — OS-style paging between in-context memory and external storage beats fixed-context baselines.
- **Reflexion** — Shinn et al.; NeurIPS 2023 — https://arxiv.org/abs/2303.11366 — Persisted episodic self-reflections lifted HumanEval pass@1 to 91%.
- **Anthropic memory tool + structured note-taking** — https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool — Compaction keeps the live window small; notes persisted outside survive summarization.
- **Claude Code Best Practices** — Anthropic, Apr 18, 2025 — https://www.anthropic.com/engineering/claude-code-best-practices — CLAUDE.md pattern; Markdown checklists/scratchpads for large tasks. `.codearbiter/` = this practice systematized and checked in.
- **Manus: filesystem as context** — restorable compression (keep path, drop content). [Experience report.]
- Weakness: little controlled evidence quantifying disk-backed state's post-compaction benefit; support is architectural consensus + case studies.

## Target 4 — Subagent isolation — VERDICT: PARTIALLY SUPPORTS (mitigation is load-bearing)

- **Anthropic multi-agent research system** — June 13, 2025 — https://www.anthropic.com/engineering/multi-agent-research-system — Lead + subagents beat single-agent by 90.2% on internal research eval; costs ~15x chat tokens; explicitly notes coding has fewer parallelizable tasks. [Internal eval; number does not transfer to coding.]
- **Don't Build Multi-Agents** — Walden Yan (Cognition/Devin); June 2025 — https://cognition.com/blog/dont-build-multi-agents — Parallel subagents without shared traces make conflicting implicit decisions; intent lives in the full trace; bites hardest in coding.
- **Why Do Multi-Agent LLM Systems Fail? (MAST)** — Cemri et al. (Berkeley); NeurIPS 2025 D&B — https://arxiv.org/abs/2503.13657 — 14 failure modes across 1,600+ traces: specification issues, inter-agent misalignment, task-verification failures; MAS gains often minimal on popular benchmarks.
- **METR long-task horizon** — Mar 2025 — https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ — Near-100% success on <4-minute-human tasks, <10% on >4-hour tasks. Supports slicing into short fresh-context tasks (writing-plans' 2-5 minute tasks).
- Verdict detail: isolation is proven for review/research fan-out (read-only, parallelizable). For authoring, it works only because the plan-on-disk substitutes for shared context; that substitution is argued, not benchmarked.

## Target 5 — Adversarial: where the pattern fails

### (a) Instruction dilution — the routing discipline is itself a prompt
- **IFScale** — Jaroslawicz et al.; July 2025 — https://arxiv.org/abs/2507.11538 — Best frontier models hit only 68% compliance at 500 simultaneous instructions; primacy bias; model-dependent decay. A meta-rule like "load the card first" will be probabilistically dropped.
- **LLMs Get Lost in Multi-Turn Conversation** — Laban et al.; ICLR 2026 Outstanding Paper — https://arxiv.org/abs/2505.06120 — ~39% average drop single-turn → multi-turn; models commit early and don't recover. Mechanism for long-session drift from opening rules.
- **Claude Skills reliability problems** — practitioner posts (e.g. https://medium.com/@marc.bara.iniesta/claude-skills-have-two-reliability-problems-not-one-299401842ca8) — skills fail to activate; or activate but steps aren't followed. [Weak evidence — anecdotal — but directly about the SKILL.md mechanism and corroborates IFScale.]
- **Judgment on H-12-style reminder hooks:** deterministic hooks are the correct mitigation shape. Rank ordering: a BLOCKING hook is a true gate; a REMINDER hook re-enters the instruction at the moment of action (highest-attention region per position-bias literature) — meaningfully better than a rule stated once at session start, but still probabilistic. Classify which invariants get which treatment.

### (b) Routing/misclassification errors
- MAST's specification/misalignment classes include wrong decomposition and misrouted premises; Anthropic's own post admits early versions spawned excessive subagents. Compounding arithmetic (0.9^10 ≈ 35%) [vendor-blog illustrations]. codeArbiter's exposure: routing-table.md is consulted by the model, so route selection inherits (a)'s failure probability; downstream gates catch consequences, not the route itself.

### (c) Index/summary staleness — CLEAREST OPEN GAP
- **Code-comment inconsistency at scale** — Wen et al., ICPC 2019 — https://dl.acm.org/doi/abs/10.1109/ICPC.2019.00019 ; outdated-docs detection (https://arxiv.org/abs/2307.04291) — Human-maintained summaries drift; updates land late or never. Analog evidence: a 23-skill/28-agent INDEX is documentation, and documentation rots. Silent failure; INDEX/skill-body consistency should be a CI-checkable invariant, not a discipline.

### (d) Retrieval-miss risk
- **Seven Failure Points When Engineering a RAG System** — Barnett et al.; CAIN 2024 — https://arxiv.org/abs/2401.05856 — Failure Point #1 is missing content/failure to retrieve. Deferred context can miss; always-loaded cannot. NoLiMa applies with teeth: routing from a one-line description to the right card is a low-lexical-overlap association task. Mitigation shape: deterministic scope-touch triggers (file-path match → card required) convert semantic guesses into deterministic events — the right response.

### (e) Indirection overhead
- Cognition (above); Manus KV-cache economics (10x cached vs. uncached pricing); DeepMind Self-Route accuracy ceiling; Anthropic concedes just-in-time is slower and recommends hybrids. [No peer-reviewed measurement of governance-layer indirection overhead; triangulated.]

## Overall assessment

The load-bearing claim (small always-on surface, deferred loads, state on disk, short-horizon
fresh contexts) is supported by an unusually consistent evidence stack. Two weak points to
concede in print: authoring-subagent isolation rests on plan-on-disk substituting for shared
context (argued, not benchmarked), and deferred loading pays retrieval-miss + staleness risk
that always-loaded context doesn't have — which is exactly why the deterministic hook layer,
not the prompt discipline, is the part of the architecture the evidence says to trust and
extend.
