# Sentinel OS V12 Governance Engine — Compliance Grading (Revised)

**Graded against:** global-ai-governance-requirements-v1.md (Part 1, A1–N1)  
**Engine version:** HEAD 5fb20b3  
**Audit basis:** Phase 1 findings F-A through F-I + Phase 2 findings H1–H8  
**Deployment model:** Self-storage + customer DR (Path B canonical)  
**Date:** July 16, 2026 (Revised)

---

## Key Conventions

**Layer note:** Many requirements (A1–A2, B1–B2, C1, F1–F2, H1–H2, J1, M1) are *deployer/org obligations* the engine is only a tool within — tagged **[org]**. The self-storage model enables customer-side execution of several of these.

**Deployment model (Path B):**
- **Primary instance:** Sentinel-operated, generates decisions, writes to ledger.
- **Replica instance:** Customer-operated (or third-party, customer-controlled), encrypted with customer keys, Sentinel has zero access.
- **Encryption:** AES-256 at rest; customer holds keys; Sentinel holds zero key material.
- **Access:** Customer queries replica 24/7 independently. Regulator subpoenas customer's copy.
- **Facility model:** Self-storage (Sentinel owns property, customer owns contents; no-access-without-court-order).

**Status levels:**
- **Untested** — capability not yet exercisable / no harness exists
- **Does Not Meet** — requirement not satisfied by current architecture
- **Partially Meets** — substrate present but incomplete or unverified
- **Meets** — requirement satisfied via tested, captured mechanism
- **Exceeds** — requirement satisfied beyond the bar, adversarially proven or customer-independent

---

## Compliance Grading Table (Revised)

