# QTAssets

`QTAssets` is a Pine Script v6 library that resolves peer symbols for QT Triad/Dyad asset selection.

## Exported API

`resolve_pair_symbols(selection_mode, badj, sym, symTicker, chartTicker, chartRoot) -> [string tsym2, string tsym3]`

- `selection_mode`: `"Triad"`, `"Dyad"`, or `"Off"`
- `badj`: futures backadjust fallback used when chart metadata does not explicitly indicate backadjust on/off
- `sym`, `symTicker`, `chartTicker`, `chartRoot`: chart identity inputs (same values used in QT Display)
- Returns:
  - `tsym2`: primary peer
  - `tsym3`: secondary peer (`""` in Dyad mode)

## What It Handles

- Triad detection and peer resolution
- Dyad resolution (explicit and auto-mapped groups)
- Dated/continuous contract handling
- Micro/standard contract size alignment
- Futures session/backadjust modifiers via `ticker.modify`
- Chart backadjust auto-detection via `syminfo.tickerid` metadata (with `badj` fallback)
- Self/duplicate peer cleanup

## Built-In Groups

- Triads: `DXY/6E/6B`, `CL/RB/HO`, `ZB/TN/ZF`, `GC/SI/HG`, `NQ/ES/YM`
- Dyads: `ZB/TN` plus auto pairs (indices, oil, forex `DXY <-> 6E`, metals, spot FX/crypto/CFD pairs)

## Minimal Usage

```pine
//@version=6
indicator("QT Assets Example", overlay=true)
import <publisher>/QTAssets/<version> as qa

selection_mode = input.string("Off", "Pair Selection", options=["Triad", "Dyad", "Off"])
badj = input.bool(false, "Backadjust")

sym = syminfo.tickerid
symTicker = str.upper(syminfo.ticker)   // pass your existing normalized value if you have one
chartTicker = str.upper(syminfo.ticker)
chartRoot = str.upper(syminfo.root)

[tsym2, tsym3] = qa.resolve_pair_symbols(selection_mode, badj, sym, symTicker, chartTicker, chartRoot)
```
