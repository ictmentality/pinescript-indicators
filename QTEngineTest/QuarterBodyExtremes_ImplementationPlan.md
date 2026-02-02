# Quarter Body Extremes (BH/BL) — Implementation Plan (Codex)

## Goal
Add **quarter body extremes** (and timestamps) to fixed cycles:

- **Daily**
- **m90**
- **Micro**
- **Nano**

Definitions per bar `i` in a quarter:
- `bodyHigh(i) = max(o[i], c[i])`
- `bodyLow(i)  = min(o[i], c[i])`

Definitions per quarter:
- `BH = max_i bodyHigh(i)`
- `BL = min_i bodyLow(i)`
- `bhTs` = timestamp of **first** bar that set `BH`
- `blTs` = timestamp of **first** bar that set `BL`

Constraints:
- **No new `request.security()` calls**
- Pine v6 type consistency (all branches return same types; use typed `na`)
- Do **not** use identifier `trueOpen` (reserved QT language keyword); use `actualOpen*` if needed elsewhere

---

## Phase 0 — Plumbing only (compile clean)
### 0.1 Extend `QuarterRecord`
Add fields:
- `float bh`
- `float bl`
- `int   bhTs`
- `int   blTs`

### 0.2 Update all constructors / initializers
Update every `QuarterRecord.new(...)` and “empty quarter” builder:
- `qt_state_new()`
- `f_make_empty_q(...)`
- any other `QuarterRecord.new(...)` call sites

Defaults:
- `bh/bl/bhTs/blTs` start as `na` (typed).

**Exit criteria:** compiles with no missing arguments/references. No behavior change required yet.

---

## Phase 1 — Core logic in `f_q_apply_bar(...)` (single source of truth)
### 1.1 Update `f_q_apply_bar(QuarterRecord qIn, int t, float o, float h, float l, float c, bool isStartBar)`
Per bar:
- `barBh = max(o, c)`
- `barBl = min(o, c)`

Initialize (when quarter initializes; match your existing semantics: `not q.has` and/or `isStartBar`):
- `q.bh := barBh; q.bhTs := t`
- `q.bl := barBl; q.blTs := t`

Update (strict comparisons only; ties keep earliest timestamp):
- if `na(q.bh)` or `barBh > q.bh`:
  - `q.bh := barBh; q.bhTs := t`
- if `na(q.bl)` or `barBl < q.bl`:
  - `q.bl := barBl; q.blTs := t`

**Exit criteria:** BH/BL populate anywhere `f_q_apply_bar` is used (even if chart-TF sourced).

---

## Phase 2 — Make Micro/Nano BH/BL chart-TF invariant (aligned override path)
Micro/Nano must have BH/BL sourced from the **same aligned path** as their quarter H/L/C (30s for Micro, 5s for Nano).

### 2.1 Ensure aligned quarter aggregates `aq1..aq4` carry BH/BL + timestamps
Wherever aligned bars are folded into `aq1..aq4`, ensure that update also computes BH/BL and timestamps using the **same rules** as Phase 1:
- Either call `f_q_apply_bar` on `aq*`, **or**
- replicate the BH/BL logic there (not preferred; avoid duplication if possible).

### 2.2 Copy BH/BL in Phase-3 overwrite for Micro/Nano
Where Micro/Nano overwrite quarter fields from aligned aggregates (`aq* → q*`), also overwrite:
- `q*.bh := aq*.bh`
- `q*.bl := aq*.bl`
- `q*.bhTs := aq*.bhTs`
- `q*.blTs := aq*.blTs`

**Exit criteria:** Micro/Nano BH/BL do **not** change when switching chart TF (30s ↔ 1m/5m, 5s ↔ 15s/1m).

---

## Phase 3 — Extend to Daily + m90
Daily/m90 should follow the same principle:
- If they already use aligned aggregates for quarter H/L/C, copy BH/BL from those aggregates too.
- If they don’t, BH/BL will remain chart-TF dependent until aligned override is wired for those cycles (reuse existing aligned ingest; do not add requests).

**Exit criteria:** Daily + m90 BH/BL behavior is correct and consistent with the cycle’s sourcing strategy.

---

## Acceptance Tests (minimal)
1) **Micro on 30s chart**
   - Manually identify bar with max `max(o,c)` and min `min(o,c)` within a quarter.
   - Verify `q#.bh/q#.bhTs` and `q#.bl/q#.blTs` match (first occurrence).

2) **Micro invariance**
   - Flip chart TF to 1m/5m.
   - BH/BL values and timestamps must remain unchanged (if Micro uses aligned overrides).

3) **Nano on 5s chart**
   - Same as Micro, then flip to 15s/1m and verify invariance.

4) **Tie handling**
   - If two bars share identical bodyHigh/bodyLow, timestamp must remain the **first** occurrence.

---

## Notes for Codex
- Implement in order: **Phase 0 → Phase 1 → Phase 2 (Micro/Nano) → Phase 3 (Daily/m90)**.
- Keep changes small and compiling at each phase.
