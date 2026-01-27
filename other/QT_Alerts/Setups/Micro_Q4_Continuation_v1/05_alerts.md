# Alerts

Two alert outputs.

## Alert A: Setup Armed
Fire exactly once when entering ST_ARMED.

Minimum requirements (v1):
- micro_q == 4
- h4_c ∈ {3,4}
- E2 recorded (first post-SSMT m15 FVG exists)
- E3 fired (Micro SSMT Q3→Q4 confirmed)
- E4 fired (m15 SMT-F fired; ANY variant accepted)

Payload (recommended fields):
- setup_id: "Micro_Q4_Continuation_v1"
- h4_c
- micro_q
- smtf_variant_id
- fvg_ts (stored)
- ssmt_q3q4_ts

## Alert B: Entry Now
Fire exactly once when entering ST_ENTRY.

Minimum requirements:
- currently ST_ARMED
- E5 fired: first close over Micro.tCISD (direction consistent with setup)

Payload:
- setup_id
- entry_ts
- micro_tCISD
- close_price