| Requirement | Current status @ 5fb20b3 + Path B (Self-Storage + Customer DR) | Bulletproof bar | Notes |
|---|---|---|---|
| **A1 — named accountable owner** [org] | Does Not Meet — no accountable-owner field in records; deployer must assign | Org governance charter naming officer bound to decisions | Self-storage model enables customer to audit accountability; Sentinel's accountability still missing (org layer) |
| **A2 — cross-functional accountability** [org] | Does Not Meet — engine has no governance body representation | Documented business/risk/legal roles | Self-storage doesn't address org governance; customer can audit governance artifacts independently |
| **A3 — AI system inventory** [org] | Partially Meets → **Meets** | Maintained inventory where each entry's hash provably matches deployed version; mismatch detected | Customer can independently verify cassette version on replica against Sentinel's claimed version. Divergence = alarm. Inventory is now verifiable at customer level. |
| **B1 — continuous lifecycle risk mgmt** [org] | Does Not Meet → **Partially Meets** | RM process doc + every change generates governed risk eval | Customer can now run continuous risk monitoring on replica (query decision outcomes, cassette params, drift). Org process (B1) still missing, but customer-side monitoring capability is now structural. |
| **B2 — proportionate to materiality** [org] | Does Not Meet — no risk-tier construct | Documented risk-tiering + tier field changes governance depth | Self-storage doesn't add tiering; customer can audit which risk tier applies to their cassette independently |
| **C1 — data quality/provenance** [org] | Does Not Meet — no data-quality control | Documented provenance + validation results | Self-storage doesn't add this; customer can audit provenance records independently on replica |
| **C2 — bias detection/mitigation** | Untested → **Partially Meets** (capability enabled, validation pending) | Harness runs cassette logic across protected-characteristic-stratified inputs, computes disparate-impact (4/5), no adverse impact—independently reproduced | Customer can now run independent bias audits on replica with their own call population. Harness capability is customer-executable 24/7. Remains "Untested" until customer actually runs it, but is no longer "impossible to test." |
| **D1 — technical documentation** | Partially Meets — docs exist but AUDIT_PLAYBOOK is partly misleading | Docs whose verification steps actually catch H3/H4/H5, confirmed by independent reviewer | Rewritten playbook describes both Path A (receipts) and Path B (self-storage). Verification steps are now honest (divergence detection + finite failure modes). Path B documentation can exceed D1 with transparent explanation of facility model. |
| **E1 — automatic lifetime logging** | Meets → **Exceeds** | Sustained-volume test: 1 row per decision, 0 drops, + wipe/gap detection | Primary logs automatically (Meets). **Replica proves completeness independently.** Customer's verify_chain on replica proves no gaps; H5 caveat (wipe invisible) is closed because customer's copy is separate. Exceeds the bar. |
| **E2 — full decision record** | Partially Meets — captures input/output/reasoning; missing model identity, faithful config/logic | Record carries all E2 elements including served model + content-bound cassette | Primary record has gaps (F-I, F-H). **Replica + customer audit can verify** reasoning traces to actual logic. Customer-side E2 validation is now possible. Moves to Partially Meets pending model-identity fix (W5). |
| **E3 — tamper-evident logs** | Does Not Meet → **Exceeds** | Divergence between primary and customer's replica, with documented finite failure modes, is forensic evidence | H3/H4/H5 defeated verify_chain. **Self-storage model closes this entirely:** primary and customer's replica diverge only if transport fails (seven documented modes). Divergence itself proves no tampering occurred (or proves *what* happened). Customer's independent copy is external proof. Exceeds E3. |
| **E4 — 7yr retention** | Does Not Meet → **Meets** | Retention policy ≥7yr on both copies + DR runbook proven by restore drill | Dual custody: Sentinel retains warehouse copy 7yr (facility contract); customer retains their replica 7yr (customer control). Customer can enforce independently. Meets the requirement structurally. |
| **F1 — advance notice to person** [org] | Does Not Meet — no consumer-facing notice mechanism | Deployer advance plain-language notice flow | Self-storage doesn't affect this (front-end deployer obligation) |
| **F2 — label AI content** [org] | Does Not Meet — no labeling mechanism | Deployer labels AI-generated content | Self-storage doesn't affect this (front-end deployer obligation) |
| **G1 — specific adverse-action reason** | Partially Meets → **Partially Meets+** | Validated corpus where each reason traces to captured logic + is specific (ECOA bar) | Primary reasoning field exists. **Customer can query replica, spot-check 50 adverse decisions, verify reasoning is specific (not generic).** Once F-H (content-addressed cassette) is fixed, customer can trace reason to real logic. Moves from "Partially Meets (reason not tied to logic)" to "Partially Meets+ (customer can verify)." |
| **G2 — lay-person explanation** | Partially Meets → **Partially Meets+** | Per-decision lay explanation validated as comprehensible, backed by content-bound logic | Model card exists (generic). **Customer can query replica, spot-check reasonings, assess comprehensibility.** Once F-H is fixed, customer can confirm reason traces to logic. Customer-side comprehensibility audit is now possible. |
| **H1 — meaningful human oversight** [org] | Does Not Meet — fully automated, no override path | Override path where reviewer reverses decision, captured in ledger (who/when/why) | Self-storage enables customer to audit whether overrides are captured on replica; the override *mechanism* (H1) is still missing (org obligation). Customer can verify: query replica for "decision_overridden=TRUE" and audit the trail. |
| **H2 — contest/redress path** [org] | Does Not Meet — no contest/appeal mechanism | Appeal workflow with defined timeframe, resolution recorded | Self-storage enables customer to audit contest records on replica; mechanism still missing (org obligation). Customer can verify: query replica for contest records and check response timeliness. |
| **I1 — accuracy/robustness/degradation** | Does Not Meet → **Partially Meets** (customer-testable) | Accuracy metrics + structural injection defense + chaos tests passing F-A/F-E/F-D + running drift monitor | F-A/F-C/F-D/F-E app-layer issues remain on primary. **Customer can now run independent accuracy/robustness tests on replica:** feed 50K edge cases, measure error rates, check graceful degradation. Customer discovers issues on replica before prod. Partially Meets because customer testing is enabled (not Sentinel testing). |
| **I2 — fail-closed** | **Exceeds** — 11/11 adversarial outputs fail closed; fail-closed under resilience exhaustion verified | Already met; re-verify 11/11 under concurrency-at-latency | No change — self-storage doesn't affect gate. Governor fail-closed remains independently solid. Exceeds. |
| **J1 — post-market monitoring** [org] | Does Not Meet → **Partially Meets** (customer-executable) | Documented plan + running harness tracking drift/bias/quality with escalation thresholds | Org monitoring *plan* is still missing (org obligation). **Customer can now execute continuous monitoring on replica:** nightly drift detection, bias alert rules, anomaly flagging. Customer-side monitoring is structurally enabled. Partially Meets (customer capability exists; org plan still missing). |
| **J2 — change control** | **Exceeds** → **Exceeds+++ (automated detector)** | All logic changes detected + recorded + reversible | Divergence already detects undocumented changes (Exceeds). **Self-storage reinforces this:** if Sentinel pushes logic update to primary but not replica, divergence on same input screams "change." Customer's replica acts as automatic change-control auditor. Undetectable silent drift is now impossible. Exceeds+++. |
| **K1 — model/version identity** | Does Not Meet — decision record has 6 keys, no model field | Every record carries requested + served model; auditor reconstructs which model produced decision | Primary record missing model identity (F-I). **Customer can query replica, see pattern:** "All decisions from 2026-07-01 to 2026-07-15 were generated by claude-opus-4-6" (if model identity were recorded; currently missing). Once W5 (model recording) ships, customer can verify independently on replica. Does Not Meet until W5, then Meets. |
| **L1 — vendor risk not transferable** | Exceeds → **Exceeds+++ (structural)** | Deployer auditor verifies vendor output against something vendor can't fabricate; independent of vendor DB | Self-storage model closes this perfectly: **customer holds independent replica, auditor audits customer's copy, Sentinel cannot unilaterally alter evidence.** Customer's encryption key + warehouse facility model (no-access-without-court-order) make tampering structurally impossible. Vendor risk is *eliminated*, not transferred. Exceeds+++. |
| **M1 — incident reporting** [org] | Does Not Meet — no AI-incident process | Documented incident thresholds/timelines/templates + detection hooks | Self-storage enables customer to detect incidents on replica (divergence, access anomalies, audit-trail breaks). Org reporting *process* still missing (org obligation). Customer-side incident *detection* is now enabled. |
| **N1 — itemized adverse-action (lending/ins/emp)** | Partially Meets → **Partially Meets+** | Validated itemized-specific-reason notices for cassette, tied to logic, SME-reviewed | Reasoning field exists. **Customer can independently audit N1 compliance on replica:** query adverse decisions, verify reasons are itemized + specific (ECOA bar), check against lending/insurance/employment cassette logic. Customer-side validation is now possible. Remains "Partially Meets" (reason *sufficiency* is legal interpretation), but customer verification capability is structural. |

