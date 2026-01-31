Understood — make `bhTs` / `blTs` **first-class fields** in `QuarterRecord` (not optional), and treat them exactly like `hTs/lTs`: they track the **timestamp of the bar that *set* the current extreme**, updating whenever the extreme updates.

Here’s the updated implementation plan (no code edits yet).

---

## 1) Struct changes: `QuarterRecord` gets 4 new required fields

### Touchpoint

`export type QuarterRecord` 

### Add (required)

* `float bh`  — quarter body high
* `float bl`  — quarter body low
* `int bhTs`  — timestamp of the bar that set `bh`
* `int blTs`  — timestamp of the bar that set `bl`

**Semantic contract**

* `bh = max(bodyHigh)` over bars in the quarter
* `bl = min(bodyLow)`  over bars in the quarter
* `bhTs` is the `time` of the bar where `bh` was first achieved (and updated if a later bar makes a higher `bh`)
* `blTs` same idea for `bl`

---

## 2) Constructor updates (mandatory or you’ll break compilation)

You must update **every** `QuarterRecord.new(...)` call to include the new fields.

### A) `qt_state_new()` → `nilQ`

This seeds all cycle states. 
Add:

* `bh = na`, `bl = na`, `bhTs = na`, `blTs = na`

### B) `f_make_empty_q(qStart)`

This is used whenever quarters are reinitialized. 
Also add the same `na` initializers.

---

## 3) Aggregation update: `f_q_apply_bar(...)` maintains bh/bl + timestamps

### Touchpoint

`f_q_apply_bar(...)` 

### Per-bar derived values

* `barBH = max(o, c)`
* `barBL = min(o, c)`

### On first bar of quarter (`not q.has`)

Initialize:

* `q.bh := barBH`
* `q.bl := barBL`
* `q.bhTs := t`
* `q.blTs := t`

### On subsequent bars

Update with timestamp tracking:

* If `barBH > q.bh`:

  * `q.bh := barBH`
  * `q.bhTs := t`
* If `barBL < q.bl`:

  * `q.bl := barBL`
  * `q.blTs := t`

> **Timestamp choice:** use `t` (bar open time), same convention you already use for `hTs/lTs` inside this function. If you ever want “body extreme close timestamp” instead, that would require passing `tClose` into `f_q_apply_bar`, which is a larger signature change. For HSSMT and debugging, bar open `t` is consistent and sufficient.

---

## 4) Carry-forward and finalize logic: no new code needed (but verify behavior)

You do **not** need to touch:

* `f_q_clear_evts` 
* `f_q_finalize` 
* `f_finalize_and_roll` 

Because:

* The entire `QuarterRecord` gets rolled into `prev1/prev2`, so your new fields will roll automatically. 

---

## 5) Critical alignment step: copy bh/bl + bhTs/blTs anywhere you override OHLC from aligned records

This is the most important “don’t subtly break alignment” part.

### Micro/Nano override block

You currently overwrite `h/l/c` (and timestamps) from `aq*` into `q*`. 
You must also copy:

* `qX.bh := aqX.bh`
* `qX.bl := aqX.bl`
* `qX.bhTs := aqX.bhTs`
* `qX.blTs := aqX.blTs`

Otherwise:

* wick/close would be aligned, but body extremes would still be chart-TF aggregated (inconsistent).

### m90 override block

You currently overwrite `o` and `c` from aligned records. 
For consistency (and to make m90 HSSMT meaningful), also copy:

* `bh/bl` and `bhTs/blTs` from `aq*` into `q*`

---

## 6) What this enables immediately

Once this is in the engine:

* Any indicator (including `QTEngineTest`) can compute HSSMT from **quarter records only**:

  * Prior ref: `prev1.bh` (bearish) / `prev1.bl` (bullish)
  * Current progress: active quarter’s `bh/bl`
* You no longer need per-indicator rolling body-extreme state.

---

## 7) Cost / footprint (so you know what you’re buying)

Per `QuarterRecord` you add:

* 2 floats + 2 ints

Given you store several quarters per cycle plus aligned mirrors, this is still small relative to the benefit (and way smaller than repeating state per indicator).


 I can map **exactly which “aligned record” structs** (your `aq*` variants) ields so the copy logic compiles cleanly across all cycles—still without 
