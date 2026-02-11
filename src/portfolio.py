import pathlib
import re
from dataclasses import dataclass

import deal
import polars as pl

"""
Portfolio Simulation Module

This module simulates the performance of a global equity portfolio under Austrian tax law.
It is designed to compare "Rent and Invest" vs "Buy" scenarios.

Asset Class:
    Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)
    - Data source: curvo.eu/backtest/
    - Strategy: Buy and hold, accumulating dividends.

Key Considerations:
    - Austrian Tax (KESt): 27.5% on capital gains.
    - AgE (Ausschüttungsgleiche Erträge): "Deemed distributed income".
      In Austria, accumulating funds are taxed annually on the dividends they *would* have distributed.
      This tax is deducted from the investor's cash account (not the fund value directly),
      creating a "tax drag" on liquidity. To prevent double taxation, the acquisition cost (basis)
      is stepped up by the specific amount of the AgE.
"""

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

# Approx historical inflation 2%
# Used to adjust nominal returns to real returns if requested.
INFLATION_MONTHLY = (1.02) ** (1 / 12) - 1


@dataclass
class PortfolioResult:
    """
    Result of the portfolio simulation.

    Attributes:
        values: List of portfolio market values at each time step t.
        cost_basis: List of tax-adjusted acquisition costs at each time step t.
                    This is crucial for calculating the final capital gains tax.
                    Capital Gain = Value - Cost Basis.
    """

    values: list[float]
    cost_basis: list[float]


@deal.pre(lambda monthly_savings, start_month, months, **kwargs: bool(re.match(r"^\d{2}/\d{4}$", start_month)))
@deal.pre(lambda monthly_savings, start_month, months, **kwargs: 0 <= months <= 1200)
@deal.pre(lambda monthly_savings, start_month, months, **kwargs: 0 <= monthly_savings <= 1e9)
@deal.ensure(lambda monthly_savings, start_month, months, **kwargs: len(kwargs["result"].values) == months + 1)
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
    Simulates a monthly investment plan into the FTSE All-World ETF.

    Args:
        monthly_savings: Amount saved and invested at the *end* of each month.
        start_month: Start date in "MM/YYYY" format.
        months: Duration of simulation in months.
        initial_balance: Lump sum invested at t=0 (e.g., capital that would otherwise be a down payment).
        ag_e_yield: Annual yield of "Ausschüttungsgleiche Erträge" (AgE) as a decimal (e.g. 0.015 for 1.5%).
                    Used to simulate the annual tax drag on cash flows.
        tax_rate: Austrian Capital Gains Tax rate (KESt), typically 27.5%.
        real: If True, returns are adjusted for inflation (2% annual).

    Returns:
        PortfolioResult containing market values and tax basis for each month.
    """
    df = pl.read_csv(DATA_PATH)

    # Price data column is the second column
    df = df.rename({df.columns[1]: "price"})

    # Find the row index corresponding to the start month
    start_idx_rows = df.with_row_index().filter(pl.col("Date") == start_month).select("index")

    if start_idx_rows.height == 0:
        raise ValueError(f"Start month {start_month} not found in data")

    start_idx = start_idx_rows.item(0, 0)

    # Ensure sufficient data exists for the requested simulation horizon
    if start_idx + months >= df.height:
        raise ValueError(f"Not enough data for {months} months starting from {start_month}")

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
    for t in range(1, months + 1):
        price_prev = prices[t - 1]
        price_curr = prices[t]

        # 1. Calculate Market Return
        nominal_return = price_curr / price_prev

        if real:
            step_return = nominal_return / (1 + INFLATION_MONTHLY)
        else:
            step_return = nominal_return

        # 2. Simulate Tax Drag (AgE)
        # Yield is provided as an annual figure, so we smooth it over 12 months.
        # ag_e_gross: The theoretical dividend amount accumulated this month.
        ag_e_gross = portfolio_values[t - 1] * (ag_e_yield / 12)

        # ag_e_tax: The actual tax bill the investor must pay.
        # In Austria, this is deducted from the broker's cash account.
        ag_e_tax = ag_e_gross * tax_rate

        # 3. Determine Net Investment
        # The investor aims to save `monthly_savings`, but must first pay the tax bill.
        # The remaining amount is what actually flows into the ETF.
        # Assumption: monthly_savings > ag_e_tax. If not, we'd have negative investment (selling).
        net_investment = monthly_savings - ag_e_tax

        # 4. Update Portfolio Value
        # Current Value = (Previous Value * Return) + Net New Investment
        portfolio_values[t] = portfolio_values[t - 1] * step_return + net_investment

        # 5. Update Cost Basis
        # The basis increases by:
        #   a) The net new money we put in (`net_investment`)
        #   b) The gross AgE amount (`ag_e_gross`)
        #      Why (b)? Because we paid tax on it! Adding it to the basis prevents
        #      paying tax on it again when we eventually sell.
        cost_basis[t] = cost_basis[t - 1] + net_investment + ag_e_gross

    return PortfolioResult(values=portfolio_values, cost_basis=cost_basis)
