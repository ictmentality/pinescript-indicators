# Oil Daily Q3 SSMT v0

## Locked Scope
- Indicator first, strategy second.
- Wednesday only.
- Daily cycle only.
- HTF narrative required first.
- Asset set: `NYMEX:CL1!`, `NYMEX:RB1!`, `NYMEX:HO1!`
- Primary pair: `CL/RB`
- Setup window: Daily `Q3` only
- PDArray filter: `BPR` only

## Repo Defaults
- Timezone: `America/New_York`
- HTF narrative TF: `H4`
- Daily cycle anchor: `18:00`
- Setup scan window: `06:00-12:00` New York (`Daily Q3`)
- Quarters:
  - `Q1` `18:00-00:00`
  - `Q2` `00:00-06:00` (`True Open`)
  - `Q3` `06:00-12:00`
  - `Q4` `12:00-18:00`
- Use full overnight session.
- Use the same timeframe for all three assets.
- Use `15m` as the execution/aligned timeframe for Daily-cycle logic.

## HTF Narrative Gate
- Do not scan for Daily-cycle SSMT unless one HTF condition is present first.
- Valid HTF narrative:
  - `H4` ICT FVG in play
  - `H4` `02:00 AM` TPD in play
- If neither is present, skip the Daily-cycle setup.
- `H4` defines narrative. Daily `SSMT` is the trigger.
- `H4` bullish FVG = 3-candle imbalance where `C3 low > C1 high`
- `H4` bearish FVG = 3-candle imbalance where `C3 high < C1 low`
- `H4` gap narrative is valid only if the Daily `SSMT` forms inside that `H4` gap on at least one asset.
- Use `C2` as the naming anchor for `H4` TPD.
- `02:00 AM H4 TPD`:
  - `C1 = 22:00 H4`
  - `C2 = 02:00 H4`
  - `C3 = 06:00 H4`
- TPD = crack in correlation between `C1 close` and `C3 open`.
- Bullish: one asset has `C3 open > C1 close` and a peer does not.
- Bearish: one asset has `C3 open < C1 close` and a peer does not.

## SSMT Rule For v0
- Use consecutive-quarter logic only.
- Compare the current quarter against the previous quarter's absolute high/low only.
- Bearish SSMT: one asset takes the previous quarter high and the peer fails.
- Bullish SSMT: one asset takes the previous quarter low and the peer fails.
- Current `QTDisplay` normal SSMT is wick/high-low based.
- Body-based logic exists separately as `HSSMT`; do not mix it into `v0`.
- Directional filter:
  - Bullish SSMT should form below the Daily `True Open`
  - Bearish SSMT should form above the Daily `True Open`

## Tentative Setup
- Stage 0: confirm `H4` narrative first.
- Look for setups only during Daily `Q3`.
- In `Q3`, one oil leg sweeps the `Q2` absolute high/low.
- `CL/RB` must show the split.
- `HO` is secondary confirmation only.
- If no `Q3` split, no setup.
- If the setup is not confirmed before `Q3` ends, invalidate it.

## Still Open
- Exact `BPR` formula
- Exact entry trigger bar
- Exact stop
- Exact target
- Whether `v0` keeps current wick-based SSMT or adds a new close-based variant
