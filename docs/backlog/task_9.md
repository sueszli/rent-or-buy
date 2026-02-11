# Task 9: Output & Visualisation

**Methodology section:** §8

## Goal

Generate the four outputs specified by the methodology.

## Required Outputs

1. **Net worth curves** — $NW_{\text{rent}}(t)$ and $NW_{\text{buy}}(t)$ plotted over $t \in [0, T]$.
2. **Terminal comparison** — $\Delta NW = NW_{\text{buy}}(T) - NW_{\text{rent}}(T)$, printed with sign.
3. **Breakeven year** — smallest $t$ where $NW_{\text{buy}}(t) \geq NW_{\text{rent}}(t)$, or "none".
4. **Sensitivity analysis results** — table or chart (see Task 10).

## Dependencies

- Task 8 (simulation results)
- Task 10 (sensitivity data, for output #4)

## What to Build

1. A plotting function that takes NW curves and produces a line chart (matplotlib or similar).
2. A summary printer that outputs ΔNW and breakeven year.
3. A sensitivity table/chart renderer.

## Verification

- [ ] Visual: run simulation with default params, verify plot shows two curves over time
- [ ] Visual: verify curves are labelled (rent vs buy) and axes are labelled (year, €)
- [ ] Verify breakeven annotation on plot matches computed value
- [ ] Verify terminal ΔNW printed value matches plot endpoint difference

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
