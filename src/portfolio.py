import pathlib
import re
from dataclasses import dataclass

import deal
import polars as pl

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"


ANNUAL_INFLATION = 1.0254


@dataclass
class PortfolioResult:
    values: list[float]  # values at each time step t
    cost_basis: list[float]  # incurred costs at each time step t, adjusted for tax drag (AgE)


@deal.pre(lambda start_month, **_: bool(re.match(r"^\d{2}/\d{4}$", start_month)))
@deal.pre(lambda months, **_: 0 <= months <= 1200)
@deal.pre(lambda monthly_savings, **_: 0 <= monthly_savings <= 1e9)
@deal.ensure(lambda months, result, **_: len(result.values) == months + 1)
def simulate_portfolio(
    monthly_savings: float,
    start_month: str,
    months: int,
    initial_balance: float = 0.0,
    ag_e_yield: float = 0.0,
    tax_rate: float = 0.275,
    real: bool = False,
) -> PortfolioResult:
    """
    Product: Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)
    Equity ETF that tracks the entire world stock market.

    Key Considerations:
        - KESt (Kapitalertragssteuer): 27.5% on capital gains
        - AgE (Ausschüttungsgleiche Erträge): on dividends they *would* have distributed.
        This tax is deducted from the investor's cash account (not the fund value directly),
        creating a "tax drag" on liquidity. To prevent double taxation, the acquisition cost (basis)
        is stepped up by the specific amount of the AgE.

    Args:
        monthly_savings: Amount saved and invested at the *end* of each month.
        start_month: Start date in "MM/YYYY" format.
        months: Duration of simulation in months.
        initial_balance: Lump sum invested at t=0 (e.g., capital that would otherwise be a down payment).
        ag_e_yield: Annual yield of "Ausschüttungsgleiche Erträge" (AgE) as a decimal (e.g. 0.015 for 1.5%).
                    Used to simulate the annual tax drag on cash flows.
        tax_rate: Austrian Capital Gains Tax rate (KESt), typically 27.5%.
        real: If True, the output values are deflated to the start date (t=0) using 2% annual inflation.
              NOTE: The simulation calculates taxes on NOMINAL gains (as per Austrian law) and deflates AFTER.
              Using `real=True` hides the nominal cost basis, so be careful when calculating final capital gains tax!
              For accurate tax calculation, use `real=False`, calculate tax, then deflate.

    Returns:
        PortfolioResult containing market values and cost basis for each month.
    """
    df = pl.read_csv(DATA_PATH)
    df = df.rename({df.columns[1]: "price"})

    # Find the row index corresponding to the start month
    start_idx_rows = df.with_row_index().filter(pl.col("Date") == start_month).select("index")
    assert start_idx_rows.height != 0

    start_idx = start_idx_rows.item(0, 0)
    assert start_idx + months < df.height

    # Slice the data for the simulation period [t=0 to t=months]
    subset = df.slice(start_idx, months + 1)
    prices = subset["price"].to_list()

    portfolio_values = [0.0] * (months + 1)
    cost_basis = [0.0] * (months + 1)

    # t=0: Initial State
    # We invest the initial lump sum immediately.
    portfolio_values[0] = initial_balance
    cost_basis[0] = initial_balance

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
        ag_e_gross = portfolio_values[t - 1] * (ag_e_yield / 12)

        # ag_e_tax: The actual tax bill the investor must pay.
        ag_e_tax = ag_e_gross * tax_rate

        # 3. Determine Net Investment
        # Investor aims to save `monthly_savings`, but must first pay the tax bill.
        net_investment = monthly_savings - ag_e_tax

        # 4. Update Portfolio Value
        # Current Value = (Previous Value * Return) + Net New Investment
        portfolio_values[t] = portfolio_values[t - 1] * nominal_return + net_investment

        # 5. Update Cost Basis
        # The basis increases by net investment AND the gross AgE amount.
        cost_basis[t] = cost_basis[t - 1] + net_investment + ag_e_gross

    # Post-Processing: Deflation
    if real:
        deflators = [(1 + ((ANNUAL_INFLATION) ** (1 / 12) - 1)) ** t for t in range(months + 1)]
        portfolio_values = [v / d for v, d in zip(portfolio_values, deflators)]
        cost_basis = [b / d for b, d in zip(cost_basis, deflators)]

    return PortfolioResult(values=portfolio_values, cost_basis=cost_basis)
