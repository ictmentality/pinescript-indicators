# tCISD Requirements (v1)

## Scope
- Implement tCISD for SSMT only.
- Skip HSSMT in v1.
- Use QTEngine quarter data.

## QTEngine Integration
- Import: `import Jaw1312/QTEngine/33 as qt` (confirmed).
- Cycle scope for v1: **Daily**.
- SSMT detection timeframe alignment:
1. Daily cycle SSMT on aligned `15m`.
2. m90 cycle SSMT on aligned `5m`.
- QTEngine fields available and usable for context/debug:
1. `eng.daily.curQuarterIndex`
2. `eng.daily.q1`, `eng.daily.q2`, `eng.daily.q3`, `eng.daily.q4` (`o/h/l/c` + timestamps)
3. `eng.daily.evt` (boundary event)
4. `eng.daily.cycleStartTs`, `eng.daily.cycleEndTs`

## Definition
tCISD confirms only after an SSMT exists.
- Bullish tCISD: first bar close `> close(tcisdAnchor)`.
- Bearish tCISD: first bar close `< open(tcisdAnchor)` (open price of the down-closed anchor candle).
- Confirmation is strict (`>` / `<` only, never equality).
- Confirmation can happen at any later time (not quarter-limited).

## Anchor Selection (tcisdAnchor)
Let `ssmtCandle` be the SSMT-creating candle on the relevant asset.

- Bearish SSMT scenario:
1. Required anchor color: bullish.
2. If `ssmtCandle` is bullish, use it.
3. Else use the most recent bullish candle before it.

- Bullish SSMT scenario:
1. Required anchor color: bearish.
2. If `ssmtCandle` is bearish, use it.
3. Else use the most recent bearish candle before it.

- Lookback for fallback anchor search: unlimited.
- Inclusion rule: `ssmtCandle` is allowed when it matches required color.

## Failure Swing Mapping
- On the failure swing asset, use the same anchor timestamp selected from the stop-hunt asset.
- Anchor timestamp is expected to always exist on mapped series.
- If it does not exist, throw a runtime error.

## Lifecycle / Invalidation
- Once confirmed, tCISD remains valid until its parent SSMT is invalidated.
- SSMT invalidation condition: both assets run PQL or PQH.
- Keep/label all tCISDs that exist.

## Required Outputs
- `tcisdAnchorTs`
- `tcisdO`
- `tcisdC`
- `confirmTs`

Optional debug:
- `anchorReason` (`ssmtCandle`, `priorOppCandle`, `failureSwingMapped`)
