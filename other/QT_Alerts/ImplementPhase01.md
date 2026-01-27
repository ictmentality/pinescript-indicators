/QT_Alerts/Setups/Micro_Q4_Continuation_v1/IMPLEMENT_PHASE_01_ARMED_ONLY.md

# IMPLEMENTATION PHASE 01 — Armed Alert Only (Setup-Only v0)

## Goal
Implement the first alert step only:
- Alert: QT Setup Armed (generic message)
- Policy: Sticky Armed
- Frequency: One armed per Micro cycle (no re-arm until reset)

No Entry/Stop/Target logic in this phase.

---

## Inputs / Dependencies

### From QTEngine (required)
- micro_q (1..4)
- micro_end_ts

### Indicator-side context (required)
- h4_c ∈ {1,2,3,4} computed internal logic (Define later)

Recommended daily quarter map (time model):
- C1: 18:00–00:00
- C2: 00:00–06:00
- C3: 06:00–12:00
- C4: 12:00–18:00

Timezone:
- Use a single chosen timezone (input), e.g. America/New_York or UTC+2.
- Compute h4_c by time-of-day classification in that timezone.

### From native-TF event feeds (stubbed OK for v0)
- 30s: ssmt_q3q4_ts_candidate (int or na)
- 15m: smtf_ts_candidate (int or na)

> Note: In v0 these can come from debug inputs instead of real detectors.

---

## Persistent State (latched; reset at boundaries)

### Setup latch
- armed: bool (default false)
- armed_ts: int (na until armed)
- h4_c_at_arm: int (na until armed)
- micro_end_ts_at_arm: int (na until armed)

### Prerequisite latches
- ssmt_q3q4_ts: int (na until first seen)
- smtf_ts: int (na until first seen)

### One-per-cycle lock
- armed_cycle_id: int (use micro_end_ts as the cycle identifier)

---

## Arm Condition (evaluated only when not already armed)
Arm when ALL are true:
1) micro_q == 4
2) h4_c ∈ {3,4} (checked ONLY at arm-time; sticky thereafter)
3) ssmt_q3q4_ts exists (not na)
4) smtf_ts exists (not na)
5) Ordering guard: smtf_ts >= ssmt_q3q4_ts

On arm:
- set armed = true
- set armed_ts = max(ssmt_q3q4_ts, smtf_ts)
- set h4_c_at_arm = h4_c
- set micro_end_ts_at_arm = micro_end_ts
- set armed_cycle_id = micro_end_ts
- fire alert: "QT Setup Armed" / "Micro_Q4_Continuation_v1 armed"

---

## Reset Rules (hard reset only)
Reset everything (including prerequisite latches) when either:
1) Micro cycle rollover: time_close > micro_end_ts_at_arm
2) Daily reset boundary (hook later if needed)

Sticky Armed:
- After arming, do NOT invalidate based on later h4_c changes.

---

## Debug Mode (recommended for Phase 01)
Optional debug inputs to force prerequisites without real detectors:
- dbg_ssmt_q3q4_fire (edge) → sets ssmt_q3q4_ts
- dbg_smtf_fire (edge) → sets smtf_ts
Optional gates:
- dbg_force_micro_q4
- dbg_force_h4_c34

---

## Acceptance Criteria
1) Arms exactly once per Micro cycle.
2) Sticky Armed: h4_c changes after arming do not invalidate or re-arm.
3) Resets cleanly at micro_end_ts; next Micro cycle can arm again.
4) Ordering guard enforced: smtf_ts must be >= ssmt_q3q4_ts.
