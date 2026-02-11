# Task 5: Buy Strategy — Ownership Costs

**Methodology section:** §4.3 (ownership costs)

## Goal

Model the recurring ownership costs that grow with inflation.

## Equations

$$\text{own}(t) = O_0 \cdot (1 + \pi)^{t/12}$$

where $O_0$ includes Betriebskosten, Rücklage, Grundsteuer, insurance, and maintenance.

## Inputs

| Parameter | Symbol | Type |
|---|---|---|
| Monthly ownership costs | $O_0$ | €/mo |
| Inflation rate | $\pi$ | %/yr (same as Task 1) |

## Existing Code

`mortgage.py` has `_monthly_ownership_costs(purchase_price)` which derives costs by scaling from a "typical" €500k/80m² apartment. The methodology treats $O_0$ as a direct input instead. Decide whether to keep the scaling heuristic as a default or require explicit input.

## What to Build

1. A function `ownership_costs_monthly(t, O_0, pi) -> float`.
2. Optionally: a helper `estimate_O_0(purchase_price) -> float` that uses the existing scaling logic as a convenience default.

## Verification

- [ ] Unit test: `ownership_costs_monthly(0, 600, 0.025)` == `600`
- [ ] Unit test: `ownership_costs_monthly(12, 600, 0.025)` == `600 * 1.025`
- [ ] Unit test: `ownership_costs_monthly(60, 600, 0.025)` == `600 * 1.025^5`
- [ ] Sanity check: for a €500k/80m² apartment, verify estimated $O_0$ is in the range €400–€800/mo (cross-reference with Vienna Hausverwaltung data)

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
