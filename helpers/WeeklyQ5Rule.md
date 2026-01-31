## W.Q5 End Rule (use Friday close)

### Friday close (intent)
- `friClose_intent` = **Friday 17:00:00 America/New_York** (CME ETH week close)

### Friday close (effective)
- `friClose_eff` = the **effective end timestamp** for W.Q5:
  - Default: `friClose_eff = friClose_intent`
  - If **early close / abnormal schedule** (no reliable calendar available):
    - set `friClose_eff = lastPrintedBarCloseTs` within the Friday session
    - set `isEarlyClose = true`

### W.Q5 window
- `W.Q5 = [thu18_eff, friClose_eff)`

### Week start next (separate, not W.Q5 end)
- `weekStart_next_intent` = next **Sunday 18:00**
- `weekStart_next_eff` = first printed bar-open time `>= weekStart_next_intent`

Notes:
- There are **no bars** between `friClose_eff` and `weekStart_next_eff` in normal conditions (weekend market closure).
- Do not extend W.Q5 across the weekend gap; keep weekend as **no-trade time outside W.Q5**.
