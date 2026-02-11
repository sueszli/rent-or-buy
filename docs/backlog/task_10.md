# Task 10: Sensitivity Analysis

**Methodology section:** §8.4

## Goal

Sweep key parameters to show how the rent-vs-buy answer changes with different assumptions.

## Specification

Independently vary each of the following by ±1–2 percentage points from the base case:

| Parameter | Symbol | Base case | Sweep range |
|---|---|---|---|
| Investment return | $r$ | 7% | 5%–9% |
| Rent growth | $g_r$ | 3% | 1%–5% |
| Property appreciation | $g_a$ | 2% | 0%–4% |
| Mortgage rate | rate | 3.4% | 1.4%–5.4% |

For each variation, report:
- $\Delta NW(T)$
- Breakeven year (or "none")

Identify which parameter the answer is **most sensitive to** (largest swing in ΔNW).

## Dependencies

- Task 8 (simulation runner)

## What to Build

1. A function `run_sensitivity(base_params, sweep_config) -> DataFrame/dict` that runs the simulation for each parameter variation.
2. Format output as a table: rows = parameter variations, columns = ΔNW, breakeven year.

## Verification

- [ ] Unit test: verify sweep produces expected number of scenarios (4 params × ~5 values each = ~20 runs, or whatever grid is chosen)
- [ ] Sanity check: higher `r` should favour renting (larger NW_rent)
- [ ] Sanity check: higher `g_a` should favour buying (larger property value)
- [ ] Sanity check: higher mortgage rate should favour renting (more interest paid)
- [ ] Sanity check: higher `g_r` should favour buying (rent becomes more expensive)

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
