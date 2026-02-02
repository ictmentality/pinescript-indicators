1) Concise plan for Codex (no code edits yet)

Task A — Add "actual-open" series to aligned ingest (Micro + Nano)
   Anchors
   - f_micro_aligned_ohlc_expr()
   - f_nano_aligned_ohlc_expr()

   Action
   - In each aligned expr, compute and return two concepts:
     1) Bar OHLC/time (what you already return)
     2) Quarter "actual-open" series, held constant until next quarter:
        - actualOpen        = open of the first aligned bar on/after the quarter boundary
        - actualOpenTs      = that bar's timestamp
        - actualBoundaryTs  = the boundary timestamp for the active quarter
        - actualQi          = quarter index (1–4)

   Constraints
   - No new request.security() calls
   - lookahead_off only
   - Do not use an identifier reserved by QT language; use actualOpen*

   Done when
   - Aligned expr returns:
     (o, h, l, c, t, actualOpen, actualOpenTs, actualBoundaryTs, actualQi)
   - Values are stable within the quarter.

   Test
   - Same symbol/date-range on:
     - 30s + 1m + 5m charts (Micro)
     - 5s + 15s / 1m charts (Nano)
   - Quarter open price + timestamp must match the aligned-derived capture on all
     chart TFs.


Task B — Upgrade aligned picker to pass the new fields downstream
   Anchor
   - f_aligned_ohlc_pick(...)

   Action
   - Return the extended tuple for Micro/Nano.
   - Return na placeholders for m90.

   Constraints
   - Preserve Pine v6 type consistency:
     every branch returns the same tuple shape.

   Done when
   - All call sites destructure the extended tuple.
   - Compilation succeeds.

   Test
   - Compile
   - Quick visual smoke test: aligned values still match prior behavior.


Task C — Remove separate Micro/Nano open-capture requests in the engine path
   Anchors
   - f_fixed_cycle_update(...)
   - Calls to:
     - f_micro_open_current_30s()
     - f_nano_open_current_5s()

   Action
   - Delete/retire engine-path usage of the dedicated open-capture functions.
   - Populate pendingBoundaryTs / pendingOpen / pendingOpenTs from aligned-pack
     fields:
     (actualBoundaryTs, actualOpen, actualOpenTs)

   Constraints
   - Keep quarter realization rule: time_close > ts (early mode)
   - On activation: set QuarterRecord.o and QuarterRecord.oTs once
   - After activation: update h/l/c only; never touch o/oTs again

   Done when
   - Engine path has no dependency on dedicated open-capture requests.
   - Micro/Nano opens are stable across chart TFs.

   Test
   - Reproduce original mismatch case (1m vs 30s) and confirm it is gone.
