# Task 1: Shared Income & Expenses Module

**Methodology section:** §4.1

## Goal

Create a module that computes `gross(t)`, `net(t)`, `expenses(t)`, and `savings(t)` as functions of month index `t`. This is the shared foundation used by both rent and buy strategies.

## Equations

$$\text{gross}(t) = \text{gross}_0 \cdot (1 + g_w)^{t/12}$$

$$\text{net}(t) = f_{\text{tax}}(\text{gross}(t))$$

$$\text{expenses}(t) = E_0 \cdot (1 + \pi)^{t/12}$$

$$\text{savings}(t) = \text{net}(t) - \text{expenses}(t)$$

## Inputs

| Parameter | Symbol | Type |
|---|---|---|
| Starting annual gross salary | $\text{gross}_0$ | €/yr |
| Nominal annual wage growth | $g_w$ | %/yr |
| Monthly non-housing expenses | $E_0$ | €/mo |
| Inflation rate | $\pi$ | %/yr |

## Existing Code

- `income_tax.net_salary(annual_gross) -> int` — already handles Austrian progressive brackets + 14-salary system. **Considered sane, no re-verification needed.**
- `cost_of_living.py` — has `EXPENSES_BREAKDOWN` and `GROSS_INCOME_BY_PERCENTILE` data dicts. Useful as defaults but no growth model yet.

## What to Build

1. A function `gross_monthly(t, gross_0, g_w) -> float` returning gross monthly salary at month `t`.
2. A function `net_monthly(t, gross_0, g_w) -> float` that calls `income_tax.net_salary` on the annualised gross at month `t` and divides by 12.
3. A function `expenses_monthly(t, E_0, pi) -> float` returning non-housing expenses at month `t`.
4. A function `savings_monthly(t, ...) -> float` returning `net(t) - expenses(t)`.

## Verification

- [ ] Unit test: `gross_monthly(0, 58300, 0.03)` == `58300 / 12`
- [ ] Unit test: `gross_monthly(12, 58300, 0.03)` == `58300 * 1.03 / 12`
- [ ] Unit test: `expenses_monthly(0, 1430, 0.025)` == `1430`
- [ ] Unit test: `expenses_monthly(12, 1430, 0.025)` == `1430 * 1.025`
- [ ] Unit test: `savings_monthly(0, ...)` == `net(0) - expenses(0)` for known inputs
- [ ] Confirm `savings(t) > 0` for median Vienna salary (€58,300) after typical expenses