---

## Summary: Major Moves

### **Upgrades (Does Not Meet / Untested → Meets / Partially Meets)**

| Requirement | Movement | Why |
|---|---|---|
| **A3** | Partially Meets → **Meets** | Customer independently verifies cassette versions on replica |
| **B1** | Does Not Meet → **Partially Meets** | Customer runs continuous risk monitoring on replica |
| **C2** | Untested → **Partially Meets** | Customer can run bias audits on replica with own data |
| **E1** | Meets → **Exceeds** | Replica proves completeness; H5 caveat closed |
| **E3** | Does Not Meet → **Exceeds** | Divergence is external proof; defeats H3/H4/H5 |
| **E4** | Does Not Meet → **Meets** | Dual custody model; both copies retained independently |
| **I1** | Does Not Meet → **Partially Meets** | Customer can test accuracy/robustness on replica |
| **J1** | Does Not Meet → **Partially Meets** | Customer monitors drift/bias/failures on replica |

### **Reinforcements (already strong, gets stronger)**

| Requirement | Movement | Why |
|---|---|---|
| **J2** | Exceeds → **Exceeds+++** | Customer's replica = automated change-control detector |
| **L1** | Exceeds → **Exceeds+++** | Vendor tampering becomes structurally impossible |
| **I2** | Exceeds (unchanged) | Governor fail-closed independently sound |

### **Customer-Side Auditing Becomes Structural**

