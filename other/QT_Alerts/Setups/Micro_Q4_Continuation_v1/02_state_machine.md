# State Machine (FSM)

## State list
- ST_IDLE
- ST_WAIT_MICRO_Q1
- ST_Q1_ACCUM_A_OK         (TBD definition; can be stubbed true initially)
- ST_SSMT_Q1Q2_CONFIRMED
- ST_CAPTURE_M15_FIRST_FVG
- ST_Q3_TIGHT_DIST_OK      (TBD definition; optional gate initially)
- ST_SSMT_Q3Q4_CONFIRMED
- ST_ARMED                 (fires "Setup Armed")
- ST_ENTRY                 (fires "Entry Now")
- ST_DONE                  (optional; prevents repeats until reset)

## Required progression (minimal v1)
ST_IDLE
  → ST_WAIT_MICRO_Q1
  → ST_SSMT_Q1Q2_CONFIRMED
  → ST_CAPTURE_M15_FIRST_FVG
  → ST_SSMT_Q3Q4_CONFIRMED
  → ST_ARMED
  → ST_ENTRY
  → ST_DONE

## Guards (must be true to advance)
- Daily scope is active (not out-of-session if you enforce session rules)
- H4 filter: h4_c ∈ {3,4} must be true at arming and remain true until entry (configurable)

## Notes
- “Q1 Accumulation A” and “Q3 tight distribution” are placeholders:
  - v1 can run without them (treat as always true) to validate plumbing first.
