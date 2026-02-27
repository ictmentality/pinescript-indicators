TPD/SSMT TODO


3) tCISD Level
4) 1st P FVG
5) Entry, Stop, & Take Profit
6) Add togglebox for Expansion Invalidation
7) Remove Require SMT C2-C3 user toggle, it is always require for this model




Expansion Candle Invalidation:
Expansion Invalidation level = 50% of C2 on the failure-swing asset.
- Use 50% of the whole candle range when the C2 body is larger than the upper wick and lower wick combined.
- Example formula: `(C2 High + C2 Low) / 2`.
- Note: On the H6 example, C3 opened below both the open and close of H6 C2. This may be important later.

Expansion Invalidation level = 50% of C2 Rejection Wick
- Use 50% of the wick if the directional wick >= C2 body
- Directional Wick definitions: Bearish setup = Upper wick, Bullish Setup = Lower Wick


Alert System:
- Stage 1: HTF C3 open (if there is valid TPD setup). Alert Message: "{Asset}, {Timeframe}, {Direction} TPD, {time}"
- Stage 2: SMT Purge (Awaiting tCISD confirmation)
- Stage 3: Setup Confirmed (tCISD confirmed)
- Stage 4: Entry (tCISD Retest)



Debug Window
Vaild TPD: Y/N
TPD w SSMT: Y/N
tCISD Confirmed: Y/N
tCISD Retest (Entry): Y/N
Invalidation Hit: Y/N
2.5R Hit: Y/N


Potential Rule Adds:
- Above/Below True Open
- If tCISD is triggered in first half of C3, then tCISD retest must occur during first half of C3 too (11/17/25 SIL1!)
- If the tCISD is triggered in the first 1/3 of C3, require tCISD confirmation on other asset
- Consider LTF 2022 model setup on Purge asset 


A+ Setup
tCISD Confirmed on both assets
Expansion Invalidation not hit






1. Post-confirm same-side sweep is not modeled as a loss state.
You correctly avoid deleting lines after confirmed/latched, but state output collapses to false instead of explicitly marking “confirmed-then-invalidated/loss”.


2. Setup activation is tied to SMT (bull_tpd and bull_smt), not Stage 1 TPD.
This makes realtime line behavior depend on SMT presence even when Stage 1 is intended to be valid without SMT.


3. Same-side invalidation cleanup clears invalidation flags back to false.
That can hide failure reason in downstream debug/alert interpretation.


4. Debug C3 direction check appears inconsistent (likely typo).
d_c3_main/d_c3_pair compare C1 close against C3 open fields.



HIGH LEVEL PLAN (H6->m15, Bearish Focus):
1. On HTF C3 open of a Valid TPD, show TPD icon on H6 and m15 timeframes. Set "Bearish Valid TPD" to true.
2. If neither asset sweeps HTF C3 High by the end of H6 C3 close, then Set "Bearish Valid TPD" to false. Wait for next valid TPD.
3. If one asset sweeps HTF C2, show Purge line (on both timeframes), set "Bearish Valid TPD/SSMT" to true.
4. If price closes below the m15 tCISD level on the m15 timeframe, set "Setup Confirmed" to true.
5. If invalidation level is hit before #4 happens (HTF C2 sweep on failure swing asset), then "Bearish Valid TPD", "Bearish Valid TPD/SSMT" should be set to false and the drawings should be deleted on both m15 and H6 timeframes.



State Machine Specs:
# Bearish TPD → Purge → tCISD Confirmation (Dyad Only)
## H6 (HTF) → m15 State Machine

This document specifies the indicator logic as a finite-state machine. It defines: (1) the dyad-only TPD definition, (2) how purgeAsset and failureSwingAsset are selected at HTF C3 open, (3) state transitions, (4) required drawings and flag outputs.

## 1) TPD Definition (Dyad Only)
TPD = Terminus Price Divergence. In dyad mode (2 assets), TPD is a 3-candle “crack in correlation” pattern where you must observe two distinct divergences inside the same C1 → C2 → C3 sequence.

