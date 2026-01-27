# m15 FVG + SMT-F (ALL variations)

## A) FVG definition (ICT classic)
Bullish FVG:
- candle[2].high < candle[0].low
- bounds:
  - top = candle[0].low
  - bot = candle[2].high

Bearish FVG:
- candle[2].low > candle[0].high
- bounds:
  - top = candle[2].low
  - bot = candle[0].high

## B) "First post-SSMT" FVG
- After E1 (SSMT Q1→Q2), record the FIRST qualifying m15 FVG.
- Stored fields:
  - fvg_ts, fvg_top, fvg_bot, fvg_dir

## C) SMT-F prerequisite (Bucko-style)
SMT-F requires:
1) A same-time FVG event on ES and NQ (same m15 bar timestamp).
2) A divergence in retracement/fill behavior AFTER the FVG prints.

Track per asset:
- traded_into_gap (bool)
- fill_depth (0..1) where 0 = no entry, 0.5 = midpoint, 1 = full fill
- close_through_gap (bool) (optional caution signal)

## D) SMT-F variants (enable ALL; each can independently validate MTF)

Variant V1 — "No-trade-into vs trades-into"
- One asset trades into its gap (fill_depth > 0)
- The peer does not trade into its gap at all (fill_depth == 0)

Variant V2 — "Midpoint divergence"
- Both trade into their gaps
- One trades below the 50% midpoint (fill_depth > 0.5)
- The peer fails to trade below 50% (fill_depth <= 0.5)

Variant V3 — "Full fill divergence"
- One asset fills its gap completely (fill_depth == 1)
- The peer fails to fill completely (fill_depth < 1)

(Optionally keep “close-through caution” as metadata rather than disqualifier in v1.)

## E) SMT-F event output
- smtf_fired (edge)
- smtf_ts
- smtf_variant_id ∈ {V1,V2,V3}
- smtf_winner_symbol (the one that filled deeper)
- smtf_loser_symbol  (the one that held better)

## F) For this setup
- Accept ANY SMT-F variant as MTF validation once:
  - E2 exists (we have a stored post-SSMT FVG context)
  - and SMT-F occurs AFTER E2.ts (configurable strictness)
