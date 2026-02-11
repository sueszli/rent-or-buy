# Task 7: Terminal Net Worth Calculation

**Methodology section:** §3, end of §4.2, end of §4.3

## Goal

Compute terminal net worth for both strategies, applying Austrian capital gains tax (KESt) correctly.

## Equations

**Renter:**
$$NW_{\text{rent}}(T) = P_r(T) - 0.275 \cdot \max\!\left(0,\; P_r(T) - \Sigma_r(T)\right)$$

**Buyer:**
$$NW_{\text{buy}}(T) = V(T) + P_b(T) - 0.275 \cdot \max\!\left(0,\; P_b(T) - \Sigma_b(T)\right) - M(T)$$

**Tax notes:**
- 27.5% KESt on investment portfolio gains only
- No Immobilienertragsteuer on primary residence held >2 years (Hauptwohnsitzbefreiung)

## Inputs

| Value | Source |
|---|---|
| $P_r(T)$, $\Sigma_r(T)$ | Task 2 |
| $P_b(T)$, $\Sigma_b(T)$ | Task 6 |
| $V(T)$ | Task 6 |
| $M(T)$ | Task 4 |

## Dependencies

- Tasks 2, 4, 6

## What to Build

1. `nw_rent(P_r, Sigma_r) -> float`
2. `nw_buy(V, P_b, Sigma_b, M) -> float`
3. `delta_nw(nw_buy, nw_rent) -> float`
4. `breakeven_year(nw_rent_curve, nw_buy_curve) -> int | None`

## Verification

- [ ] Unit test: `P_r=500000`, `Σ_r=300000` → KESt = `0.275 * 200000 = 55000`, NW = `445000`
- [ ] Unit test: zero gains (`P_r == Σ_r`) → no tax, NW = portfolio value
- [ ] Unit test: portfolio loss (`P_r < Σ_r`) → no tax (max with 0)
- [ ] Unit test: buyer with `V=600000`, `P_b=100000`, `Σ_b=80000`, `M=200000` → NW = `600000 + 100000 - 0.275*20000 - 200000 = 494500`
- [ ] Unit test: breakeven detection — supply two curves where buy overtakes rent at year 15, verify `breakeven_year == 15`
- [ ] Edge case: buy never overtakes rent → returns `None`

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