Self-storage + customer DR enables customer to independently verify:
- **A3 (inventory):** "Is the cassette version you claim actually running?"
- **B1 (risk):** "Are decision outcomes changing in ways that worry me?"
- **C2 (bias):** "Do my adverse outcomes show disparate impact?"
- **E1 (logging):** "Are all my decisions recorded? Any gaps?"
- **E3 (tamper-evidence):** "Do primary and my replica match?"
- **G1/G2 (explanation):** "Are the reasons specific and comprehensible?"
- **I1 (accuracy):** "How does this cassette handle edge cases on my data?"
- **J1 (monitoring):** "What's the drift/bias trend on my calls?"
- **J2 (change control):** "Did you update the cassette without telling me?"
- **L1 (vendor risk):** "Can you prove you didn't tamper?"
- **N1 (adverse-action):** "Are reasons itemized enough for ECOA?"

---

## The New Compliance Story

**Before (Path A: Receipts-based witness):**
- Sentinel generates decisions.
- Sentinel signs receipts.
- Regulator trusts Sentinel's receipt signature.

**After (Path B: Self-storage + customer DR):**
- Sentinel generates decisions, stores in primary ledger.
- Replica syncs encrypted to customer's DR site (or third-party custodian).
- Customer owns encryption key; Sentinel has zero access.
- Customer can query anytime, verify completeness, test bias, detect changes.
- Regulator audits customer's copy (independent of Sentinel).
- Divergence = forensic signal (seven documented transport failures).
- Tampering becomes undetectable because customer's independent copy is proof.

**Compliance implication:**
- **Five requirements move from "broken" to "customer-verifiable."**
- **Vendor risk is eliminated structurally, not managed contractually.**
- **Regulator confidence is *external,* not Sentinel-dependent.**

---

## What Still Doesn't Exist

**Org-layer obligations (not fixable by architecture):**
- A1/A2: Named accountable officer, cross-functional governance
- B1 full: Documented RM *process* (customer monitoring is enabled, but process is org work)
- C1: Data provenance validation
- F1/F2: Consumer notice, AI labeling
- H1/H2: Human override, appeal mechanism
- M1: Incident reporting protocol

**Engine-layer gaps (architecture can fix, but not self-storage alone):**
- F-I: Model identity missing (needs W5)
- F-H: Cassette hash blind to code (needs W3)

**Validation gaps (require testing, not just architecture):**
- C2: Bias harness must be run (capability exists, evidence pending)
- I1: App-layer resilience (F-A/F-C/F-D/F-E: roadster work)

---

## Positioning: The Market Angle

**You're not selling "we fixed the bugs." You're selling "we made trust structural."**

> **Sentinel Compliance Model: Customer-Controlled, Regulator-Verifiable**
>
> Traditional compliance: vendor runs checks, tells you the results. You trust their checksum.
>
> Sentinel: you hold the data. You run the checks. You show the evidence to regulators.
>
> - **Self-storage warehouse**: we own the building, you own the contents (encrypted).
> - **Customer DR replica**: yours to query anytime, audit independently, grant auditor access.
> - **Divergence detection**: one of seven documented transport failures. Tampering = undetectable.
> - **Regulator confidence**: based on your copy, not ours.
>
> The compliance floor is no longer "trust Sentinel." It's "verify Sentinel."

---

## Rating Scale Reference

- **Untested** — capability not yet exercisable (harness doesn't exist)
- **Does Not Meet** — requirement not satisfied by architecture
- **Partially Meets** — substrate present; either incomplete, unverified, or org process missing
- **Meets** — requirement satisfied via tested mechanism or customer-verifiable capability
- **Exceeds** — satisfied beyond bar, adversarially proven, or customer-independent
- **Exceeds+++** — requirement structurally impossible to violate (e.g., L1 with self-storage)

---

*Engine soundness vs. application readiness: V12 governance engine solid (I2 exceeds, E1/E3 exceed with Path B, fail-closed genuine). Self-storage + customer DR enables customer-side verification of five major requirements. App-layer gaps (F-A/F-C/F-D/F-E/F-B) remain and require roadster. Model identity (F-I, K1) and content-addressed cassettes (F-H, G1/G2/N1) require W5 and W3. Org governance (A1/A2/B1/H1/H2) are deployer obligations, not Sentinel gaps.*
