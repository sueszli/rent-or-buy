# Methodology: Rent-and-Invest vs Buy-to-Live

## 1. The Question

A salaried worker in Vienna has some starting cash and a stable income. They need a place to live. They have two options:

- **Rent** an apartment and invest all surplus income into a global equity index fund.
- **Buy** an apartment with a mortgage. The buyer does not invest any surplus income.

**Which strategy produces higher net worth after $T$ years?**

This is a capital allocation problem. The same income stream flows through two different pipelines. We simulate both month by month, track every euro, and compare terminal net worth.

## 2. Why This Is Not Obvious

The naive intuition — "buying builds equity, renting is throwing money away" — ignores three things:

1. **Opportunity cost of the down payment.** The buyer locks ~20% of the purchase price + ~12.5% closing costs into an illiquid asset at $t = 0$. The renter invests that same cash into the market immediately.
2. **Ownership is not free.** Beyond the mortgage, the buyer pays maintenance, operating costs, insurance, property tax — costs the renter doesn't have.
3. **Leverage cuts both ways.** The mortgage amplifies property gains but also amplifies losses relative to the buyer's equity.

The answer depends on the spread between investment returns, property appreciation, rent growth, and mortgage rates. The simulation resolves this numerically.

## 3. Metric

We compare **terminal net worth** — the total value of everything you own minus everything you owe at year $T$:

$$NW(T) = \text{liquid assets}(T) + \text{property equity}(T) - \text{debt}(T)$$

For the renter, this is just the investment portfolio (after tax on gains). For the buyer, this is the property value minus remaining mortgage.

**Secondary metric:** the **breakeven year** — the first $T$ at which $NW_{\text{buy}}(T) > NW_{\text{rent}}(T)$. If no crossover occurs within the horizon, renting wins outright.

## 4. Simulation Structure

Deterministic, month-by-month forward simulation. Both strategies share the same income and expense model. The only difference is how housing is paid for and where surplus cash goes.

No Monte Carlo. We use fixed growth rates and handle uncertainty through sensitivity analysis over key parameters.

---

### 4.1 Shared: Income and Expenses

Every month $t \in [0, 12T)$:

$$\text{gross}(t) = \text{gross}_0 \cdot (1 + g_w)^{t/12}$$

where $g_w$ is nominal annual wage growth.

$$\text{net}(t) = f_{\text{tax}}(\text{gross}(t))$$

where $f_{\text{tax}}$ is the Austrian income tax function (progressive brackets, 14-salary system with special treatment of 13th/14th payments).

$$\text{expenses}(t) = E_0 \cdot (1 + \pi)^{t/12}$$

where $E_0$ is baseline monthly non-housing expenses and $\pi$ is annual inflation.

$$\text{savings}(t) = \text{net}(t) - \text{expenses}(t)$$

This is the disposable income available for housing and investing each month. It is identical for both strategies.

---

### 4.2 Strategy A: Rent-and-Invest

**Initial condition.** The renter does not need a down payment. Their entire starting cash $C_0$ is invested into the index fund at $t = 0$:

$$P_r(0) = C_0$$

**Each month:**

$$\text{rent}(t) = R_0 \cdot (1 + g_r)^{t/12}$$

where $R_0$ is starting monthly rent and $g_r$ is annual rent growth.

The renter pays rent and invests everything left over:

$$P_r(t) = P_r(t-1) \cdot \left(1 + \frac{r}{12}\right) + \left[\text{savings}(t) - \text{rent}(t)\right]$$

where $r$ is annual nominal investment return (net of fund TER).

Track cumulative contributions for tax purposes:

$$\Sigma_r(t) = \Sigma_r(t-1) + \left[\text{savings}(t) - \text{rent}(t)\right]$$

with $\Sigma_r(0) = C_0$.

**Terminal net worth** (after capital gains tax):

$$NW_{\text{rent}}(T) = P_r(T) - 0.275 \cdot \max\!\left(0,\; P_r(T) - \Sigma_r(T)\right)$$

The 27.5% is Austrian KESt (flat capital gains tax), applied to the difference between portfolio value and total contributions (= realized gain at liquidation).

---

### 4.3 Strategy B: Buy-to-Live

**Initial condition.** The buyer uses their starting cash for the down payment and closing costs. Nothing left to invest:

$$\text{down} = C_0 - \text{upfront\_costs}(\text{price}, M_0)$$

$$M(0) = \text{price} - \text{down}$$

$$P_b(0) = 0$$

where $M(0)$ is the initial mortgage balance and upfront costs include Grunderwerbsteuer, notary, agent, land registry, bank fees, and mortgage registration.

**Each month — mortgage:**

The mortgage payment is a fixed annuity over the loan term $N$:

$$\text{pmt} = M(0) \cdot \frac{i(1+i)^{12N}}{(1+i)^{12N} - 1}$$

where $i = \text{rate}/12$ is the monthly interest rate.

Each month, interest accrues and principal is paid down:

$$\text{interest}(t) = M(t-1) \cdot i$$

$$M(t) = M(t-1) - (\text{pmt} - \text{interest}(t))$$

**Each month — ownership costs:**

$$\text{own}(t) = O_0 \cdot (1 + \pi)^{t/12}$$

where $O_0$ includes Betriebskosten, Rücklage, Grundsteuer, insurance, and maintenance. These grow with inflation.

