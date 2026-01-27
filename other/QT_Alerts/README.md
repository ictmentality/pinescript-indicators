# QT Alerts (QTEngine-powered)

Purpose:
- Build alert-only indicators that sequence Quarterly Theory conditions using QTEngine as the source of cycle/quarter identity + levels.
- Each setup emits two alerts:
  1) Setup Armed
  2) Entry Now

Design rules:
- QTEngine provides: cycle timestamps, quarter identity, True Opens/tCISD/levels.
- Indicator provides: event detection (SSMT, FVG, SMT-F, etc.), scenario FSM, alerts.
- All multi-timeframe logic is evaluated on its native timeframe via request.security().
- Alerts are edge-triggered (fire once per qualifying transition).
