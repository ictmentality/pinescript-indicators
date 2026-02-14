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


A+ Setup
tCISD Confirmed on both assets
Expansion Invalidation not hit
