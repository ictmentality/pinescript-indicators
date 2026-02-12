# Metals Dyad QT Model — v0.1 (H6/H4 TPD → LTF Crack Entry)

## 1) Purpose
Trade **Gold + Silver only** using:
- **Stage 1 (HTF):** an **H6 or H4 TPD** that forms *at a pre-defined HTF zone*.
- **Stage 2 (LTF):** a **crack in correlation** (**TPD or SSMT**) as the entry trigger inside/near that same zone.

---

## 2) Markets + Chart Stack
### Instruments 
- **Futures:** MGC1! (Gold), SIL1! (Silver)

### Timeframes
- **Setup:** H6 and/or H4
- **Refine:** m30 or m15
- **Trigger:** m5 or m1

---

## 3) Definitions (Locked)

### 3.1 TPD (as JacobSpeculates teaches/uses it)
**TPD = *Terminus Price Divergence*.** A **3-candle, multi-asset crack in correlation** requiring **two distinct divergences** inside the same **C1–C2–C3** sequence:

1) **Crack #1 (C2 close divergence / PSP component)**  
On **Candle 2**, one asset closes **bullish** while the other closes **bearish** (or vice versa).

- Bullish close: `C2 close > C2 open`
- Bearish close: `C2 close < C2 open`

2) **Crack #2 (C3 open vs C1 close divergence)**  
On **Candle 3**, the **opening price** diverges relative to **Candle 1’s close** across the assets.

- Compute, per asset: `sign(open(C3) − close(C1))`
- Divergence exists when the **sign differs** between Gold and Silver (one opens above C1 close, the other opens below; or vice versa).

**A valid TPD requires both cracks** inside the same 3-candle sequence.

**References (user-provided):**
- TradingView: “2-Stage PSP with SMT [Pogiest] — Indicator by Pogiest”
- Scribd: “PSP | PDF”

### 3.2 “Crack in Correlation” (Dyad)
A crack exists when **Gold and Silver do not do the same important thing in the same window**.

Allowed crack types in this model:
- **TPD crack** (definition above)
- **SSMT crack** (definition below)

### 3.3 SSMT (Dyad — operational)
SSMT crack = in a defined window, **one asset** takes a prior swing **high/low** (or key prior level) and the **other asset does not**, producing relative strength/weakness.

Minimum rule (simple + binary):
- **Bullish SSMT:** one sweeps prior *low* and the other doesn’t (or one fails to break down while the other does).
- **Bearish SSMT:** one sweeps prior *high* and the other doesn’t.

(Refine later with your preferred quarter-based SSMT rules; keep this version strict for v0.1.)

---

## 4) Stage 0 — Prework (HTF zones)
Before looking for TPD, mark **HTF objective zones** on both assets (same timeframe):

Allowed zones (pick 1–2 for v0.1):
- HTF **PDArray zone** you trust (e.g., FVG/BPR/gap per your QT rules)
- HTF **True Open** level
- HTF **prior quarter high/low** (external liquidity)

**Rule:** If the HTF zone is not clear, it’s **no-trade**.

---

## 5) Stage 1 — HTF Setup Filter (H6/H4 TPD)
You are only allowed to look for LTF entries when:

1) A **TPD prints on H6 or H4**, **AND**
2) It occurs **inside or at the edge** of a pre-defined HTF objective zone.

### Stage-1 Output (must be written down)
- **Setup TF:** H6 or H4
- **Zone in play:** (exact price bounds)
- **Directional plan:** *reversal-bias* unless your rules say otherwise  
  - Default v0.1 assumption: HTF TPD near an HTF zone suggests **termination / reversal potential**.
- **Hard invalidation:** the level that proves the zone + TPD failed (usually the far side of the zone or the swing extreme that created the setup).

**No-trade:** HTF TPD that forms in the middle of nowhere (not at a zone).

---

## 6) Stage 2 — LTF Trigger (Crack Confirmation)
Once Stage 1 is active, take trades only if a **LTF crack** forms **in the same HTF zone** (or immediately adjacent).

Allowed LTF triggers:
- **Trigger A: LTF TPD** (same 3-candle definition) on **M15 or M5**
- **Trigger B: LTF SSMT** on **M15 or M5**

**Window rule:** The LTF trigger must appear **soon after** the HTF setup (no “hours later” rationalizations).

---

## 7) Stage 3 — Entry, Stop, Targets (mechanical)
### Entry (default)
- Enter on **M5 confirmation** in the direction of your Stage-1 plan:
  - Conservative: **M5 close** confirming direction after the LTF trigger
  - Aggressive: pullback to the trigger’s level (only if structure stays intact)

### Stop (default)
- Place stop beyond the **level that invalidates the LTF crack narrative**:
  - For TPD-trigger: beyond the swing extreme of the 3-candle sequence or beyond the HTF zone edge (whichever is tighter but still logical)
  - For SSMT-trigger: beyond the swept level that would “undo” the crack

### Targets (default)
- **T1:** opposing edge of the HTF zone *or* nearest internal liquidity
- **T2:** next HTF objective (next PDArray / prior quarter hi/lo / True Open)

---

## 8) Risk + Governance
- Risk per trade: fixed **R** (choose % or $ and keep constant)
- 1 thesis = 1 entry plan = 1 stop (no averaging)
- If HTF zone is violated / accepted against your plan → **stand down** until a new Stage-1 setup forms
- If the crack is not **clean and binary** → skip

---

## 9) Trade Checklist (printable)
### Stage 1 (HTF)
- [ ] Instrument pair set: Gold + Silver (consistent symbols)
- [ ] HTF objective zone marked
- [ ] H6/H4 **TPD present** at/inside zone
- [ ] Invalidation level defined

### Stage 2 (LTF)
- [ ] LTF trigger inside/near same HTF zone:
  - [ ] TPD (M15/M5) **or**
  - [ ] SSMT (M15/M5)
- [ ] Trigger window is timely (not late)

### Stage 3 (Execution)
- [ ] Entry method chosen (M5 close confirm vs pullback)
- [ ] Stop is narrative-valid (not arbitrary)
- [ ] T1/T2 defined
- [ ] Risk size set (R)

---

## 10) Next locks for v0.2
- Decide whether Stage-1 TPD implies **reversal only** or can be **continuation** in acceptance regimes.
- Define “swing high/low” method for SSMT (fractals, 5-bar swings, quarter levels, etc.).
- Add a strict “session/time” constraint if you want (e.g., only take triggers during specific windows).
