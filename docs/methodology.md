# Rent-and-Invest vs Buy-to-Live

## Goal

Compare terminal net worth of two strategies over a fixed horizon T (e.g. 30 years) for a salaried worker in Vienna. The question: _at year T, which strategy leaves you richer?_

```
NW(T) = liquid_assets(T) + illiquid_assets(T) − liabilities(T)
```

Secondary output: breakeven year and sensitivity ranges.

---

## Method

Month-by-month simulation. Both strategies share the same income stream and cost-of-living. The only difference is how the housing-related cash flow is structured. Any surplus is invested identically.

### Shared cash flow

```
gross(t)    = gross_0 × (1 + wage_growth)^t          # nominal wage growth
net(t)      = austrian_tax(gross(t))                  # 14-salary system, progressive brackets
col(t)      = col_0 × (1 + inflation)^t              # cost of living excl. housing
savings(t)  = net(t) − col(t)                         # disposable income for housing + investing
```

### Strategy A — Rent-and-Invest

Each month:
```
rent(t)       = rent_0 × (1 + rent_growth)^t
investable(t) = savings(t) − rent(t)
portfolio(t)  = portfolio(t−1) × (1 + r_monthly) + investable(t)
```

Terminal net worth:
```
NW_rent(T) = portfolio(T) − KESt(T)
KESt(T)    = 0.275 × max(0, portfolio(T) − Σ contributions)
```

### Strategy B — Buy-to-Live

At t=0, deploy cash savings as down payment + upfront costs. Each month:
```
housing(t)    = mortgage_payment + own_costs(t)       # fixed annuity + inflation-adjusted maintenance
investable(t) = max(0, savings(t) − housing(t))
portfolio(t)  = portfolio(t−1) × (1 + r_monthly) + investable(t)
```

Terminal net worth:
```
NW_buy(T) = property(T) + portfolio(T) − KESt(T) − mortgage_balance(T)
property(T) = price_0 × (1 + appreciation)^T
```

---

## Parameters and assumptions

### Shared

| Parameter | Value | Rationale |
|---|---|---|
| Horizon T | 30 yr | Standard for lifecycle comparison |
| Inflation | 2.0% | ECB target rate |
| Wage growth | 2.5% nominal | ≈ inflation + 0.5% real; conservative for tech |
| CoL (excl. housing) | ~€630/mo | Numbeo, single person, Vienna |
| Investment return | 7.0% nominal | MSCI World Net TR, 1978–2024 CAGR ≈ 10.5% gross, minus ~0.2% TER, minus tax drag ≈ 7% after-cost; or use 5% real + 2% inflation |
| KESt | 27.5% flat | Austrian capital gains tax on realized gains |

### Rent path

| Parameter | Value | Source |
|---|---|---|
| Starting rent | €21/m² × 80m² = €1680/mo | 2025 Vienna avg incl. Betriebskosten |
| Rent growth | 3.0% nominal | Mietpreisindex: historically ≈ CPI + 1pp |

### Buy path

| Parameter | Value | Source |
|---|---|---|
| Purchase price | €500k | 80m² Vienna median |
| Upfront costs | ~12.5% of price | GrESt 3.5% + Notar 2.4% + Makler 3.6% + Grundbuch 1.1% + bank 3% |
| Down payment | ≥20% | KIM-VO regulation |
| Mortgage rate | 3.4% fixed | 2025 Austrian market rate |
| Term | 25 yr | Standard |
| Ownership costs | ~€650/mo | Betriebskosten + Rücklage + Grundsteuer + insurance + utilities |
| Property appreciation | 2.5% nominal | OeNB Wohnimmobilienpreisindex Vienna, long-run avg |
| Maintenance capex | 1.0% of value/yr | Standard planning assumption |

---

## Investment benchmark

Use **MSCI World Net Total Return Index (USD or EUR-hedged)** as the single benchmark. Justification:
- Most widely used passive global equity index
- Represents the "default" retail investor portfolio (e.g. single-ETF strategy via iShares MSCI World UCITS, TER 0.20%)
- Backtestable from 1969 (gross) / 1978 (net) via msci.com or curvo.eu

For the simulation, use a **fixed annual CAGR** (deterministic). Optional extension: Monte Carlo with log-normal returns calibrated to historical μ and σ.

---

## What makes this comparison fair

1. **Same income stream.** Both strategies start with the same gross salary and savings.
2. **Opportunity cost is explicit.** The renter invests what the buyer spends on down payment + closing costs at t=0.
3. **Surplus investing is symmetric.** Both strategies invest any leftover savings into the same index fund.
4. **Tax treatment is complete.** Income tax, KESt on investment gains, and transaction taxes on purchase are all modeled.
5. **All housing costs included.** Rent path: rent. Buy path: mortgage + ownership + maintenance + upfront costs. No hidden costs on either side.

---

## Computation outline

```python
for month in range(T * 12):
    # shared
    savings = net_salary(gross * (1 + g)^(month/12)) - col * (1 + π)^(month/12)

    # rent
    rent = rent_0 * (1 + rent_g)^(month/12)
    rent_invest = savings - rent
    rent_portfolio = rent_portfolio * (1 + r/12) + rent_invest

    # buy
    mortgage_pmt = annuity(principal, rate, term)  # fixed
    own_costs = own_costs_0 * (1 + π)^(month/12)
    buy_invest = max(0, savings - mortgage_pmt - own_costs)
    buy_portfolio = buy_portfolio * (1 + r/12) + buy_invest
    mortgage_balance = amortize(balance, rate, pmt)

# terminal
nw_rent = rent_portfolio - 0.275 * max(0, rent_portfolio - rent_contributions)
nw_buy  = price * (1 + appr)^T + buy_portfolio - 0.275 * max(0, buy_portfolio - buy_contributions) - mortgage_balance

breakeven = first year where nw_buy > nw_rent
```

---

## Output

1. **Net worth over time** — two curves, one per strategy.
2. **Breakeven year** — crossover point (if any).
3. **Sensitivity table** — vary key params (return ±2pp, rent growth ±1pp, appreciation ±1pp, mortgage rate ±1pp) and show terminal NW delta.
