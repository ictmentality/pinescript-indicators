1. Freeze a baseline in [`QT/QTDisplay.txt`](/Users/jack/Desktop/GitHub-ictmentality/pinescript-indicators/QT/QTDisplay.txt) and capture current PASS/FAIL screenshots for existing dyads.

DONE

2. Define canonical asset IDs (`ES`, `NQ`, `YM`, `RTY`, `CL`, `RB`, `6E`, `6B`, etc.) in one constants section.

3. Add one symbol parser function that returns: root ID, micro/mini flag, continuous flag, month code, year, exchange.

4. Encode dyad/triad groups as data tables (single source of truth) based on [`helpers/Asset Alignments (Root Copy).md`](/Users/jack/Desktop/GitHub-ictmentality/pinescript-indicators/helpers/Asset Alignments%20(Root%20Copy).md).

5. Add one resolver function for Dyad Auto: `chart symbol -> canonical peer ID -> concrete contract symbol`.

6. Keep manual modes unchanged initially; wire only Dyad Auto through the new resolver.

7. Replace both “actual” and “expected” dyad selection paths to call the same resolver output.

8. Keep existing futures modifier call (`f_ssmt_apply_futures_modifiers`) after resolution so behavior stays consistent.

9. Add temporary debug outputs for parser/resolver fields (canonical ID, contract profile, resolved peer).

10. Run a test matrix for each dyad group across current, micro, and continuous variants.

11. Fix edge cases (exchange aliasing, JSON-like `tickerid`, micro fallback rules) until matrix is stable.

12. Extend the same resolver approach to Triad Auto (still local in `QTDisplay`).

13. Extract resolver functions and mapping tables into a new Pine library with identical function signatures.

14. Import library back into `QTDisplay`, retest full matrix, then roll into other indicators.