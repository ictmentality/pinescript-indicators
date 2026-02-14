# How to implment tCISD

## Purpose
This is the canonical implementation guide for adding tCISD to any indicator that imports QTEngine.

Primary goals:
- Reuse one consistent tCISD definition across scripts.
- Source all chart values from QTEngine (no raw `close/open/time` for tCISD logic).
- Keep behavior consistent with current `2CiC State` + `TPDSSMT` patterns.


## Version + Data Contract
- Import version:
  - `import Jaw1312/QTEngine/34 as qt`
- For daily-cycle models, run detection on aligned `15m`.
- Required QTEngine sources:
  - `qt.qt_daily_update(...)` for quarter context (`q1..q4`, boundaries, cycle state).
  - `qt.qt_daily_aligned_ohlc_debug()` for aligned bar triplet used by tCISD anchor/confirm.

Hard rule:
- For tCISD anchor/confirm logic, do not use raw chart `close/open/time`.
- Use QTEngine aligned values only.


## Canonical Series Pack Helper
Use this helper pattern in indicators so all downstream logic gets QTEngine-sourced values:

```pine
f_qt_pick_qr(int idx, qt.QuarterRecord q1, qt.QuarterRecord q2, qt.QuarterRecord q3, qt.QuarterRecord q4) =>
    qt.QuarterRecord out = q1
    if idx == 2
        out := q2
    else if idx == 3
        out := q3
    else if idx == 4
        out := q4
    out

f_qt_daily_c123() =>
    var qt.QTConfig cfg = qt.qt_config_default()
    var qt.CycleState st = qt.qt_state_new()
    [st0, d] = qt.qt_daily_update(st, cfg, time, time_close)
    st := st0

    qt.QuarterRecord qcur = f_qt_pick_qr(d.curQuarterIndex, d.q1, d.q2, d.q3, d.q4)
    qt.QuarterRecord qprev = d.curQuarterIndex == 1 ? st.daily.prev1 : d.curQuarterIndex == 2 ? d.q1 : d.curQuarterIndex == 3 ? d.q2 : d.q3
    qt.QuarterRecord qprev2 = d.curQuarterIndex == 1 ? st.daily.prev2 : d.curQuarterIndex == 2 ? st.daily.prev1 : d.curQuarterIndex == 3 ? d.q1 : d.q2
    bool qprev_up = qprev.has and not na(qprev.c) and not na(qprev.o) and qprev.c > qprev.o
    bool qprev_down = qprev.has and not na(qprev.c) and not na(qprev.o) and qprev.c < qprev.o
    [a_o, a_h, a_l, a_c, a_t, a_actual_o, a_actual_o_ts, a_actual_boundary_ts, a_actual_qi] = qt.qt_daily_aligned_ohlc_debug()

    // Last 3 outputs are the tCISD bar triplet: close/open/time from QTEngine aligned pack.
    [qprev2.h, qprev2.l, qprev2.c, qprev2.o, qprev2.boundaryTs, qprev.h, qprev.l, qprev.c, qprev.o, qprev.boundaryTs, qcur.h, qcur.l, qcur.c, qcur.o, qcur.boundaryTs, qprev_up, qprev_down, qprev.lTs, qprev.hTs, a_c, a_o, a_t]
```

Request both main and pair via this same helper:

```pine
[... , mcb0, mob0, mtb0] = request.security(syminfo.tickerid, "15", f_qt_daily_c123(), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=true)
[... , pcb0, pob0, ptb0] = request.security(_pair_sym,        "15", f_qt_daily_c123(), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=true)
```


## tCISD Terms
- `purge asset`: asset that performs the sweep in the setup direction.
- `failure asset`: opposite asset used for confirmation.
- `C2 high/low`: prior quarter extreme used as sweep reference.
- `tCISD anchor`: candle open level chosen near purge timestamp on target asset.
- `confirm`: failure asset close breaks anchor level with strict inequality.


## Bearish tCISD (Canonical Flow)
1. Detect setup context (TPD + directional assignment of purge/failure asset).
2. Capture first sweep timestamps:
   - main sweep ts and pair sweep ts.
3. Stage 2 trigger:
   - purge sweep seen after at least one C2 high sweep.
4. Compute candidate timestamp for failure-side tCISD anchor:
   - use purge event timestamp mapped to failure side.
5. Resolve candle index:
   - match `back0` on exact timestamp;
   - fallback `back1` to handle alignment edge.
6. Anchor candle color rule:
   - bearish tCISD uses bullish anchor candle (`close > open`).
