# Task 8: Simulation Runner

**Methodology section:** §4 (overall structure)

## Goal

Wire all modules together into a single simulation entry point. Run both strategies month-by-month with the same shared income/expense model and produce comparable results.

## Structure

```
for t in range(12 * T):
    savings = savings_monthly(t, ...)

    # Rent strategy
    rent = rent_monthly(t, ...)
    P_r, Σ_r = update_rent_portfolio(...)

    # Buy strategy
    interest, M = update_mortgage(...)
    own = ownership_costs_monthly(t, ...)
    surplus = savings - pmt - own
    P_b, Σ_b = update_buy_portfolio(...)

NW_rent = nw_rent(P_r, Σ_r)
NW_buy = nw_buy(V(T), P_b, Σ_b, M)
```

## Inputs

All parameters from §7 of the methodology (see parameter table).

## Dependencies

- Tasks 1–7 (all modules)

## What to Build

1. A `SimulationParams` dataclass (or dict) holding all inputs.
2. A `run_simulation(params) -> SimulationResult` function that returns monthly NW curves for both strategies, terminal NW, ΔNW, and breakeven year.
3. Replace the placeholder `main.py` with this.

## Fairness Constraints (§6)

Verify inside the simulation:
- Both strategies use the same `savings(t)` — identical income/expense model
- Both strategies use the same investment return `r`
- Starting cash `C_0` is the same for both

## Verification

- [ ] Smoke test: run with baseline Vienna params (€58k salary, €500k property, €200k cash, 25yr horizon), check both NW > 0
- [ ] Verify `savings(t)` is computed once and shared (not duplicated)
- [ ] Verify renter invests `C_0` at t=0, buyer invests `0` at t=0
- [ ] Verify buyer's mortgage balance reaches 0 at or before year N
- [ ] Output structure contains all four items from §8 (NW curves, ΔNW, breakeven, sensitivity data placeholder)

## Quality

Make sure to follow the `CONTRIBUTING.md` file for code style.
