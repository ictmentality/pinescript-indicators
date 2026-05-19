# QTEngineElastic

Fixed + elastic quarter engine for Pine v6. This README refers to
`QTEngineElastic.txt`.

Data-only: timestamps, OHLC, body levels, and state flags for Daily / m90 /
Micro / Nano / Weekly / Monthly cycles. No drawings, no styling, no
`bar_index` anchoring. Non-repaint (`request.security(..., lookahead_off)` only).

## Cycles
- Daily: 24h cycle, quarters 6h, aligned TF 15m
- m90: 6h cycle, quarters 90m, aligned TF 5m
- Micro: 90m cycle, quarters 22m30s, aligned TF 30s
- Nano: 22m30s cycle, quarters 5m37.5s, aligned TF 5s
- Weekly: elastic week cycle, aligned TF 1h
- Monthly: elastic month cycle, aligned TF 4h

Day-start anchor defaults to `America/New_York` `18:00`. Aligned open capture
uses the fixed NY `18:00` anchor regardless of `cfg.tz` due to Pine
`request.*` constraints.

## Quick Start
```pinescript
import Jaw1312/QTEngineElastic/11 as qt

var qt.QTConfig cfg = qt.qt_config_default()
var qt.CycleState st = qt.qt_state_new()

[st, daily] = qt.qt_daily_update(st, cfg, time, time_close)
[st, weekly] = qt.qt_weekly_update(st, cfg, time, time_close)

var qt.QtEngineState eng = qt.f_qt_init()
eng := qt.f_qt_step(eng, time, time_close)
```

## API
Constructors:
- `qt_config_default() -> QTConfig`
- `qt_state_new() -> CycleState`
- `f_qt_init() / f_qt_init_with_cfg(cfg) -> QtEngineState`

Per-cycle updates:
- `qt_daily_update(st, cfg, t, tClose)`
- `qt_m90_update(st, cfg, t, tClose)`
- `qt_micro_update(st, cfg, t, tClose)`
- `qt_nano_update(st, cfg, t, tClose)`
- `qt_weekly_update(st, cfg, t, tClose)`
- `qt_monthly_update(st, cfg, t, tClose)`
Return: `[CycleState, CycleResult]`

Engine step:
- `f_qt_step(eng, t, tClose) -> QtEngineState`

Debug (read-only):
- `qt_micro_aligned_ohlc_debug()`
- `qt_nano_aligned_ohlc_debug()`
- `qt_m90_aligned_ohlc_debug()`
- `qt_daily_aligned_ohlc_debug()`
- `qt_micro_aligned_qr_debug(st)`
- `qt_nano_aligned_qr_debug(st)`
- `qt_daily_qr_debug(st)`
- `qt_m90_qr_debug(st)`
- `qt_micro_qr_debug(st)`
- `qt_nano_qr_debug(st)`
- `qt_weekly_qr_debug(st)`
- `qt_monthly_qr_debug(st)`

## Data Shapes
`QTConfig`:
- `tz`, `dayStartHour`, `dayStartMin`, `keepCycles`
- `tfDaily`, `tfM90`, `tfMicro`, `tfNano` (reserved; aligned TFs are fixed in the library)

`QuarterRecord`:
- `boundaryTs` (quarter start)
- `o/h/l/c` and `oTs/hTs/lTs/cTs`
- `bh/bl` and `bhTs/blTs`
- `has`, `isEmpty`, `isFinal`, `evtStart`, `evtFinalize`

`CycleResult`:
- `startTs`, `endTs`
- `q1Ts..q5Ts`
- `q2Realized..q5Realized`
- `curQuarterIndex`, `inWindow`
- `q1..q5` (`QuarterRecord`)

`QtCycleState`:
- `CycleResult` fields plus `lastBoundaryTs`, `prev1`, `prev2`, `evt`

## Notes
- Realization uses `time_close > boundaryTs` for state-trigger correctness.
- Aligned `H/L/C/body` values override chart-TF aggregation when the aligned path is used; opens are preserved from actual-open capture.
- `bh/bl` are close-based body extremes.
- Weekly and Monthly elastic cycles are implemented.
