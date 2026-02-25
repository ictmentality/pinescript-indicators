Monthly Cycle Specifications

Scope (phase 1 only)
- Monthly cycle dividers (vertical quarter boundaries)
- Monthly opening lines (Q1 open + true open + quarter opens)
- No monthly SSMT in this phase

Core rule
- A Monthly Cycle can contain up to 5 quarters (M.Q1..M.Q5).
- Monthly quarters are week-based (Sunday 18:00 New York to next Sunday 18:00).
- A week belongs to a month when that week's Monday belongs to that month.

Definition of "full week" for monthly assignment
- A full week is the Monday-Thursday block of a trading week.
- The first monthly quarter (M.Q1) starts only on a week whose Monday is inside the month.
- If day 1 of the calendar month starts on Tuesday (or any day after Monday), that first partial week is not M.Q1 for the new month. It remains M.Q5 of the prior month.

Monthly True Open
- Monthly Q2 Open (Monthly Cycle True Open) is the second Monday of the month.
- "Second Monday" is the calendar selector for which week is M.Q2.
- Trading boundary for M.Q2 is the start of that week: Sunday 18:00 New York.
- Use effective first printed bar at/after the M.Q2 boundary (not Monday 18:00).

Time anchors (CME/Globex context)
- Timezone: America/New_York
- Weekly boundary anchor for monthly quarters: Sunday 18:00
- Monday is used only for month-assignment/second-Monday logic.
- Quarter/open lines are anchored to the weekly trading boundary (Sunday 18:00) using effective first printed bar timing.

Behavior from reference images

Normal vs Distorted (quick test)
- Normal month = 4 qualified Mondays in that month -> 4 quarters (M.Q1..M.Q4).
- Distorted month = 5 qualified Mondays in that month -> 5 quarters (M.Q1..M.Q5).

Normal month example (helpers/Normal_Month_Example.jpg)
- This screenshot is the 4-quarter case.
- Visible weekly boundaries: Sun 01/04/2026 18:00, Sun 01/11/2026 18:00, Sun 01/18/2026 18:00, Sun 01/25/2026 18:00, Sun 02/01/2026 18:00.
- Qualified Mondays for this month (January 2026): 01/05, 01/12, 01/19, 01/26 (four Mondays).
- Purple labels in the screenshot align to these windows:
  - M.Q1: Sun 01/04 18:00 -> Sun 01/11 18:00
  - M.Q2: Sun 01/11 18:00 -> Sun 01/18 18:00
  - M.Q3: Sun 01/18 18:00 -> Sun 01/25 18:00
  - M.Q4: Sun 01/25 18:00 -> Sun 02/01 18:00
- The week starting Sun 12/28/2025 18:00 is not January M.Q1; it belongs to the prior month.
- Second Monday of January 2026 is Mon 01/12/2026, so Monthly True Open is the open at/after Sun 01/11/2026 18:00 (M.Q2 start).

Distorted month example (helpers/Distorted_Month_Example.jpg)
- This screenshot is the 5-quarter case.
- Visible weekly boundaries: Sun 11/30/2025 18:00, Sun 12/07/2025 18:00, Sun 12/14/2025 18:00, Sun 12/21/2025 18:00, Sun 12/28/2025 18:00, Sun 01/04/2026 18:00.
- Qualified Mondays for this month (December 2025): 12/01, 12/08, 12/15, 12/22, 12/29 (five Mondays).
- Purple labels in the screenshot align to these windows:
  - M.Q1: Sun 11/30 18:00 -> Sun 12/07 18:00
  - M.Q2: Sun 12/07 18:00 -> Sun 12/14 18:00
  - M.Q3: Sun 12/14 18:00 -> Sun 12/21 18:00
  - M.Q4: Sun 12/21 18:00 -> Sun 12/28 18:00
  - M.Q5: Sun 12/28 18:00 -> Sun 01/04 18:00
- Second Monday of December 2025 is Mon 12/08/2025, so Monthly True Open is the open at/after Sun 12/07/2025 18:00 (M.Q2 start).

Divider and open-line requirements (for implementation)
- Draw quarter divider verticals at monthly quarter starts (M.Q1..M.Q5 when present).
- Draw projected divider(s) for next unrealized monthly quarter boundary.
- Draw Q1 open line from M.Q1 start through monthly end.
- Draw true-open line from M.Q2 open (second Monday) through monthly end.
- Draw quarter-open lines for M.Q3, M.Q4, and M.Q5 (if M.Q5 exists), each extending until next quarter boundary (or month end for last quarter).

Resolved decision before coding
- For a month with only 4 qualified weeks, expose M.Q1..M.Q4 and keep M.Q5 fields as na (unused).
- Do not remap/relabel quarters to force a synthetic M.Q5.
- Reuse weekly boundary realization mechanics (effective first printed bar + time_close > boundaryTs), but keep monthly quarter count dynamic (4 or 5).
- Month end is week-based: the end of the monthly cycle is the next month's M.Q1 boundary.
- This means M.Q5 can include data from the next calendar month when the week extends across month-end (as in the distorted example).
