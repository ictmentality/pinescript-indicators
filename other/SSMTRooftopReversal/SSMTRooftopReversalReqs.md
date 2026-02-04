SSMT Rooftop Reversal — Requirements (v0.3b)

Checklist (step-by-step)
- [ ] Stage 1: Inputs + symbol normalization + QTEngine m90 packs (dyad)
- [ ] Stage 2: Sweep flags (m90) + previous-quarter selection
- [ ] Stage 3: SSMT divergence + sweeper identification (Q0/Q1)
- [ ] Stage 4: Rooftop detection + roofTs + roofInvalid
- [ ] Stage 5: State machine S0–S4 + expiry windows (m5 bars)
- [ ] Stage 6: tCISD level + trigger (m5)
- [ ] Stage 7: MSS trigger (m5)
- [ ] Stage 8: SMT-F / PSP signals + stop rules
- [ ] Stage 9: Alerts + debounce
- [ ] Stage 10: Debug outputs (tables/data window) + replay validation

1) Purpose
   Detect and alert on a Rooftop Reversal setup defined by:
   - Rooftop pattern (m90)
     - Sweep SSMT followed immediately by Failure SSMT (consecutive)
     - Alternating sweeper asset
   - tCISD confirmation (m5)
     - Confirm via m5 close through the tCISD level in the direction implied by rooftop bias
   - MSS (m5)
   - SMT-F and/or PSP
   - Produce a stop reference per rules

   Notes
   - This is an alert indicator (not a strategy).


2) System Boundary

   2.1 QTEngine responsibilities (library)
       QTEngine is responsible for:
       - Maintaining cycle state and quarter records for fixed cycles via (I'm not certain that I will need any other cycles than the m90):
         - qt_daily_update
         - qt_m90_update
         - qt_micro_update
         - qt_nano_update
         - f_qt_step

       - Exposing data structures needed to derive higher-level models:
         - quarter OHLC
         - timestamps
         - quarter index
         - boundary events
         - etc.
         via exported UDTs:
         - QTConfig
         - QuarterRecord
         - QtSeriesPack
         - CycleResult
         - FixedCycleState
         - CycleState
         - QtBoundaryEvent
         - QtCycleState
         - QtEngineState

       QTEngine does NOT export:
       - SSMT / HSSMT events
       - tCISD events
       - MSS / SMT-F / PSP logic

   2.2 Indicator responsibilities (all model logic)
       The SSMT Rooftop Reversal indicator must compute and verify:
       - SSMT and its subtypes (Sweep SSMT vs Failure SSMT)
       - Rooftop pattern + bias
       - tCISD level + trigger
       - MSS
       - SMT-F / PSP
       - State machine, debouncing, alerts, and minimal plotting in TradingView


3) Data Sourcing Requirements (indicator-owned)

   3.1 Using QTEngine for quarter data (required)
       The indicator must:
       1) Initialize QTEngine state:
         - qt_config_default (use default tz/day start)
         - qt_state_new
       2) Step/update required cycles:
         - m90 via qt_m90_update (CycleState path; no f_qt_step)
         - m5 data via request.security(...,"5", ...) for tCISD/MSS/PSP/SMT-F
       3) Read quarter data (current + previous quarter) from QTEngine-returned objects:
          - CycleResult / CycleState / FixedCycleState / QuarterRecord

   3.2 Multi-symbol requirement (Dyad)
       - Rooftop requires a dyad comparison (exactly two correlated symbols).
       - The indicator must source quarter records for each symbol using request.security()
         calls that evaluate the indicator’s QTEngine-backed logic on each symbol.
       - Performance rule:
         one request per (symbol, timeframe) and reuse series everywhere
         (UDT packing preferred).


4) Canonical Definitions (indicator-verified, Dyad)
   Let the dyad symbols be symA and symB.

   4.1 Sweep test (m90, per symbol)
       Sweep is computed relative to the previous m90 quarter’s extremes
       (sourced from QTEngine quarter records):

       - sweepUp(sym) is true if current m90 quarter exceeds prior m90 quarter high
         (wick-based default)
       - sweepDn(sym) is true if current m90 quarter exceeds prior m90 quarter low
         (wick-based default)

       Notes
       - Body-based toggle allowed later.
       - Wick-based default for rooftop classification.
       - Live evaluation during the current m90 quarter (can repaint).
       - Previous quarter selection (matches QTEngineTest):
         - if curQuarterIndex == 1 => use st.m90.prev1
         - else use prior quarter in the same cycle (Q1/Q2/Q3)

   4.2 SSMT event (m90) — dyad divergence rule
       An m90 quarter is an SSMT quarter if the dyad diverges on the relevant side:

       - Bearish-side SSMT (above highs):
         sweepUp(symA) != sweepUp(symB)

       - Bullish-side SSMT (below lows):
         sweepDn(symA) != sweepDn(symB)

   4.3 Sweep SSMT quarter (m90) — unique sweeper (dyad)
       A Sweep SSMT quarter is an SSMT quarter where exactly one symbol sweeps
       (implied by dyad divergence):

       - Bearish Sweep SSMT:
         sweepUp(symA) != sweepUp(symB)

       - Bullish Sweep SSMT:
         sweepDn(symA) != sweepDn(symB)

       Define
       - sweeperSym =
         - symA if sweepUp(symA)==true (bearish case) or sweepDn(symA)==true (bullish case)
         - else symB
       - sweepSide ∈ { aboveHighs, belowLows }

   4.4 Failure SSMT quarter (m90) — alternating sweeper
       A Failure SSMT quarter occurs immediately after a Sweep SSMT quarter and satisfies:
       - The dyad is again an SSMT quarter on the same sweepSide, AND
       - The sweeper alternates:
         - sweeperSym_current != sweeperSym_previous


