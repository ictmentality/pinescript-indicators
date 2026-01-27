# Conventions

## Timeframes
- Highest scope (filter): Daily cycle
- HTF context: H4 (240m) cycle quarter (C1..C4)
- MTF validator: m15 (15m) SMT-F / FVG logic
- LTF execution: 30s Micro SSMT + entry confirmation

## Event discipline
- Every event is:
  - computed on its native TF
  - edge-triggered
  - timestamped
- Store event timestamps as `var int` (Unix ms from `time`), and only advance FSM forward.

## Boundary realization
- Treat boundaries as realized using `time_close > ts` (no confirmed-bar gating).
- Closes > wicks for confirmation logic; wicks can be treated as gaps if needed.

## Symbols
- Primary pair: ES + NQ (triad optional later).
