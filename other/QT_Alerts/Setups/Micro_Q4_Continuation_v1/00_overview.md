# Micro.Q4 Continuation (v1)

Goal:
- Alert a Micro.Q4 continuation trade using:
  - HTF context: H4 is C3 or C4
  - MTF validator: m15 SMT-F (ALL supported variants)
  - LTF execution: 30s Micro.SSMT
  - Final validation: close over Micro.tCISD

Narrative (target model):
- Micro.Q1: Accumulation A (definition TBD)
- Micro.SSMT Q1→Q2
- Micro.Q2: Expansion (creates the m15 FVG)
- Micro.Q3: Tight Distribution (not expansive; definition TBD)
- Micro.SSMT Q3→Q4
- Setup Armed after SMT-F validates the post-SSMT FVG context
- Entry Now on first close over Micro.tCISD while armed