5) Rooftop Definition (locked, Dyad)
   A Rooftop is formed when:
   1) Quarter Q0 (m90) is a Sweep SSMT quarter
      - dyad divergence; one sweeper
   2) Quarter Q1 (next consecutive m90 quarter) is a Failure SSMT quarter:
      - dyad divergence again on the same sweepSide
      - sweeper alternates vs Q0

   Rooftop bias
   - aboveHighs sweep side -> bearish rooftop bias
   - belowLows  sweep side -> bullish rooftop bias

   Rooftop completion point
   - roofTs = sweep timestamp in Q1 (failure quarter) for the sweeper:
     - aboveHighs -> use hTs
     - belowLows  -> use lTs

   Persist rooftop metadata
   - roofBias
   - roofSweeper0, roofSweeper1
   - roofQ0_hi/lo, roofQ1_hi/lo for each symbol (from QTEngine quarter records)
   - roofInvalid (computed in 9.1)


6) tCISD (m5) — indicator-verified

   6.1 tCISD level computation (required)
       The indicator must compute:
       - tcisdLevel (float)
       - tcisdDir   (bull/bear)
       - tcisdTs    (timestamp)

       Notes
       - Construction is implementation-defined for now, but must be:
         - derived from m5 price action
         - gated by rooftop bias (directional consistency)
       - m5 data is sourced via request.security(...,"5", ...), not QTEngine

   6.2 Trigger rule (locked)
       tCISD is confirmed only when the m5 close crosses the level:
       - If bearish rooftop bias:
         confirm when m5 close < tcisdLevel
       - If bullish rooftop bias:
         confirm when m5 close > tcisdLevel

       Confirmed means
       - evaluated on m5 close (not intrabar)


7) MSS / SMT-F / PSP (indicator-owned)

   7.1 MSS (m5)
       Confirm MSS when an m5 close breaks a defined protected swing in the
       direction of bias.

   7.2 SMT-F / PSP
       SMT-F and PSP are computed in the indicator (m5 default) and return:
       - booleans + any levels needed for stop logic

       Return values (examples)
       - smtf_ok, plus fvg_hi/lo if available
       - psp_ok, plus any helpful swing refs (optional)


8) State Machine *Note: S2 and S3 can occur in either order but typically S2 is first
   - S0 Idle
     -> S1 Rooftop Armed
     -> S2 tCISD Confirmed
     -> S3 MSS Confirmed
     -> S4 Setup Ready

   Expiry windows
   - rooftopMaxAge_m90Bars
   - tCISDLookahead_m5Bars
   - MSSLookahead_m5Bars
   - ConfluenceLookahead_m5Bars
   - All lookahead/expiry windows are measured in m5 bars (name retained)

   Debounce
   - once-per-setup default


9) Required Levels

   9.1 Rooftop invalidation level (required)
       On rooftop completion, define invalidation using combined dyad extremes
       across Q0 and Q1:

       - Bearish rooftop:
         roofInvalid = max(
           high(Q0,symA), high(Q0,symB),
           high(Q1,symA), high(Q1,symB)
         )

       - Bullish rooftop:
         roofInvalid = min(
           low(Q0,symA), low(Q0,symB),
           low(Q1,symA), low(Q1,symB)
         )

       Used for
       - invalidation in S1+
       - default stop reference if PSP + SMT-F not present

   9.2 Stop reference rules
       1) If PSP AND SMT-F:
          - stop = beyond FVG extreme (bias-dependent)

       2) Otherwise:
          - stop = beyond roofInvalid (bias-dependent)

       3) Rejection Block exception (optional)


10) Alerts
    - Rooftop Armed (optional):
      include sweepers Q0/Q1 + roofTs
    - tCISD Confirmed:
      include tcisdLevel + confirming close
    - MSS Confirmed
    - Setup Ready (primary):
      include bias, sweepers, timestamps, confluence flags, stop rule + stop price

    Debounce requirement
    - All alerts must be debounced once-per-setup by default.


11) Inputs (recommended)
    - Dyad symbols: symA, symB
    - enableBearish = true
    - enableBullish = false
    - requireSMTF   = true
    - requirePSP    = false
    - requireBoth   = false
    - rooftopMaxAge_m90Bars      = 6
    - tCISDLookahead_m5Bars      = 24
    - MSSLookahead_m5Bars        = 24
    - ConfluenceLookahead_m5Bars = 24
    - resetAfterAlert = true


12) Debug / Testing (Dyad)
    Debug must show:
    - Last 2 m90 quarters per symbol:
      - prior quarter H/L
      - current quarter H/L
      - sweep flags (sweepUp, sweepDn)
      - sweeper symbol for Q0 and Q1

    - Rooftop formed?
      - sweepers Q0/Q1
      - roofInvalid

    - m5 tCISD:
      - tcisdLevel
      - trigger evaluation
      - timestamp

    - MSS / SMT-F / PSP booleans
    - current state S0–S4

    Replay cases
    1) Sweep -> Failure rooftop, then tcisd trigger, MSS, confluence
    2) Sweep SSMT but next quarter sweeper does not alternate (reject)
    3) Rooftop forms but tcisd trigger never fires (expiry)

    Extra Notes
    1) The Rooftop SSMT Q1 does not need to close for the state machine to begin looking for tCISDs
