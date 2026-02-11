# Task 4: Buy Strategy — Mortgage Amortisation

**Methodology section:** §4.3 (mortgage)

## Goal

Implement the fixed-rate annuity mortgage as specified in the methodology. Clean monthly amortisation schedule — no prepayment logic.

## Equations

$$\text{pmt} = M(0) \cdot \frac{i(1+i)^{12N}}{(1+i)^{12N} - 1}$$

where $i = \text{rate}/12$.

Each month:

$$\text{interest}(t) = M(t-1) \cdot i$$

$$M(t) = M(t-1) - (\text{pmt} - \text{interest}(t))$$

## Inputs

| Parameter | Symbol | Type |
|---|---|---|
| Initial mortgage balance | $M(0)$ | € (from Task 3) |
| Annual mortgage rate | rate | %/yr |
| Mortgage term | $N$ | years |

## Existing Code

`mortgage.py` has `_monthly_mortgage_payment` (correct formula) and `_simulate_payoff_years` (adds prepayment/notice logic not in the methodology). The methodology calls for a simpler, cleaner implementation.

## What to Build

1. A function `monthly_payment(principal, annual_rate, years) -> float`.
2. A function that produces the full amortisation schedule: arrays of `M(t)`, `interest(t)`, `principal(t)` for each month.

## Verification

- [ ] Unit test: €400k loan, 3.4%/yr, 25yr → verify monthly payment matches financial calculator (expect ~€1,983)
- [ ] Unit test: after 12*25 = 300 months, verify `M(300) ≈ 0` (within rounding)
- [ ] Unit test: sum of all interest payments == total paid - principal
- [ ] Unit test: `interest(0) = M(0) * rate/12`
- [ ] Edge case: rate == 0 → `pmt = principal / (years * 12)`
