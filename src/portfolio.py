import pathlib

import deal
import polars as pl

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"
TAX_RATE = 0.275  # kapital ertragsteuer KESt
AG_E_YIELD = 0.0  # Annual yield of "Ausschüttungsgleiche Erträge" (AgE)


@deal.pre(lambda start_month, **_: 1 <= start_month <= 12)
@deal.pre(lambda start_year, **_: 1900 <= start_year <= 2100)
@deal.pre(lambda months, **_: 0 <= months <= 1200)
@deal.pre(lambda monthly_savings, **_: 0 <= monthly_savings <= 1e9)
@deal.ensure(lambda months, result, **_: len(result) == months + 1)
def simulate_portfolio(
    monthly_savings: float,
    start_year: int,
    start_month: int,
    months: int,
    initial_investment: float = 0.0,
) -> list[float]:
    df = pl.read_csv(DATA_PATH).select(pl.col("Date"), pl.col("^Vanguard.*$").alias("price"))
    start_idx = df.select(pl.arg_where(pl.col("Date") == f"{start_month:02d}/{start_year}")).item(0, 0)
    prices = df.slice(start_idx, months + 1)["price"].to_list()
    assert len(prices) == months + 1

    portfolio_values = [0.0] * (months + 1)
    cost_basis = [0.0] * (months + 1)

    # t=0: Initial State
    # We invest the initial lump sum immediately.
    portfolio_values[0] = initial_investment
    cost_basis[0] = initial_investment

    # t=1 to t=months: Monthly Steps
    # Simulation runs in NOMINAL terms to correctly apply tax logic
    for t in range(1, months + 1):
        price_prev = prices[t - 1]
        price_curr = prices[t]

        # 1. Calculate Nominal Market Return
        nominal_return = price_curr / price_prev

        # 2. Simulate Tax Drag (AgE)
        # Yield is provided as an annual figure, so we smooth it over 12 months.
        # ag_e_gross: The theoretical dividend amount accumulated this month.
        ag_e_gross = portfolio_values[t - 1] * (AG_E_YIELD / 12)

        # ag_e_tax: The actual tax bill the investor must pay.
        ag_e_tax = ag_e_gross * TAX_RATE

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
    return [val - max(0.0, val - basis) * TAX_RATE for val, basis in zip(portfolio_values, cost_basis)]
