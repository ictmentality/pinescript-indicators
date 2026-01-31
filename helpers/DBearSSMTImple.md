QTENGINE TEST — DAILY BEARISH HIDDEN SSMT (HSSMT) IMPLEMENTATION (ES vs NQ)
==========================================================================

GOAL
----

You already have standard **Daily SSMT** (wick-based). **Hidden SSMT (HSSMT)** is the same
*consecutive-quarter divergence* idea, but the **reference** and **break tests** are
**body/close** rather than wick-based.

Key requirement going forward:

- **Do not** recompute quarter body extremes inside `QTEngineTest`.
- Instead, **QTEngine must track quarter body extremes** (and their timestamps) so every
  indicator can reuse them consistently.

---

0) PREREQUISITE — ADD BODY EXTREMES TO QTENGINE (REQUIRED)
----------------------------------------------------------

**Why:** HSSMT (and future body-based logic) needs quarter body extremes and their timestamps.
`QuarterRecord` currently stores wick `h/l` plus `o/c`, but not body extremes. Therefore
we will extend `QuarterRecord` so *all cycles* can expose body-based behavior without
reimplementing it in each indicator.

0.1) Extend `QuarterRecord` (mandatory fields)

- Add required fields:
  - `bh`   — quarter **body high** (max(open, close) over bars in quarter)
  - `bl`   — quarter **body low**  (min(open, close) over bars in quarter)
  - `bhTs` — timestamp of the bar that set `bh` (updates when `bh` updates)
  - `blTs` — timestamp of the bar that set `bl` (updates when `bl` updates)

0.2) Update all `QuarterRecord.new(...)` call sites

- `qt_state_new()` → `nilQ`: initialize `bh/bl/bhTs/blTs` to `na`.
- `f_make_empty_q(qStart)`: initialize `bh/bl/bhTs/blTs` to `na`.

0.3) Update quarter aggregation: `f_q_apply_bar(...)`

Per bar:
- `barBH = max(o, c)`
- `barBL = min(o, c)`

Rules:
- On first bar of quarter (`not q.has`):
  - initialize `bh/bl` to `barBH/barBL`
  - initialize `bhTs/blTs` to `t`
- Else:
  - if `barBH > bh` → update `bh` and `bhTs := t`
  - if `barBL < bl` → update `bl` and `blTs := t`

Timestamp convention:
- Use `t` (bar open time), matching the existing `hTs/lTs` convention.

0.4) Maintain alignment where QTEngine overwrites OHLC from aligned records

Anywhere QTEngine copies aligned OHLC fields from `aq*` → `q*`, also copy:
- `bh`, `bl`, `bhTs`, `blTs`

Otherwise you will end up with:
- aligned `c/cTs` (correct)
- but **non-aligned body extremes** (incorrect)

(At minimum this applies to the Micro/Nano aligned-override block; and m90 should also
copy body fields if you intend to use HSSMT there.)

---

1) DEFINITION (BEARISH HSSMT AT HIGHS)
-------------------------------------

- **Daily Bearish HSSMT** = during the **next quarter**, **one** of {ES, NQ} achieves a
  **body/close break above** the **prior-quarter body-high**, while the other does **not**.

Where:
- `barBodyHigh = max(open, close)`
- `priorQuarterBodyHigh = max(barBodyHigh)` over all bars in the **prior quarter**
  (this becomes `prevQ.bh` once QTEngine tracks body extremes).

---

2) DATA YOU NEED (FROM QTENGINE, PER SYMBOL)
--------------------------------------------

For **each** of ES and NQ, on the **daily-aligned TF** (likely `cfg.tfDaily`), you need:

- `prevQ.bh` and `prevQ.bhTs` — prior quarter body-high reference + timestamp
- `curQ.bh` and `curQ.bhTs`   — current quarter running body-high + timestamp (for debug)
- Current bar `close` (to support close-break, if used)
- A quarter-change signal to reset latches (use QTEngine quarter boundary events, e.g.
  `evtStart`, or a change in the active quarter `boundaryTs`).

Note:
- With `bh/bl/bhTs/blTs` in QTEngine, `QTEngineTest` no longer needs its own rolling
  `prevBodyHigh/curBodyHigh` state.

---

3) COMPUTE + RESET LOGIC (QTEngineTest)
---------------------------------------

For each symbol security stream (**ES** and **NQ** separately):

3.1) Run the Daily engine (existing pattern)

- Execute `qt_daily_update(state, cfg, time, time_close)` inside
  `request.security(symbol, cfg.tfDaily, ...)`.

3.2) Identify the active quarter record + previous quarter record

- Determine the active quarter (`curQ`) from `res.curQuarterIndex`:
  - `curQ` is one of `res.q1/res.q2/res.q3/res.q4`
- Use `res.prev1` as the immediately prior finalized quarter record (`prevQ`).

3.3) Define “break” (canonical + optional debug)

Canonical (recommended for “TF-aligned close” validation):
- **Close-break:** `close > prevQ.bh`

Optional debug comparison:
- **Body-break:** `curQ.bh > prevQ.bh`
  (equivalently: “some bar in the current quarter has bodyHigh above prior quarter bh”)

3.4) Pairwise divergence condition (bearish only)

Once you have `esBreak` and `nqBreak` on the same aligned bar timestamp:

- **Bearish HSSMT event (at highs):**
  - `(esBreak and not nqBreak) OR (nqBreak and not esBreak)`
  - (Equivalent: `XOR(esBreak, nqBreak)`)

3.5) “Fire once” behavior (clean test signal)

Store a per-quarter latch:
- `hssmtFiredThisQuarter`

Reset rule:
- Reset on quarter start (use the active quarter’s `evtStart`), **or**
- Reset when the active quarter `boundaryTs` changes.

Emit rule:
- Only emit the HSSMT signal the **first** time divergence becomes true inside that quarter.

---

4) OUTPUT + DEBUG (HIDDEN CORRECTNESS TEST)
-------------------------------------------

Output (default hidden):
- `alertcondition(D_HSSMT_Bear, "Daily Bearish HSSMT (ES vs NQ)", ...)`

Optional debug toggle (recommended):
- Print/log at trigger time:
  - `prevQ.bh` + `prevQ.bhTs`
  - `curQ.bh` + `curQ.bhTs`
  - `esBreak`, `nqBreak`
  - active `curQ.boundaryTs`
- Optionally label which symbol **broke** and which **failed**.

This is a correctness test:
- If you change chart timeframe, the signal timing should remain stable because the
  computation is sourced from `cfg.tfDaily` via `request.security(...)`.
