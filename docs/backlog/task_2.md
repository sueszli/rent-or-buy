# Task 2: Rent Strategy — Portfolio Simulation

**Methodology section:** §4.2

## Goal

Implement the rent-and-invest strategy: pay rent each month, invest all surplus into the index fund.

## Equations

$$\text{rent}(t) = R_0 \cdot (1 + g_r)^{t/12}$$

$$P_r(t) = P_r(t-1) \cdot \left(1 + \frac{r}{12}\right) + \left[\text{savings}(t) - \text{rent}(t)\right]$$

$$\Sigma_r(t) = \Sigma_r(t-1) + \left[\text{savings}(t) - \text{rent}(t)\right]$$

**Initial condition:** $P_r(0) = C_0$, $\Sigma_r(0) = C_0$.

## Inputs

| Parameter | Symbol | Type |
|---|---|---|
| Starting monthly rent | $R_0$ | €/mo |
| Annual rent growth | $g_r$ | %/yr |
| Annual investment return (net TER) | $r$ | %/yr |
| Starting cash | $C_0$ | € |
| `savings(t)` | from Task 1 | €/mo |

## What to Build

1. A function `rent_monthly(t, R_0, g_r) -> float`.
2. A simulation function that runs month-by-month for `12*T` months, returning arrays of `P_r(t)` and `Σ_r(t)`.

## Dependencies

- Task 1 (savings function)

## Verification

- [ ] Unit test: `rent_monthly(0, 800, 0.03)` == `800`
- [ ] Unit test: `rent_monthly(12, 800, 0.03)` == `800 * 1.03`
- [ ] Unit test: run 12 months with `C_0=100000`, `savings=3000/mo`, `rent=800/mo`, `r=0.07`. Verify `P_r(12)` and `Σ_r(12)` match hand calculation.
- [ ] Edge case: `savings(t) < rent(t)` — portfolio should still decrease but remain tracked correctly
