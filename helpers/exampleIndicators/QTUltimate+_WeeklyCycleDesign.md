# Weekly Cycle Design (QT Ultimate+)

Source indicator: `helpers/exampleIndicators/QTUltimate+`

## Overview
Weekly segmentation is derived from the Daily A session start (18:00-00:00)
using a user-set UTC offset. On the first bar of that session the script
advances the New York calendar day by +1 to define the "trueday" trading day.

## Timebase and boundaries
- `day_week = dayofweek(time, "America/New_York")` (DST-aware).
- Session windows (including Daily A `1800-0000`) use
  `tz = "UTC±<tz_incr>"` (fixed offset; default `-5`).
- `trueday` updates only when `is_sesq` flips from false to true.

## Weekly mapping
`trueday` is set to the next calendar day:
- Sunday(1) -> Monday(2)
- Monday(2) -> Tuesday(3)
- Tuesday(3) -> Wednesday(4)
- Wednesday(4) -> Thursday(5)
- Thursday(5) -> Friday(6)
- Friday(6) -> Saturday(7)
- Saturday(7) -> Sunday(1)

Weekly buckets then map as:
- trueday=2 -> "A" / "Weekly A"
- trueday=3 -> "M" / "Weekly B"
- trueday=4 -> "D" / "Weekly C"
- trueday=5 -> "X" / "Weekly D"
- trueday=6 -> "Fr" / "Weekly x"
- trueday=7 -> "Sat" / "Weekly x"
- trueday=1 -> "Sun" / "Weekly x"

## Rendering behavior
- Weekly changes are detected via `val_sesW` and `newW`, feeding `f_allrun`.
- Friday through Sunday are labeled "Weekly x" (not A/B/C/D).

## Edge cases / limitations
- Weekly boundaries are tied to the Daily A session start, not to calendar
  midnight or a Sunday 18:00 weekly boundary.
- `day_week` uses New York time while sessions use fixed UTC offsets, so DST
  shifts require manual `tz_incr` adjustment to keep alignment.
- If data is missing at the session start, `trueday` persists until the next
  Daily A start.

## Design implications for QTEngine
- This is a daily-session-driven weekly map with an explicit +1 day shift.
- It is not a pure calendar-week model and has no intent/effective boundaries.
