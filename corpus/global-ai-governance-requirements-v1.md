# Global AI Governance Requirements — Blended Compliance Floor

**Prepared for:** Sentinel OS / Cassette OS design reference
**Date:** July 16, 2026
**Method:** Each requirement below is synthesized from the actual binding or authoritative text of the frameworks listed after it. Where frameworks phrase the same underlying obligation differently, the wording here is drafted to satisfy every cited version — not just the strictest one. Frameworks not yet in force, or withdrawn, are flagged explicitly rather than blended in as if they were live law.

---

## Frameworks covered (20)

| # | Framework | Jurisdiction | Status as of July 2026 |
|---|---|---|---|
| 1 | EU AI Act (Reg. 2024/1689), Arts. 9–15, 12, 26 | EU | High-risk obligations apply from Aug 2, 2026 (Digital Omnibus may extend some deadlines — not yet adopted) |
| 2 | GDPR Article 22 (+ Arts. 13–15) | EU | Binding, in force |
| 3 | NIST AI Risk Management Framework 1.0 | US (federal) | Voluntary; de facto baseline |
| 4 | ISO/IEC 42001:2023 (AIMS) | Global | Voluntary, certifiable |
| 5 | CFPB / ECOA & Regulation B (12 CFR 1002.9) | US (federal) | Statute binding; **AI-specific circulars 2022-03/2023-03 withdrawn May 12, 2025** — underlying adverse-action duty unchanged |
| 6 | NAIC Model Bulletin on AI Systems by Insurers | US (state, insurance) | Adopted in 25+ states; principles-based, not a model law |
| 7 | FDA AI/ML-Based SaMD guidance (GMLP, PCCP) | US (federal, medical devices) | Binding for device clearance pathway |
| 8 | NYC Local Law 144 (AEDT Bias Audit Law) | US (NYC, employment) | Binding, enforced since July 2023 |
| 9 | Colorado AI Act (SB 24-205) | US (Colorado) | Effective date pushed to June 30, 2026 |
| 10 | China: Generative AI Measures + Algorithm Recommendation Provisions + Deep Synthesis Regulations (CAC) | China | Binding |
| 11 | UK: UK GDPR/DUAA 2025 (Arts. 22A–22D), ICO AI & ADM Code (final expected Summer 2026), sector regulators (FCA, MHRA) | UK | Partially binding; ICO Code pending finalization |
| 12 | South Korea AI Basic Act | South Korea | Effective Jan 22, 2026 (1-year enforcement grace period) |
| 13 | Singapore Model AI Governance Framework (+ GenAI/Agentic extensions, MAS AI-MRM) | Singapore | Voluntary except MAS guidance for regulated financial institutions |
| 14 | Brazil Bill 2338/2023 ("Marco Legal da IA") | Brazil | **Not yet law** — Senate-approved, pending Chamber of Deputies vote |
| 15 | FINRA Rule 3110 + 2026 Annual Regulatory Oversight Report (GenAI section) | US (broker-dealers) | Guidance binding via existing rule; report sets exam expectations |
| 16 | SR 26-2 — Federal Reserve/OCC/FDIC Model Risk Management Guidance | US (banks >$30B, federal) | Effective April 17, 2026; **explicitly excludes GenAI/agentic AI from formal scope**, but requires institutions to govern them under existing risk-management principles |
| 17 | HIPAA Security Rule + Business Associate Agreement requirements | US (healthcare) | Binding |
| 18 | Japan AI Promotion Act + AI Guidelines for Business | Japan | Act effective June 4, 2025; guideline-driven, no penalties |
| 19 | Canada — Artificial Intelligence and Data Act (AIDA) | Canada | **Died in Parliament, Jan 2025 — not law.** Listed for completeness; do not build to it as binding |
| 20 | EEOC / Title VII disparate-impact doctrine (via NYC LL144's four-fifths rule and general employment law) | US (federal) | Binding, general-purpose (not AI-specific) |

*Cross-cutting references informing several of the above: OECD AI Principles (2024 revision, 46 countries); Council of Europe Framework Convention on AI (2024, first binding international AI treaty).*

---

## Part 1 — The Blended Universal Requirements

These are the requirements that recur, in substance, across most or all of the above frameworks. Each is phrased to satisfy every cited source's wording simultaneously.

### A. Governance & Accountability

**A1. Named, accountable ownership.** The organization must maintain a documented governance structure for each AI system in regulated use, with a named individual or body (senior officer, board committee, or designated compliance role) accountable for its risk posture — not merely a technical owner. *[EU AI Act Art. 17 (QMS); NAIC AIS Program; ISO 42001 Cl. 5; UK draft Bill "AI Responsible Officer"; Colorado AI Act reasonable-care duty; FINRA Rule 3110]*

**A2. Cross-functional accountability structure.** Governance must draw on more than one discipline — at minimum, the business/product owner, a risk or compliance function, and (where personal data or consequential decisions are involved) legal — each with defined scope of authority. *[NAIC Model Bulletin; ISO 42001 Cl. 5.3; NIST AI RMF Govern function]*

**A3. Documented AI system inventory.** The organization must maintain an inventory of AI systems in regulated use, including purpose, risk classification, and version/configuration history. *[EU AI Act Art. 71 (DB registration for high-risk); SR 26-2 (model inventory); ISO 42001 Cl. 4/8; UK ATRS]*

### B. Risk Management (Continuous, Lifecycle-Wide)

**B1. A documented, continuous risk-management process** must run across the full system lifecycle — design, validation, deployment, monitoring, and retirement — not as a one-time gate. It must identify and analyze known and reasonably foreseeable risks (including under conditions of reasonably foreseeable misuse), estimate and evaluate them, and apply targeted mitigations, with residual risk judged acceptable and documented as such. *[EU AI Act Art. 9; NIST AI RMF (Map/Measure/Manage); ISO 42001 Cl. 6/8; Colorado AI Act "reasonable care" duty; NAIC AIS Program risk controls]*

**B2. Risk assessment must be proportionate to materiality/exposure**, not uniform across all systems — low-impact tools may receive lighter governance, high-impact/high-risk systems require full rigor. *[SR 26-2 materiality construct; NIST AI RMF profiles; Colorado AI Act "high-risk" tiering; Brazil PL 2338 three-tier risk classification (pending)]*

### C. Data Governance & Quality

**C1. Training, validation, and reference data must be relevant, representative, and — to the extent possible — free of errors and complete**, with documented provenance and, where personal data is involved, a lawful basis and minimization discipline. *[EU AI Act Art. 10; GDPR Arts. 5, 25; China Generative AI Measures (training data legality); ISO 42001 Cl. 8]*

**C2. Bias identification, detection, and mitigation in data and outputs is mandatory** for systems making or materially influencing decisions about individuals, tested against protected characteristics where applicable. *[EU AI Act Art. 10(2)(f); NYC LL144 bias audit; NAIC fairness/nondiscrimination; Colorado AI Act algorithmic discrimination; CFPB/ECOA disparate-impact exposure; EEOC four-fifths rule]*

### D. Technical Documentation

**D1. Technical documentation sufficient to demonstrate compliance must exist before market/production use**, describing system purpose, design choices, data sources, performance characteristics, and known limitations, and must be kept current through the system's life. *[EU AI Act Art. 11, 18; FDA GMLP; ISO 42001 Cl. 7.5; SR 26-2 model documentation]*

### E. Record-Keeping, Logging & Audit Trail (Tamper-Evident)

**E1. Automatic, system-generated event logging is required over the full operational lifetime** of any system making or materially influencing a consequential decision about a person. Manual/after-the-fact record-keeping does not satisfy this. *[EU AI Act Art. 12; HIPAA Security Rule audit controls; SOX-adjacent expectations for financial logs]*

**E2. Each logged decision record must, at minimum, capture:** who/what triggered the event, the exact input data considered, the model/algorithm version and configuration in effect at that moment, the output/decision and its stated reasoning, any human override (by whom, when, why), and a correlation ID linking it to the user-facing action. *[EU AI Act Art. 12(3); NAIC audit documentation; CFPB adverse-action decision-trail expectations; ISMS/Article-12 implementation guidance]*

**E3. Logs must be tamper-evident, not merely stored** — the framework consensus (articulated explicitly in EU AI Act commentary and implicit in HIPAA/SOX audit-integrity expectations) is that a log an operator can silently edit without detection has *zero evidentiary value* to a regulator, regardless of retention length.

**E4. Minimum retention periods** (use the longest applicable to your sector/geography): EU AI Act Art. 12/26(6) floor = 6 months; EU AI Act Art. 18 technical documentation = 10 years post-withdrawal; HIPAA = 6 years; SOX-adjacent financial practice = 7 years. *[Blended: retain decision records for no less than 7 years, or the applicable sector maximum, whichever is longer, unless a shorter floor is explicitly sufficient for your only operating jurisdiction.]*

### F. Transparency & Disclosure to Affected Persons

**F1. Individuals must be told, in advance and in plain language, when an AI system is being used to evaluate them**, what data feeds it, and what the decision affects. *[GDPR Arts. 13–15; EU AI Act Art. 13, 50; NYC LL144 10-business-day notice; Colorado AI Act pre-adverse-action notice; South Korea AI Basic Act advance-notice duty; China labeling requirements for synthesized content]*

**F2. AI-generated or AI-manipulated content must be labeled as such** where it could be mistaken for human-originated or authentic content. *[EU AI Act Art. 50; China Deep Synthesis Regulations; South Korea AI Basic Act]*

### G. Explainability / Right to Meaningful Explanation

**G1. A specific, accurate, non-generic explanation of the principal reason(s) for an adverse decision must be available to the affected individual** — "the model decided" or a broad/generic bucket reason does not satisfy this, regardless of model complexity or vendor opacity. The obligated party (not the AI vendor) bears responsibility for producing a compliant explanation. *[ECOA/Reg B (CFPB Circular 2022-03/2023-03 principles, still good law via the statute even post-withdrawal); GDPR Art. 22(3)/Recital 71; EU AI Act Art. 68c (right to explanation); Colorado AI Act principal-reason disclosure; NAIC transparency/explainability]*

**G2. The logic, significance, and consequences of automated decision-making must be describable in terms meaningful to a lay person**, balanced against legitimate trade-secret protection but never used to withhold the decision's basis entirely. *[GDPR Arts. 13–15; UK ICO "Explaining Decisions Made with AI"; EU AI Act Art. 13]*

### H. Human Oversight, Contestability & Redress

**H1. Meaningful human oversight must be available for any solely-automated decision with legal or similarly significant effect** — oversight that is genuinely capable of overriding the system's output, exercised by someone with the knowledge and authority to actually reconsider the case, not a rubber-stamp review. *[GDPR Art. 22(3); EU AI Act Art. 14; UK DUAA Arts. 22A–22D; South Korea AI Basic Act]*

**H2. Affected individuals must have an accessible path to contest a decision, request human review, and express their point of view**, with a defined response timeframe. *[GDPR Art. 22(3); EU AI Act Art. 68c; Colorado AI Act appeals process; NAIC redress expectations]*

### I. Accuracy, Robustness & Cybersecurity

**I1. Systems must be tested for accuracy, resilience to adversarial manipulation, and graceful degradation/fallback under failure**, with ongoing (not one-time) validation as data and conditions drift. *[EU AI Act Art. 15; FDA GMLP Principle 10; SR 26-2 outcomes analysis/back-testing; ISO 42001 Cl. 9]*

**I2. Fail-closed / fail-safe behavior is expected wherever a system's output governs a consequential action** — an unresolvable error, ambiguous input, or system fault should default to rejection or escalation to a human, not a default approval. *(Consensus principle drawn from FDA safety-critical design norms, EU AI Act Art. 15 robustness requirement, and NIST AI RMF "Manage" function; not a single named framework, but the direction every safety-critical regime points.)*

### J. Post-Market / Ongoing Monitoring

**J1. Deployed systems must be continuously monitored for performance drift, emergent bias, and unexpected failure modes**, with a documented plan (not ad hoc review) for what is monitored, how often, and what triggers escalation. *[EU AI Act Art. 72; FDA PCCP monitoring; SR 26-2 ongoing monitoring; ISO 42001 Cl. 9; NAIC validation/retesting]*

**J2. Material changes to a deployed model must go through a pre-defined change-control process** — undocumented drift or silent retraining is not compliant, even where the change improves performance. *[FDA Predetermined Change Control Plans; SR 26-2 model change governance; EU AI Act "substantial modification" triggers a new conformity assessment]*

### K. Model / Version Identity & Attribution

**K1. Every automated decision record must identify which specific model or algorithm version produced it**, sufficient to reconstruct what logic was in effect at decision time. This is implicit across nearly every framework's record-keeping and explainability requirements and explicit in FDA PCCP labeling and EU AI Act Art. 12(3) obligations, but is one of the most commonly under-implemented requirements in practice.

### L. Third-Party / Vendor Risk Management

**L1. Using a vendor-supplied or third-party AI system does not transfer regulatory responsibility.** The deploying organization remains accountable for validating vendor claims (not merely accepting them), securing audit/inspection rights in contracts, and ensuring vendor-supplied explainability outputs are independently verified. *[NAIC vendor diligence; CFPB "vendor told us" is not a defense; FINRA third-party risk management; EU AI Act Art. 25 value-chain responsibility]*

### M. Incident Reporting

**M1. Serious incidents or malfunctions must trigger a defined internal investigation and, where thresholds are met, a report to the relevant authority within a bounded timeframe.** *[EU AI Act Art. 62/73; FDA adverse-event reporting norms; China security-assessment/incident obligations]*

### N. Sector-Specific Adverse-Action / Denial Explanations

**N1. In lending, insurance, employment, and housing decisions specifically, a heightened, itemized, specific-reason disclosure requirement applies** beyond general transparency — this is the strictest tier across all frameworks reviewed and should be treated as the design ceiling, not the floor. *[ECOA/Reg B; NAIC adverse consumer outcomes; NYC LL144; Colorado AI Act "consequential decisions"; Fair Housing Act disparate-impact liability]*

---

## Part 2 — Notable Non-Universal Requirements (Jurisdiction-Specific "Deltas")

These do **not** generalize — building to them everywhere would over-engineer for markets that don't require them. Worth knowing so a cassette can be jurisdiction-aware rather than falsely "one-size-fits-all":

- **China only:** Pre-launch government security assessment and algorithm registration with the Cyberspace Administration of China; content must not "undermine socialist core values"; mandatory real-name user verification; data localization. No equivalent exists in any Western framework reviewed.
- **NYC LL144 only:** Bias audit must be conducted by an *independent third-party auditor* (not internal) and results *publicly posted* — most other frameworks require internal validation, not public disclosure.
- **EU AI Act only:** CE marking and formal conformity assessment (self-attested via Annex VI, or third-party via Annex VII/notified body) as a market-access gate — no other framework reviewed has an equivalent binding pre-market certification mechanism.
- **South Korea only:** Distinguishes disclosure obligations for AI output that stays within a service environment (lighter — UI notice sufficient) versus exported/downloadable synthetic content (heavier — must survive outside your system).
- **SR 26-2 (US banking) only:** Explicitly and deliberately *excludes* GenAI and agentic AI from its formal model-risk scope for now — but states the institution's own governance principles still apply. This is a live regulatory gap, not a settled floor; it is the single most relevant fact for a governance-engine vendor selling into banks, because it means there is currently no codified federal MRM checklist for exactly the kind of system Sentinel governs.
- **Brazil PL 2338:** Not yet law. Do not represent Brazil compliance as achieved; represent it as "aligned with the pending framework."
- **Canada AIDA:** Dead. Do not cite as a current requirement under any circumstance; PIPEDA (existing privacy law) is what actually applies today.

---

## Part 3 — Where Sentinel's Current Engine Sits Against This Floor

Quick cross-reference to the Phase 1 findings, for continuity — not a re-audit, just a mapping:

| Blended requirement | Sentinel status |
|---|---|
| E1–E3 (tamper-evident automatic logging) | **Gap.** Chain rewrite verifies clean (H3); wipe reports ok=True (H5). This is the single most consequential item on this entire list relative to Sentinel's positioning. |
| K1 (model/version identity per decision) | **Gap.** Confirmed F-I — no model field in the decision record. |
| E2 (input/output/reasoning per decision) | **Met.** Ledger already captures input_data, policy_parameters, reasoning, output. |
| I2 (fail-closed on error) | **Met, strongly.** 11/11 adversarial governor tests failed closed. |
| C2 (bias testing) | **Untested this phase** — no bias-audit harness has been run against a cassette yet. |
| N1 (specific adverse-action reasons) | **Partially met** — reasoning field exists, but nothing yet validates it meets ECOA's "specific and accurate" bar rather than a generic bucket. |
| L1 (vendor/third-party independent verification) | **Not applicable yet** — Sentinel is the governance vendor, not the deployer; this becomes relevant to how *Sentinel's own customers* use it. |

---

*Compiled from primary regulatory sources and current secondary analysis as of July 16, 2026. Regulatory status changes quickly — verify effective dates and any pending amendments (especially the EU Digital Omnibus delay, Colorado AI Act timeline, and Brazil PL 2338 passage) before treating any date above as final.*