**Each month — check affordability:**

$$\text{surplus}(t) = \text{savings}(t) - \text{pmt} - \text{own}(t)$$

Note: if $\text{surplus}(t) < 0$, the buyer cannot afford the house on their income. This is a constraint violation, not a modeled scenario. The buyer is assumed to consume any positive surplus (it does not contribute to net worth).

**Property appreciation:**

$$V(T) = \text{price} \cdot (1 + g_a)^T$$

where $g_a$ is annual nominal property appreciation.

**Terminal net worth:**

$$NW_{\text{buy}}(T) = V(T) - M(T)$$

Note: there is no capital gains tax on the primary residence in Austria (no Immobilienertragsteuer for Hauptwohnsitz held > 2 years).

## 5. Investment Benchmark

The **Rent-and-Invest** strategy invests surplus cash into a **global equity index fund tracking the MSCI World Net Total Return Index** via an accumulating UCITS ETF (e.g. iShares Core MSCI World, TER ~0.20%). The **Buy-to-Live** strategy does not invest.

Why this benchmark:
- It is the default "set and forget" portfolio recommended by virtually all passive investing guides.
- It is globally diversified across ~1500 large/mid-cap stocks in 23 developed markets.
- It has a continuous track record since 1969 (gross) / 1978 (net total return).
- Backtestable via MSCI factsheets, curvo.eu, or justETF.

We use the **Net Total Return** variant (dividends reinvested after withholding tax) because it reflects what an accumulating ETF actually delivers before domestic tax.

The simulation uses a **fixed annual CAGR** $r$ for the return. This is a simplification — real returns are volatile — but sensitivity analysis across a range of $r$ values captures the uncertainty without the complexity of stochastic modeling.

Historical reference for calibrating $r$: MSCI World NTR EUR, 1978–2024, annualized ≈ 9–10%. After subtracting ~0.2% TER and adjusting for the Austrian Vorabpauschale (deemed distribution tax on accumulating ETFs, minor impact), a reasonable base case is $r \approx 7\%$ nominal.

## 6. Fairness Constraints

The comparison is only valid if these conditions hold:

1. **Same starting cash.** Both strategies begin with the same $C_0$. The buyer uses it for the down payment; the renter invests it.
2. **Same income stream.** Same gross salary, same wage growth, same tax treatment.
3. **Same non-housing expenses.** Cost of living excluding housing is identical.
4. **Investment strategy.** The renter invests any surplus beyond housing costs into the index fund. The buyer does not invest surplus cash (it is assumed consumed).
5. **Comparable housing.** The rented apartment and the purchased apartment are equivalent in size, location, and quality. The rent and purchase price must correspond to the same dwelling.
6. **Complete cost accounting.** All costs are included on both sides. No free maintenance, no ignored transaction costs.

## 7. Parameters

The simulation requires the following inputs. No defaults are specified here — these are determined separately from market data and personal circumstances.

### Shared

| Symbol | Parameter | Unit | Source |
|---|---|---|---|
| $T$ | Time horizon | years | User choice |
| $\text{gross}_0$ | Starting annual gross salary | €/yr | levels.fyi, personal |
| $g_w$ | Nominal annual wage growth | %/yr | Historical wage data or assumption |
| $\pi$ | Inflation rate | %/yr | ECB, Statistik Austria VPI |
| $E_0$ | Monthly non-housing expenses | €/mo | Numbeo, personal tracking |
| $C_0$ | Starting cash savings | € | Personal |
| $r$ | Nominal annual investment return (net of TER) | %/yr | MSCI World NTR backtest |

### Rent

| Symbol | Parameter | Unit | Source |
|---|---|---|---|
| $R_0$ | Starting monthly rent (incl. Betriebskosten) | €/mo | willhaben, immoscout24, local market |
| $g_r$ | Annual rent growth | %/yr | Statistik Austria Mietpreisindex |

### Buy

| Symbol | Parameter | Unit | Source |
|---|---|---|---|
| $\text{price}$ | Purchase price | € | willhaben, immoscout24, local market |
| $\text{upfront}$ | Closing costs as fraction of price | % | Sum of statutory rates |
| $\text{down\%}$ | Down payment as fraction of price | % | KIM-VO minimum + user choice |
| $\text{rate}$ | Annual mortgage interest rate (fixed) | %/yr | Bank offers, durchblicker.at |
| $N$ | Mortgage term | years | Loan agreement |
| $O_0$ | Monthly ownership costs | €/mo | Hausverwaltung, municipal data |
| $g_a$ | Annual nominal property appreciation | %/yr | OeNB Wohnimmobilienpreisindex |

## 8. Output

1. **Net worth curves** $NW_{\text{rent}}(t)$ and $NW_{\text{buy}}(t)$ for $t \in [0, T]$.
2. **Terminal comparison:** $\Delta NW = NW_{\text{buy}}(T) - NW_{\text{rent}}(T)$.
3. **Breakeven year:** smallest $t$ such that $NW_{\text{buy}}(t) \geq NW_{\text{rent}}(t)$, or "none."
4. **Sensitivity analysis:** independently vary $r$, $g_r$, $g_a$, and mortgage rate by ±1–2 percentage points. Report how $\Delta NW(T)$ and breakeven year respond. This reveals which assumptions the answer is most sensitive to.
