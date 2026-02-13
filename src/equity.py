import datetime
from enum import Enum
from pathlib import Path

import polars as pl
from dateutil.relativedelta import relativedelta

from .income import rent_adjusted


def _prices_vanguard(months: int, start_month: int, start_year: int) -> list[float]:
    # data also embeds TER
    datapath = Path(__file__).parent.parent / "data" / "all-world.csv"
    assert 1 * 12 <= months <= 20 * 12, f"insufficient data for {months} months"
    assert 1 <= start_month <= 12, f"invalid start month {start_month}"
    assert 2003 <= start_year <= 2024, f"invalid start year {start_year}"

    months = int(months)
    start_month = int(start_month)
    start_year = int(start_year)

    df = pl.read_csv(datapath).with_columns(pl.col("Date").str.to_date("%m/%Y")).select(pl.col("Date"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    prices_df = df.filter(pl.col("Date") >= start_date).head(months)
    prices = prices_df["price"].to_list()
    assert len(prices) == months, f"insufficient price data. expected range {start_date} to {start_date + relativedelta(months=months)}. actual range {prices_df['Date'].min()} to {prices_df['Date'].max()}."
    return prices


def _annual_tax_vanguard(year: int, total_shares: float, current_price: float) -> tuple[float, float, float]:
    oegk_data = {
        2019: (0.4, 0.32, 0.04),
        2020: (0.4, 0.32, 0.04),
        2021: (0.4, 0.32, 0.04),
        2022: (0.65, 0.52, 0.07),
        2023: (0.65, 0.52, 0.07),
        2024: (0.35, 0.28, 0.04),
        2025: (1.5965, 1.2962, 0.1559),
    }

    if year in oegk_data:
        age_rate, step_up_rate, foreign_rate = oegk_data[year]
    else:
        # conservative estimate
        age_rate = current_price * 0.015  # expect 1.5% dividend yield
        step_up_rate = age_rate * 0.81  # prevent double taxation simulation (weighted by historic avg)
        foreign_rate = age_rate * 0.1  # expect 10% of AgE to be creditable foreign tax

    hypothetical_dividends = total_shares * age_rate
    foreign_tax_credit = total_shares * foreign_rate
    cost_basis_adjustment = total_shares * step_up_rate

    return hypothetical_dividends, foreign_tax_credit, cost_basis_adjustment


def _prices_msci(months: int, start_month: int, start_year: int) -> list[float]:
    # data also embeds TER
    datapath = Path(__file__).parent.parent / "data" / "msci-world.csv"
    assert 1 * 12 <= months <= 38 * 12, f"insufficient data for {months} months"
    assert 1 <= start_month <= 12, f"invalid start month {start_month}"
    assert 1987 <= start_year <= 2025, f"invalid start year {start_year}"

    months = int(months)
    start_month = int(start_month)
    start_year = int(start_year)

    df = pl.read_csv(datapath).with_columns(pl.col("Date").str.to_date("%m/%Y")).select(pl.col("Date"), pl.col("^iShares.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    prices_df = df.filter(pl.col("Date") >= start_date).head(months)
    prices = prices_df["price"].to_list()
    assert len(prices) == months, f"insufficient price data. expected range {start_date} to {start_date + relativedelta(months=months)}. actual range {prices_df['Date'].min()} to {prices_df['Date'].max()}."
    return prices


def _annual_tax_msci(year: int, total_shares: float, current_price: float) -> tuple[float, float, float]:
    oegk_data = {
        2017: (0.3094, 0.2059, 0.0367),
        2018: (1.4798, 1.3653, 0.0868),
        2019: (2.3710, 2.2201, 0.0992),
        2020: (1.6108, 1.4773, 0.1012),
        2021: (0.3227, 0.2015, 0.0411),
        2022: (1.4051, 1.3079, 0.0892),
        2023: (1.3425, 1.2032, 0.1223),
        2024: (1.4065, 1.2620, 0.1287),
        2025: (1.4068, 1.2425, 0.1322),
    }

    if year in oegk_data:
        age_rate, step_up_rate, foreign_rate = oegk_data[year]
    else:
        # conservative estimate
        age_rate = current_price * 0.015  # expect 1.5% dividend yield
        step_up_rate = age_rate * 0.88  # prevent double taxation simulation (weighted by historic avg)
        foreign_rate = age_rate * 0.09  # expect 10% of AgE to be creditable foreign tax

    hypothetical_dividends = total_shares * age_rate
    foreign_tax_credit = total_shares * foreign_rate
    cost_basis_adjustment = total_shares * step_up_rate

    return hypothetical_dividends, foreign_tax_credit, cost_basis_adjustment


class Products(Enum):
    # only the most "neutral" equity ETFs that track the entire world

    VANGUARD_ALL_WORLD = (_prices_vanguard, _annual_tax_vanguard)
    """
    Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)

    - https://curvo.eu/backtest/en
    - https://my.oekb.at/kapitalmarkt-services/kms-output/fonds-info/sd/af/f?isin=IE00BK5BQT80 (missing lots of data)
    - https://www.justetf.com/en/etf-profile.html?isin=IE00BK5BQT80
    - https://www.flatex.de/fileadmin/dateien_flatex/pdf/handel/gesamtliste_premium_etfs_de.pdf (no fees on flatex)
    """

    MSCI_WORLD = (_prices_msci, _annual_tax_msci)
    """
    iShares MSCI ACWI UCITS ETF (Acc) (IE00B6R52259)

    - https://curvo.eu/backtest/en
    - https://my.oekb.at/kapitalmarkt-services/kms-output/fonds-info/sd/af/f?isin=IE00B6R52259
    """


def simulate_equity_portfolio(
    monthly_savings: float,
    years: int,
    start_month: int,
    start_year: int,
    product: Products = Products.MSCI_WORLD,
) -> pl.DataFrame:
    SPREAD_HALF = 0.0012 / 2  # 0.06% spread cost each way
    KEST = 0.275  # kapital ertragssteuer

    def _buy_price(price: float) -> float:
        return price * (1 + SPREAD_HALF)

    def _sell_price(price: float) -> float:
        return price * (1 - SPREAD_HALF)

    _prices, _annual_tax = product.value

    months = years * 12
    prices = _prices(months, start_month, start_year)

    total_shares = 0.0
    safe_from_tax = 0.0

    start_date = datetime.date(start_year, start_month, 1)
    dates = [start_date + relativedelta(months=i) for i in range(len(prices))]

    payout_history = []

    for price, current_date in zip(prices, dates):
        # deduct rent
        monthly_savings -= rent_adjusted(current_date.year)

        # buy shares
        total_shares += monthly_savings / _buy_price(price)
        safe_from_tax += monthly_savings

        # annual tax event in january
        if current_date.month == 1:
            tax_year = current_date.year - 1
            hypothetical_dividends, foreign_tax_refund, national_tax_refund = _annual_tax(tax_year, total_shares, price)

            # sell shares to pay tax. models opportunity cost
            tax_due = max(0.0, hypothetical_dividends * KEST - foreign_tax_refund)

            safe_from_tax += national_tax_refund

            if tax_due > 0 and total_shares > 0:
                shares_to_sell = tax_due / _sell_price(price)  # don't deduct KESt for simplicity
                safe_from_tax *= 1.0 - (shares_to_sell / total_shares)
                total_shares -= shares_to_sell

        # how much if we would liquidate today?
        gross_value = total_shares * _sell_price(price)
        taxable_value = gross_value - safe_from_tax
        exit_tax = taxable_value * KEST if taxable_value > 0 else 0.0

        payout = gross_value - exit_tax
        payout_history.append(payout)

    return pl.DataFrame({"date": dates, "payout": payout_history})
