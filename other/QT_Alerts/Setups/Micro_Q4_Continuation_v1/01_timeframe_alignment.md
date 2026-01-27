# Timeframe Alignment

## Inputs (fixed for v1)
- HTF context TF: 240m (H4)
- MTF validation TF: 15m
- LTF execution TF: 30s
- Scope TF: Daily (filtering/reset scope)

## Required data by TF
### Daily
- Daily cycle timestamps (for global reset + session/day containment)

### H4 (240m)
- Cycle quarter classification: h4_c ∈ {1,2,3,4}
- Acceptable for this setup: h4_c ∈ {3,4}

### Micro (from QTEngine)
- micro_q ∈ {1,2,3,4}
- micro quarter timestamps: micro_q1_ts..micro_q4_ts, micro_end_ts
- micro.tCISD level (float)

### m15
- FVG detection
- SMT-F detection (paired across ES/NQ)

### 30s
- Micro SSMT detection (paired across ES/NQ) scoped to quarter transitions:
  - Q1→Q2 SSMT
  - Q3→Q4 SSMT
