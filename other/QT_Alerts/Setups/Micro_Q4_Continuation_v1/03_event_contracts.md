# Event Contracts

All events are reported as:
- `bool fired` (edge-triggered)
- `int  ts`    (event timestamp, Unix ms)
- optional metadata (direction, bounds, variant id)

## E0: Micro Quarter Change (QTEngine)
- Source: QTEngine
- Output:
  - micro_q (1..4)
  - micro_q_ts (start ts of current quarter)
  - micro_end_ts

## E1: Micro.SSMT Q1→Q2 (30s)
- Source: indicator detection on 30s
- Inputs:
  - prior-quarter reference levels (from QTEngine Micro quarter highs/lows or stored)
  - ES + NQ closes
- Output:
  - fired, ts, dir (bull/bear)

## E2: m15 First Post-SSMT FVG (15m)
- Source: indicator detection on 15m
- Trigger:
  - first FVG with `fvg_ts > ssmt_q1q2_ts`
- Output:
  - fired, ts, fvg_top, fvg_bot, fvg_dir
- Persistence:
  - store once; do not overwrite until reset

## E3: Micro.SSMT Q3→Q4 (30s)
- Same structure as E1, scoped to Q3→Q4 window
- Output:
  - fired, ts, dir

## E4: m15 SMT-F (15m) (ALL variants enabled)
- Source: paired ES/NQ logic on 15m
- Preconditions:
  - requires same-time FVG presence on at least 2 correlated assets (ES/NQ)
  - preferably the first post-SSMT FVG, but v1 allows any qualifying SMT-F after E2

## E5: Close over Micro.tCISD (chart TF or 30s)
- Source:
  - safest: evaluate on 30s and bubble up (keeps entry logic consistent)
- Trigger:
  - first bar close that crosses and closes beyond micro.tCISD in the required direction
- Output:
  - fired, ts
