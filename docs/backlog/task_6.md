# Task 6: Buy Strategy — Surplus Investing & Property Appreciation

**Methodology section:** §4.3 (surplus investing + property appreciation)

## Goal

After paying mortgage and ownership costs, invest the surplus. Track the buyer's portfolio alongside property value growth.

## Equations

$$\text{surplus}(t) = \text{savings}(t) - \text{pmt} - \text{own}(t)$$

$$P_b(t) = P_b(t-1) \cdot \left(1 + \frac{r}{12}\right) + \max(0,\;\text{surplus}(t))$$

$$\Sigma_b(t) = \Sigma_b(t-1) + \max(0,\;\text{surplus}(t))$$

$$V(T) = \text{price} \cdot (1 + g_a)^T$$

**Initial condition:** $P_b(0) = 0$, $\Sigma_b(0) = 0$.

**Constraint:** if $\text{surplus}(t) < 0$, the buyer cannot afford the property. This is a constraint violation, not a modeled scenario.

## Inputs

| Parameter | Symbol | Type |
|---|---|---|
| `savings(t)` | from Task 1 | €/mo |
| `pmt` | from Task 4 | €/mo |
| `own(t)` | from Task 5 | €/mo |
| Annual investment return | $r$ | %/yr |
| Annual property appreciation | $g_a$ | %/yr |
| Purchase price | price | € |

## Dependencies

- Task 1, Task 4, Task 5

## What to Build

1. A simulation function that runs month-by-month for `12*T` months, returning arrays of `P_b(t)` and `Σ_b(t)`.
2. A function `property_value(T, price, g_a) -> float`.
3. Validation: check `surplus(t) >= 0` at every step, raise error if violated.

## Verification

- [ ] Unit test: with `savings=3000`, `pmt=2000`, `own=500`, `r=0.07`, `C_0=0` — run 12 months, verify `P_b(12)` and `Σ_b(12)` against hand calc
- [ ] Unit test: `property_value(10, 500000, 0.02)` == `500000 * 1.02^10`
- [ ] Unit test: `surplus(t) < 0` raises constraint error
- [ ] Edge case: `surplus(t) == 0` — portfolio only grows from returns, no new contributions

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
