import datetime
import pathlib

import polars as pl

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

# costs
TRANSACTION_FEE = 0.0  # per trade. premium etf. see: https://www.flatex.de/fileadmin/dateien_flatex/pdf/handel/gesamtliste_premium_etfs_de.pdf
SPREAD = 1.0005  # per trade (this is for buying. for selling, subtract from 1)
TER = 0.0019  # annually. see: https://www.justetf.com/en/etf-profile.html?isin=IE00B3RBWM25

# tax
KEST = 0.275  # monthly. on gains. (kapital ertragsteuer)
AGE_YIELD = 0.0  # annual (jan/feb). on dividends. (ausschüttungsgleiche erträge)


def simulate_portfolio(
    monthly_savings: float,
    start_year: int,
    start_month: int,
    months: int,
    initial_investment: float = 0.0,
) -> list[float]:
    assert 1 <= start_month <= 12
    assert 1900 <= start_year <= 2100
    assert 0 <= months <= 1200
    assert 0 <= monthly_savings <= 1e9

    df = pl.read_csv(DATA_PATH).select(pl.col("Date").str.to_date("%m/%Y"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    baseline_date = (start_date - datetime.timedelta(days=1)).replace(day=1)  # to access prices[t-1] later
    prices_df = df.filter(pl.col("Date") >= baseline_date).head(months + 1)
    prices = prices_df["price"].to_list()
    assert len(prices) == months + 1, "insufficient price data"

    portfolio_values = [initial_investment] + ([0.0] * months)
    cost_basis = [initial_investment] + ([0.0] * months)  # also includes dividends that have been reinvested (ag_e_gross)

    for t in range(1, months + 1):
        price_prev = prices[t - 1]
        price_curr = prices[t]

        # 1. Calculate Nominal Market Return
        nominal_return = price_curr / price_prev

        # 2. Simulate Tax Drag (AgE)
        # Yield is provided as an annual figure, so we smooth it over 12 months.
        # ag_e_gross: The theoretical dividend amount accumulated this month.
        ag_e_gross = portfolio_values[t - 1] * (AGE_YIELD / 12)

        # ag_e_tax: The actual tax bill the investor must pay.
        ag_e_tax = ag_e_gross * KEST

        # 3. Determine Net Investment
        # Investor aims to save `monthly_savings`, but must first pay the tax bill.
        net_investment = monthly_savings - ag_e_tax

        # 4. Update Portfolio Value
        # Current Value = (Previous Value * Return) + Net New Investment
        portfolio_values[t] = portfolio_values[t - 1] * nominal_return + net_investment

        # 5. Update Cost Basis
        # The basis increases by net investment AND the gross AgE amount.
        cost_basis[t] = cost_basis[t - 1] + net_investment + ag_e_gross

    # Calculate net value (after hypothetical liquidation tax)
    # This represents the "cash in hand" value if the portfolio were sold at time t.
    result = [val - max(0.0, val - basis) * KEST for val, basis in zip(portfolio_values, cost_basis)]
    assert len(result) == months + 1
    return result


if __name__ == "__main__":
    r = simulate_portfolio(monthly_savings=1000, start_year=2020, start_month=1, months=4)
    print(r)
