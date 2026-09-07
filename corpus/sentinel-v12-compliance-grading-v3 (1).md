# Sentinel V12 Compliance Grading — v3 (Live Re-Grade, Post-Twin)

**Graded against:** `global-ai-governance-requirements-v1.md`, Part 1 (~25 blended requirements)
**Repo state:** fresh clone, HEAD `7e2c29b` (July 19, 2026) — includes roadster phase-1, rate limiter, circuit breaker, queue-identity converter, and the customer-DR witness replica ("the twin," DAP v1)
**Method:** Every rating below was either executed live this session (real Postgres/Redis, no mocks — see evidence citations) or confirmed by direct read of the current source. Nothing here is carried over unverified from the original (pre-twin, HEAD `5fb20b3`) audit.

**What changed since the last grade:** The twin didn't exist yet. It's real now, and it changes the story for exactly two of the engine's worst holes — not all of them, and not by accident. Column 4 reports what's actually true with the twin deployed, not a projection.

---

## The Table

| # | Requirement | Current status (engine alone) | Bulletproof bar | With the twin deployed |
|---|---|---|---|---|
| A1 | Named, accountable ownership | **Partially Meets** — `COMPLIANCE.md`/`MODEL_CARD.md`/`AUDIT_PLAYBOOK.md` exist and are current, but no charter names a specific accountable role/individual in the repo itself | A documented RACI or governance charter naming who owns V12 risk decisions, checked into the repo | No change — organizational, not a witness-layer question |
| A2 | Cross-functional accountability structure | **Does Not Meet** — no risk/compliance/legal review gate exists in the dev process as codified | A defined multi-discipline sign-off step (even lightweight) before a cassette ships to production | No change |
| A3 | Documented AI system inventory | **Does Not Meet** — no registry of which cassettes are live where, for whom | A maintained inventory (cassette name, domain, deployment, risk tier) | No change |
| B1 | Continuous, lifecycle-wide risk management | **Partially Meets** — the project has *lived* an unusually real iterative audit cadence (Phase 1 → roadster → twin → red-team), but it's ad hoc, not a scheduled recurring process | A named cadence (e.g. quarterly) with a defined scope checklist, not "whenever a session happens" | No change |
| B2 | Risk proportionate to materiality | **Does Not Meet** — every cassette gets the same governance rigor regardless of stakes; no tiering | A declared risk tier per cassette (e.g. IVR vs. banking) with tier-appropriate rigor | No change |
| C1 | Data governance & quality | **Untested this session** | A live test proving training/reference data provenance and quality checks | No change |
| C2 | Bias identification/mitigation | **Partially Meets** — `MODEL_CARD.md` documents a real testing methodology and a defensible domain-specific argument (IVR intent = queue choice, no protected attributes touch the decision) *for the IVR cassette specifically* — but the methodology has never been executed or automated. Confirmed by grep: zero bias-audit code exists anywhere in the repo. The banking cassette has no equivalent argument or test at all | The documented methodology actually run against real decision data, on a schedule, for every cassette — not just described | No change |
| D1 | Technical documentation | **Meets** — `COMPLIANCE.md`, `MODEL_CARD.md`, `AUDIT_PLAYBOOK.md` are substantive, current, and — notably — *honestly self-disclose* H3/H4/H5/F-H/F-I as known limitations rather than hiding them | Keep it current as the twin and future fixes land (it's currently ahead of some code — e.g. discloses H4 before this session's live confirmation) | No change |
| E1 | Automatic event logging | **Meets** — every governed decision is written to the ledger automatically, no manual step | — | No change (already solid) |
| E2 | Decision record content (who/what/when/reasoning/version) | **Meets** for input/output/reasoning/policy-parameters/cassette-version. **Does Not Meet** for model identity (see K1) | Add the missing model field | No change to this item specifically (see K1) |
| E3 | Tamper-evident logs | **Does Not Meet at the engine level, confirmed unchanged this session** — a full chain rewrite (H3) and a full wipe (H5) both still verify clean via `verify_chain()` alone, live-executed against current code | An independent party holding a copy the operator cannot alter | **Meets for H3/H5-class tampering** — live-executed: forged the primary chain and wiped primary rows using only the app's own DB credential; `verify_chain()` alone still said "clean" both times, but comparing the (forged/wiped) primary against the twin's already-shipped, untouched replica copy flagged every affected row (`clear_hash_mismatch` / `extra_on_replica_absent_on_primary`), verdict `FINDINGS`. **Does NOT close H4** — see below |
| E4 | Minimum retention (7yr / sector max) | **Untested** — no retention-enforcement code found | A live test proving old records can't be pruned before the retention floor | No change |
| F1 | Advance notice to affected individuals | **Does Not Meet** — no consumer-facing notice mechanism exists; Sentinel governs a backend decision, nothing tells the caller "an AI evaluated you" | A notice/consent touchpoint wired into the calling application | No change |
| F2 | AI-generated content labeling | **N/A** — Sentinel doesn't generate consumer-facing content | — | — |
| G1 | Specific, non-generic adverse-action reason | **Does Not Meet** — the `reasoning` field is free-text from the LLM with zero structure or specificity validation; nothing distinguishes a compliant "principal reason" from a generic bucket answer | A schema-validated reason-code mapping from decision inputs to ECOA-style specific reasons, tested against real denials | No change |
| G2 | Meaningful lay explanation | **Partially Meets** — a `reasoning` string exists and is stored, but nothing validates it's actually meaningful to a lay person vs. a technical restatement | Human-readability testing against real decisions | No change |
| H1 | Meaningful human oversight (genuine override capability) | **Does Not Meet — self-disclosed in `COMPLIANCE.md` itself**: *"There is currently no built-in mechanism to supersede or annul a past decision within Sentinel — a reviewer who disagrees acts outside the system."* | A supported override/annul function, logged as its own ledger event | No change |
| H2 | Contestability & redress path | **Does Not Meet** — no complaint/appeal mechanism exists | A defined path with response-time SLA | No change |
| I1 | Accuracy, robustness, adversarial resilience | **Partially Meets** — fail-closed behavior is solid (see I2), but no adversarial-ML robustness testing (data drift, adversarial input crafting) has been run against the classifier itself | Ongoing drift/robustness testing with a documented cadence | No change |
| I2 | Fail-closed on error | **Meets, strongly** — re-executed live this session: 10/10 adversarial governor outputs (non-JSON, wrong types, empty response, transport exception, prompt-injection-in-reasoning) all fail closed. Unchanged from the original Phase 1 finding | — | No change (already solid) |
| J1 | Post-market/ongoing monitoring | **Partially Meets** — Prometheus metrics exist (decision rate, approval rate, error rate) which is real monitoring infrastructure, but no automated drift-detection or bias-monitoring loop consumes it | Alerting tied to those metrics against defined thresholds | No change |
| J2 | Change control for model/logic updates | **Does Not Meet** — no predetermined-change-control-style process; a cassette or the governor logic can change with no gate | A documented, tested change-control process (FDA PCCP is the reference pattern) | No change |
| K1 | Model/version identity per decision | **Does Not Meet, confirmed unchanged this session** — the decision record has zero model-identity fields; live re-check: `sorted(d.keys()) = ['confidence', 'governed', 'parse_failed', 'reasoning', 'risk_level', 'safe']`. `self.model` is hardcoded and simply never makes it into the record | Record `model` + the API response's actual served-model field in every decision | No change — this is an engine fix, not a witness-layer fix |
| L1 | Vendor/third-party responsibility doesn't transfer | **N/A** — Sentinel is the governance vendor in this relationship, not a deployer of someone else's AI. Becomes relevant to how *Sentinel's own customers* use it, not to Sentinel itself | — | — |
| M1 | Incident reporting | **Does Not Meet** — decisions are logged, but there's no defined "serious incident" trigger or reporting workflow | A defined incident classification + reporting path | No change |
| N1 | Adverse-action specific-reason mechanism (heightened sector requirement) | **Does Not Meet, confirmed unchanged this session** — same root cause as G1; grepped the full current codebase for any ECOA/adverse-action/principal-reason mechanism, found none | Same bar as G1, applied specifically to lending/insurance/employment/housing decisions | No change |

