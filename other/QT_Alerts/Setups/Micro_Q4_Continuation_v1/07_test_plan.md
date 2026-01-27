# Test Plan

## Phase 1: Plumbing validation (no discretionary defs)
- Treat Q1 Accum A = true
- Treat Q3 tight distribution = true

Tests:
1) Micro quarter identity changes correctly across chart TFs.
2) E1/E3 SSMT events fire exactly once and timestamp is stable.
3) E2 “first post-SSMT FVG” stores once and persists.
4) SMT-F variants:
   - Verify V1, V2, V3 can each independently trigger E4.
   - Verify E4 fires once per variant instance (no repeats every bar).
5) ST_ARMED triggers only when all prerequisites satisfied.
6) ST_ENTRY triggers only once on first close over micro.tCISD.

## Phase 2: Add definitions
- Define "Micro.Q1 Accumulation A"
- Define "Micro.Q2 Expansion"
- Define "Micro.Q3 Tight Distribution"
Add as gates that move ST_WAIT_MICRO_Q1 → ST_Q1_ACCUM_A_OK → ... etc.

## Phase 3: Strictness knobs
- Require SMT-F to reference the stored first post-SSMT FVG only (tight mode)
- Add invalidation logic (H4 invalidation level, micro-level reclaim rules)
