# QTEngine

Fixed-cycle quarter engine for Pine v6. Data-only: timestamps, OHLC, and state
flags for Daily / m90 / Micro / Nano cycles. No drawings, no styling, no
bar_index anchoring. Non-repaint (request.security lookahead_off only).

## Cycles
- Daily: 24h cycle, quarters 6h, aligned TF 15m
- m90: 6h cycle, quarters 90m, aligned TF 5m
- Micro: 90m cycle, quarters 22m30s, aligned TF 30s
- Nano: 22m30s cycle, quarters 5m37.5s, aligned TF 5s

Day-start anchor defaults to America/New_York 18:00. Aligned open capture uses
the fixed NY 18:00 anchor regardless of cfg.tz (library request.* constraint).

## Quick start
```pinescript
import Jaw1312/QTEngine/34 as qt

var qt.QTConfig cfg = qt.qt_config_default()
var qt.CycleState st = qt.qt_state_new()

[st, daily] = qt.qt_daily_update(st, cfg, time, time_close)

var qt.QtEngineState eng = qt.f_qt_init()
eng := qt.f_qt_step(eng, time, time_close)
```

## API
Constructors:
- qt_config_default() -> QTConfig
- qt_state_new() -> CycleState
- f_qt_init() / f_qt_init_with_cfg(cfg) -> QtEngineState

Per-cycle updates:
- qt_daily_update(st, cfg, t, tClose)
- qt_m90_update(st, cfg, t, tClose)
- qt_micro_update(st, cfg, t, tClose)
- qt_nano_update(st, cfg, t, tClose)
Return: [CycleState, CycleResult]

Engine step:
- f_qt_step(eng, t, tClose) -> QtEngineState

Debug (read-only):
- qt_micro_aligned_ohlc_debug(), qt_nano_aligned_ohlc_debug(), qt_m90_aligned_ohlc_debug(), qt_daily_aligned_ohlc_debug()
- qt_micro_aligned_qr_debug(st), qt_nano_aligned_qr_debug(st)

## Data shapes
QTConfig:
- tz, dayStartHour, dayStartMin, keepCycles
- tfDaily, tfM90, tfMicro, tfNano (reserved; aligned TFs are currently fixed)

QuarterRecord:
- boundaryTs (quarter start)
- o/h/l/c and oTs/hTs/lTs/cTs
- bh/bl and bhTs/blTs (body high/low)
- has, isEmpty, isFinal, evtStart, evtFinalize

CycleResult:
- startTs, endTs, q1Ts..q4Ts, q2Realized/q3Realized/q4Realized
- curQuarterIndex, inWindow, q1..q4 (QuarterRecord)

QtCycleState:
- CycleResult fields plus lastBoundaryTs, prev1/prev2, evt (boundary event)

## Notes
- Realization uses time_close > boundaryTs for state-trigger correctness.
- Aligned H/L/C/body values override chart-TF aggregation; opens are preserved
  from actual-open capture.
- Elastic cycles (weekly/monthly/etc) are not implemented.