---

## H4 — the one that matters most from this session

**Forged the cassette policy content on the primary while leaving `cassette_hash`/`current_hash` untouched — exactly reproducing the original H4 finding — with the twin fully deployed and already holding an honest copy of that same cassette snapshot.**

`verify_chain()` alone: still says clean, as expected.

**The twin: also said clean.** `verdict: "CLEAN"`, live-executed.

Root cause, confirmed by reading `twin_detector.py`: the customer's replica genuinely holds the honest `cassette_snapshot` — it was shipped there before the forgery, sitting in their own storage right now. But nothing in the automated detection pipeline (`run_detection`) ever compares it against what the primary currently shows. The primary-vs-replica pass only compares hash-chain values (`current_hash`/`previous_hash`), and the replica's own internal-consistency check (`deep_verify_row`) only confirms the replica's copy matches *its own* stored hash — never the live primary.

The data needed to close this gap is already at the customer's site. The wiring to use it isn't built yet. That's a scoped fix — add a snapshot-content comparison to `run_detection` — not a redesign, and probably the single highest-leverage next piece of work on the witness side specifically.

---

## Three things worth saying plainly

**(a) What the engine already exceeds, no twin required:** I2 (fail-closed) is the standout — 10/10 adversarial governor failure modes correctly reject, live-tested twice now (original Phase 1 and this session), with zero drift. That's a genuinely hard property to hold and Sentinel holds it.

**(b) What the twin does NOT fix, so it doesn't quietly become "someone else's problem" once the witness work feels done:** everything about bias testing (C2), human override (H1), contestability (H2), adverse-action specificity (G1/N1), model identity (K1), change control (J2), and incident reporting (M1) is untouched by the witness architecture. The twin is a proof-of-non-tampering layer. It was never going to fix "the reasoning field has no ECOA structure" or "nobody can veto a bad decision" — those are engine and process gaps, and they're the majority of what's still red on this table.

**(c) If I could only fix one thing before more witness work:** close H4. It's the one place where the twin's own design *almost* closes a hole and doesn't, and it's a small, scoped patch rather than new architecture — the highest ratio of effort to credibility gained on this entire list.