7. Anchor level:
   - `anchor_level = anchor_open`.
8. Confirm:
   - failure asset close must be strictly below anchor level (`<`).
9. Optional purge-side anchor line:
   - same method, but on purge side.


## Bullish tCISD (Mirror Rules)
Mirror all bearish conditions:
- Use low sweeps instead of high sweeps.
- Anchor candle must be bearish (`close < open`).
- Confirm on strict break above anchor level (`>`).
- Keep same timestamp mapping pattern and `back0/back1` fallback.


## Timestamp Mapping Rules
When mapping from purge event to anchor on another asset:
- Use aligned timestamp equality first.
- If exact match fails, fallback one bar back.
- If still unresolved:
  - default mode: leave anchor as `na`.
  - strict mode: `runtime.error("tCISD anchor mapping failed")`.

Recommended strictness:
- Keep default mode in production indicators.
- Use strict mode while validating a new model.


## Lifecycle Rules
Reset state on:
- new HTF boundary (expiry),
- invalidation before confirm,
- setup cancellation events.

Do not keep stale objects/levels after reset:
- clear anchors,
- clear confirm timestamps,
- clear drawn line/label ids,
- clear purge timestamps.

Process invalidation before stage-confirm checks.


## Confirm Window Policy
Pick policy per model and keep it explicit:
- `C3-only confirm` (used in `2CiC State`): confirm must happen before `c4_open_ts`.
- `any-later confirm` (allowed by requirement doc): confirm can occur after C3.

If you use `C3-only`, compute:
- `c4_open_ts = c3_open_ts + htf_span_ms`
- confirm valid only when `bar_ts < c4_open_ts`.


## Drawing Contract (if visuals are needed)
Standard line behavior:
- `m15 tCISD` line:
  - starts at `anchor_ts`,
  - y = `anchor_level`,
  - ends at `c4_open_ts` (or policy end time).
- `m15 tCISD (Purge)` line:
  - same style, purge-side anchor.
- Purge level line:
  - draw C2 sweep level on purge asset.

Use one color family for consistency:
- base tCISD level color for anchor lines,
- semi-transparent directional color for purge-level line.


## Minimal Reusable Functions To Copy
These small helpers keep future implementations consistent:

```pine
f_pick_bear_anchor(int back0, int back1, float c0, float o0, float c1, float o1, int t0, int t1) =>
    float lvl = na
    int ts = int(na)
    if back0 <= bar_index and c0 > o0
        lvl := o0
        ts := t0
    else if back1 <= bar_index and c1 > o1
        lvl := o1
        ts := t1
    [lvl, ts]

f_pick_bull_anchor(int back0, int back1, float c0, float o0, float c1, float o1, int t0, int t1) =>
    float lvl = na
    int ts = int(na)
    if back0 <= bar_index and c0 < o0
        lvl := o0
        ts := t0
    else if back1 <= bar_index and c1 < o1
        lvl := o1
        ts := t1
    [lvl, ts]
```


## Implementation Checklist
- Import QTEngine v34.
- Add `f_qt_daily_c123()` helper with `qt.qt_daily_aligned_ohlc_debug()`.
- Use one `request.security(..., "15", f_qt_daily_c123(), ...)` for main.
- Use one `request.security(..., "15", f_qt_daily_c123(), ...)` for pair.
- Consume `mcb0/mob0/mtb0` and `pcb0/pob0/ptb0` only from QTEngine helper output.
- Assign purge/failure asset per setup direction.
- Capture purge timestamps once.
- Resolve anchor with `back0/back1`.
- Enforce candle-color requirement on anchor.
- Use strict confirm inequality (`>` or `<`).
- Apply chosen confirm window policy.
- Reset all state cleanly on invalidation/expiry.
- Keep debug outputs for anchor ts/level/confirm ts.


## Common Mistakes
- Mixing raw chart `close/open/time` with QTEngine aligned values.
- Using `>=` or `<=` for confirm (must be strict).
- Confirming before anchor exists.
- Not clearing state when setup invalidates.
- Forgetting the `back1` fallback when timestamp alignment is off by one bar.
- Drawing lines without checking `na(...)` on all endpoints.


## Recommended Debug Fields
Expose these while integrating:
- `anchor_ts`
- `anchor_level`
- `purge_anchor_ts`
- `purge_anchor_level`
- `confirm_ts`
- `purge_seen`
- `invalidation_hit`
- `expired_hit`
- `failure_is_main`
- `purge_is_main`

This makes cross-indicator parity checks fast.
