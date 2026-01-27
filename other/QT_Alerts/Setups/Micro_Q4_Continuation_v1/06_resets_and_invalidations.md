# Resets & Invalidations

## Global reset
- Reset the entire FSM when a new Daily cycle begins (or daily scope boundary you choose).
- Also reset on Micro cycle rollover (micro_end_ts passed).

## Disarm / Invalidate (v1 suggested)
- If micro_q != 4 after arming → reset to ST_WAIT_MICRO_Q1
- If H4 filter fails (h4_c not in {3,4}) after arming → disarm (configurable)
- Optional: if price closes back through Micro.tCISD opposite direction before entry → disarm

## Anti-spam
- Track `last_armed_ts` and `last_entry_ts` and do not re-fire until reset.
