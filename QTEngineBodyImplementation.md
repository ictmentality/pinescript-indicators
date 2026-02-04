# QTEngine Body High/Low Requirements (Quarter + Timestamp)

## Goal

Implement **quarter body extremes** (body high/low + timestamps) inside QTEngine so all
consumers can reuse them without per-indicator recomputation. This is required for
HSSMT (body-based divergence) and any future body-based logic.

## Scope

- **In scope:** Extend `QuarterRecord` to track body extremes; aggregate per bar; carry
  forward into prior quarters; keep aligned records consistent when overriding OHLC.
- **Cycles:** Daily, m90, Micro, Nano.
- **Out of scope:** Any indicator-level HSSMT logic (signals, latches, alerts).

## Constraints

- **No new `request.security()` calls.**
- Pine v6 type consistency: all branches return the same types; use typed `na`.
- Do **not** use identifier `trueOpen` (reserved QT keyword); prefer `actualOpen*` if needed.

## Definitions

- **Body High (BH):** `max(open, close)` per bar; quarter BH is the max of bar BHs.
- **Body Low (BL):** `min(open, close)` per bar; quarter BL is the min of bar BLs.
- **BH Timestamp (bhTs):** `time` of the **first** bar that set the current BH
  (updates only on a strict higher BH; ties keep earliest).
- **BL Timestamp (blTs):** `time` of the **first** bar that set the current BL
  (updates only on a strict lower BL; ties keep earliest).
- **Timestamp convention:** Use bar open `time` (`t`), matching `hTs/lTs`.

## Data Model Changes

### QuarterRecord (required fields)

Add four **required** fields:

- `float bh`  — quarter body high
- `float bl`  — quarter body low
- `int bhTs`  — timestamp of bar that set `bh`
- `int blTs`  — timestamp of bar that set `bl`

### Constructor updates (mandatory)

Update all `QuarterRecord.new(...)` call sites to include the new fields:

- `qt_state_new()` → `nilQ`: set `bh/bl/bhTs/blTs` to `na`
- `f_make_empty_q(qStart)`: set `bh/bl/bhTs/blTs` to `na`

## Aggregation Logic

### Function: `f_q_apply_bar(...)`

Per bar:

- `barBH = max(o, c)`
- `barBL = min(o, c)`

On first bar of quarter (`not q.has` and/or `isStartBar`, matching existing semantics):

- `q.bh := barBH`
- `q.bl := barBL`
- `q.bhTs := t`
- `q.blTs := t`

On subsequent bars (strict comparisons only; ties keep earliest):

- If `na(q.bh)` or `barBH > q.bh`:
  - `q.bh := barBH`
  - `q.bhTs := t`
- If `na(q.bl)` or `barBL < q.bl`:
  - `q.bl := barBL`
  - `q.blTs := t`

## Aligned Aggregation Requirements (Micro/Nano invariance)

All cycles body extremes must be sourced from the same **aligned aggregates** that drive
their quarter OHLC (m15 for Daily, m5 for m90, 30s for Micro, 5s for Nano).

- Wherever aligned bars are folded into `aq1..aq4`, ensure BH/BL + timestamps are computed
  using the **same rules** as `f_q_apply_bar`:
  - Prefer calling `f_q_apply_bar` on `aq*`, or
  - Replicate the BH/BL logic there (not preferred; avoid duplication).

## Alignment/Override Requirements

Anywhere QTEngine overwrites OHLC from aligned records (`aq*` → `q*`), **also copy**
body extremes and timestamps:

- `qX.bh := aqX.bh`
- `qX.bl := aqX.bl`
- `qX.bhTs := aqX.bhTs`
- `qX.blTs := aqX.blTs`


## Carry-Forward Behavior

No new logic required in:

- `f_q_clear_evts`
- `f_q_finalize`
- `f_finalize_and_roll`

Because the full `QuarterRecord` is rolled into `prev1/prev2`, the new fields will
roll automatically with existing behavior.

## Daily + m90 Notes

- If Daily/m90 already use aligned aggregates for quarter OHLC, copy BH/BL from those
  aligned records as well. (They all should, please bring this to my attention if this is not the case)


## Expected Consumer Usage (Context Only)

Once implemented, indicators (e.g., HSSMT) should use:

- `prevQ.bh` / `prevQ.bl` as prior-quarter references
- `curQ.bh` / `curQ.bl` as current-quarter progress
- `bhTs` / `blTs` for timestamped debugging or display

No per-indicator recomputation of body extremes should be needed.

## Acceptance Tests (Minimal)

1) **Micro on 30s chart**
   - Identify bar with max `max(o,c)` and min `min(o,c)` in a quarter.
   - Verify `q#.bh/q#.bhTs` and `q#.bl/q#.blTs` match the first occurrence.

2) **Micro invariance**
   - Switch chart TF to 30s/1m/3m.
   - BH/BL values and timestamps remain unchanged.

3) **Nano on 5s chart**
   - Repeat Micro checks; switch to 5s/15s/ and verify invariance.

4) **Tie handling**
   - If two bars share identical bodyHigh/bodyLow, timestamp remains the **first** occurrence.

## Open Questions (Please confirm)

None — alignment scope confirmed for all fixed cycles (Daily, m90, Micro, Nano).
