import pathlib
import re

import deal
import polars as pl

"""
Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)

- data from curvo.eu/backtest/
- most "neutral" portfolio possible. dilutes US exposure.
- must invest at least 10 years
"""

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

# Approx historical inflation 2%
INFLATION_MONTHLY = (1.02) ** (1 / 12) - 1


@deal.pre(lambda monthly_savings, start_month, months, **kwargs: bool(re.match(r"^\d{2}/\d{4}$", start_month)))
@deal.pre(lambda monthly_savings, start_month, months, **kwargs: 0 <= months <= 1200)
@deal.pre(lambda monthly_savings, start_month, months, **kwargs: 0 <= monthly_savings <= 1e9)
@deal.ensure(lambda monthly_savings, start_month, months, real, result, **kwargs: len(result) == months + 1)
def simulate_portfolio(
    monthly_savings: float,
    start_month: str,
    months: int,
    real: bool = False,
) -> list[float]:
    df = pl.read_csv(DATA_PATH)

    # Rename long column for easier access
    df = df.rename({df.columns[1]: "price"})

    # Find start index
    # Format in CSV is MM/YYYY based on file view
    start_idx_rows = df.with_row_index().filter(pl.col("Date") == start_month).select("index")

    if start_idx_rows.height == 0:
        raise ValueError(f"Start month {start_month} not found in data")

    start_idx = start_idx_rows.item(0, 0)

    # Slice data: need months + 1 rows to calculate months returns?
    # Actually we just need price changes.
    # If we invest at t=0, we buy at price[start_idx].
    # At t=1, value is (savings / price[0]) * price[1] + new_savings?
    # Simplified logic:
    # Portfolio starts at 0.
    # Month 0: Contribute savings. Balance = savings.
    # Month 1: previous balance grows/shrinks, add savings.
    # We need price data for 'months' steps.

    # Verify we have enough data
    if start_idx + months >= df.height:
        raise ValueError(f"Not enough data for {months} months starting from {start_month}")

    subset = df.slice(start_idx, months + 1)
    prices = subset["price"].to_list()

    portfolio_values = [0.0] * (months + 1)

    # Month 0: Invest start savings
    # "takes a monthly_savings (this is what we reinvest every month)"
    # Usually this implies:
    # t=0: Invest monthly_savings.
    # t=1: Invest monthly_savings.
    # ...

    # Let's assume standard annuity due or ordinary annuity?
    # "reinvest every month" -> likely investing the savings at the beginning of the month (or end).
    # Let's assume beginning of period for simplicity or end?
    # Usually: Income comes in, expenses out, savings invest immediately.

    # t=0
    portfolio_values[0] = monthly_savings

    for t in range(1, months + 1):
        price_prev = prices[t - 1]
        price_curr = prices[t]

        nominal_return = price_curr / price_prev

        if real:
            # deflation factor
            step_return = nominal_return / (1 + INFLATION_MONTHLY)
        else:
            step_return = nominal_return

        portfolio_values[t] = portfolio_values[t - 1] * step_return + monthly_savings

    return portfolio_values
