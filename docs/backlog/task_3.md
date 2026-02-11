# Task 3: Buy Strategy — Upfront Costs & Down Payment

**Methodology section:** §4.3 (initial conditions)

## Goal

Compute closing costs, down payment, and initial mortgage balance. Refactor/verify the existing `_upfront_costs` in `mortgage.py`.

## Equations

$$\text{down} = C_0 - \text{upfront\_costs}(\text{price}, M_0)$$

$$M(0) = \text{price} - \text{down}$$

## Upfront Cost Components

| Fee | Rate | Base |
|---|---|---|
| Grunderwerbsteuer | 3.5% | purchase price |
| Notary | ~2.4% (2% + 20% VAT) | purchase price |
| Agent | 3.6% (3% + 20% VAT) | purchase price |
| Land registry | 1.1% | purchase price |
| Bank processing | ~3% | mortgage amount |
| Mortgage registration | 1.2% | mortgage amount |
| Fixed admin fees | ~€128 | flat |

**Constraint:** `C_0` must cover at least 20% down payment + all closing costs (KIM-VO).

## Existing Code

`mortgage.py` has `_upfront_costs` and `_mortgage_amount`. Both exist but are marked "WARNING: inaccurate". The land registry and mortgage registration fee functions have tiered logic (free under €500k) that needs to be verified against current law.

## What to Build

1. Clean `upfront_costs(price, mortgage_amount) -> float` function.
2. Clean `initial_mortgage(price, C_0) -> tuple[float, float, float]` returning `(mortgage_amount, down_payment, upfront_costs)`.
3. Validation that `C_0` is sufficient.

## Verification

- [ ] Unit test: for €500k property with €200k cash, verify upfront costs match sum of statutory rates
- [ ] Cross-check: compare total upfront costs against [Erste Bank calculator](https://www.sparkasse.at/erstebank/privatkunden/wohnen/immobilienfinanzierung/kosten-eigentumswohnung) for same inputs
- [ ] Unit test: verify `mortgage_amount + down_payment == price`
- [ ] Unit test: verify `C_0 - upfront_costs == down_payment` (accounting identity)
- [ ] Edge case: cash exactly covers minimum down + costs → mortgage == 80% of price
- [ ] Edge case: insufficient cash → raises error