1) Crack #1 (C2 close divergence / PSP component)
On Candle 2, the two assets must have opposite close direction:
- One asset closes bullish on C2 (C2 Close > C2 Open)
- The other asset closes bearish on C2 (C2 Close < C2 Open)
This is the dyad form of “C2 close divergence.” 

2) Crack #2 (C3 open vs C1 close divergence)
On Candle 3, the opening price must diverge relative to Candle 1’s close across the two assets:
- One asset’s C3 Open is above its C1 Close
- The other asset’s C3 Open is below its C1 Close
This is the dyad form of “C3 open vs C1 close divergence.” 

A valid dyad TPD exists only when both cracks occur in the same C1–C2–C3 sequence: Crack #1 present AND Crack #2 present. 

Notes:
- Often described as “two cracks in correlation inside the 3-candle swing sequence.”
- Some materials discuss the extra C1↔C3 crack as what people call TPD (often alongside PSP naming). 



## 2) Definitions and Levels
Assets:
- `A` and `B` are the two correlated assets (dyad).

Candle sequence (HTF):
- A “TPD instance” is the HTF 3-candle sequence: C1, C2, C3.
- The state machine begins at HTF C3 open for a Valid Bearish TPD.

Sweep:
- Sweep a high level: `high > level` (intrabar)
- Sweep a low level: `low < level` (intrabar)

Key levels (bearish):
- `htfC2High`: HTF C2 high level used for the bearish precondition sweep check
- `m15_tCISD`: m15 tCISD level used for confirmation

## 3) Asset Classification (Locked at HTF C3 Open)
At `HTF_C3_OPEN` of a Valid Bearish TPD, classify assets immediately and store results for the life of this TPD instance.

For each asset X ∈ {A, B}, compute:
- `X_c1Close`
- `X_c3Open`

Bearish Setup Classification (locked at HTF C3 Open):
- `purgeAsset` is the asset where: C3 Open > C1 Close
- `failureSwingAsset` is the asset where: C3 Open < C1 Close
- Tie rule (required): if either asset satisfies `C3 Open == C1 Close`, mark this TPD instance invalid at `HTF_C3_OPEN` and do not enter `TPD_ACTIVE`.

Stability rule:
- `purgeAsset` and `failureSwingAsset` are selected once at HTF C3 open and do not change for the life of the TPD instance.

## 4) Outputs (Flags)
- `bearishValidTPD` (bool)
- `bearishValidTPD_SSMT` (bool)  // true after purge condition is satisfied
- `setupConfirmed` (bool)

## 5) Drawings (Required)
Per TPD instance, the indicator must manage drawing IDs/handles for:
- TPD icon on H6
- TPD icon on m15
- Purge line on H6
- Purge line on m15
Deletion must remove drawings on both timeframes deterministically (do not rely on searching the chart).

## 6) States
- `IDLE`
- `C3_TRACKING`     // entered at HTF C3 open; track C3-only precondition/purge/confirmation logic
- `CONFIRMED`       // fully confirmed during C3
- `INVALIDATED`     // transient, immediately transitions to IDLE
- `EXPIRED`         // transient at HTF_C4_OPEN when not confirmed, immediately transitions to IDLE

## 7) Decision Tree (State Transitions)

STATE: IDLE
Event: HTF_C3_OPEN AND ValidBearishTPD == true
Pre-check:
- If tie rule is true for either asset (`C3 Open == C1 Close`), this instance is invalid.
  Actions:
  - Keep flags false: bearishValidTPD = false; bearishValidTPD_SSMT = false; setupConfirmed = false
  - Do not draw TPD icon or purge line
  - Reset/clear instance context
  Next State: IDLE
Else:
Actions:
- Classify purgeAsset and failureSwingAsset (Section 3)
- Draw TPD icon on H6 and m15
- Set flags: bearishValidTPD = true; bearishValidTPD_SSMT = false; setupConfirmed = false
- Initialize: c2HighSwept = false; purgeSeen = false
- Capture context: purgeAsset, failureSwingAsset, htfC2High, tpdStartTs, drawing handles
Next State: C3_TRACKING

STATE: C3_TRACKING
Goal: track all C3-only setup conditions in parallel; setup expires at HTF_C4_OPEN if not confirmed.
Priority rule:
- Invalidation is evaluated before confirmation if both could occur in the same update.
Precondition monitor:
- During C3, if either asset sweeps htfC2High: set c2HighSwept = true
Purge condition:
- If c2HighSwept == true and purgeAsset sweeps htfC2High
  Actions:
  - Draw purge line on H6 and m15
  - Set bearishValidTPD_SSMT = true; purgeSeen = true
  Next State: C3_TRACKING
Invalidation (before confirmation):
- If failureSwingAsset sweeps htfC2High
  Actions:
  - bearishValidTPD = false; bearishValidTPD_SSMT = false; setupConfirmed = false
  - Delete all drawings (H6 + m15)
  - Reset stored context
  Next State: INVALIDATED → IDLE
Confirmation:
- On each m15 bar close during C3, if bearishValidTPD_SSMT == true and m15 Close < m15_tCISD
  Actions:
  - setupConfirmed = true
  Next State: CONFIRMED
Expiry:
- On HTF_C4_OPEN, if setupConfirmed == false
  Actions:
  - bearishValidTPD = false; bearishValidTPD_SSMT = false; setupConfirmed = false
  - Delete all drawings (H6 + m15)
  - Reset stored context
  Next State: EXPIRED → IDLE

STATE: CONFIRMED
Setup is confirmed.
Reset policy (locked):
- Reset on next HTF cycle boundary (`HTF_C4_OPEN` for this C3 instance).
- At `HTF_C4_OPEN`, reset runtime flags/context and return to `IDLE`.
- Drawing persistence rule at `HTF_C4_OPEN`:
  - If `setupConfirmed == false`, delete all instance drawings (H6 + m15).
  - If `setupConfirmed == true`, confirmed-instance drawings may persist; runtime state still resets to `IDLE`.

## 8) Transition Table
| Current State | Event / Trigger | Condition | Actions | Next State |
|---|---|---|---|---|
| IDLE | HTF_C3_OPEN | ValidBearishTPD AND tie rule false for both assets | classify assets; draw TPD icons; set flags; init c2HighSwept/purgeSeen | C3_TRACKING |
| IDLE | HTF_C3_OPEN | ValidBearishTPD AND tie rule true for either asset (`C3 Open == C1 Close`) | keep flags false; do not draw; reset/clear context | IDLE |
| C3_TRACKING | level check | failureSwingAsset sweeps htfC2High AND setupConfirmed == false | reset; delete drawings; reset context | INVALIDATED → IDLE |
| C3_TRACKING | level check | c2HighSwept == false AND either asset sweeps htfC2High | c2HighSwept = true | C3_TRACKING |
| C3_TRACKING | level check | c2HighSwept == true AND purgeAsset sweeps htfC2High | draw purge line; bearishValidTPD_SSMT = true; purgeSeen = true | C3_TRACKING |
| C3_TRACKING | m15 close (within C3) | bearishValidTPD_SSMT == true AND m15 Close < m15_tCISD | setupConfirmed = true | CONFIRMED |
| C3_TRACKING | HTF_C4_OPEN | setupConfirmed == false | reset flags; delete drawings; reset context | EXPIRED → IDLE |
| CONFIRMED | HTF_C4_OPEN | setupConfirmed == true | preserve confirmed drawings; reset flags/context | IDLE |

## 9) Implementation Notes
- Store and delete drawings via persistent IDs/handles for both timeframes.
- Asset classification occurs only once at HTF C3 open and must remain stable.
- During C3_TRACKING, invalidation takes precedence over confirmation when both are possible.
- All per-instance variables should be scoped to the active TPD instance via a stable identifier (e.g., tpdStartTs).
- Setup validity window is C3-only; the machine must reset at `HTF_C4_OPEN`.
