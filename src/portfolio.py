import datetime
import pathlib

import polars as pl
from dateutil.relativedelta import relativedelta

# product: Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)
#
# - equity ETF that tracks the entire world stock market.
# - most "neutral" portfolio possible. dilutes US exposure.
# - must invest at least 10 years to pay off

# based on:
# - https://curvo.eu/backtest/en
# - https://my.oekb.at/kapitalmarkt-services/kms-output/fonds-info/sd/af/f?isin=IE00BK5BQT80 (missing lots of data)
# - https://www.justetf.com/en/etf-profile.html?isin=IE00BK5BQT80
# - https://www.flatex.de/fileadmin/dateien_flatex/pdf/handel/gesamtliste_premium_etfs_de.pdf

SPREAD_HALF = 0.0012 / 2  # 0.06% spread cost each way
TRANSACTION_FEE = 0.0  # flatex premium
KEST = 0.275  # kapital ertragssteuer


def _buy_price(price: float) -> float:
    return price * (1 + SPREAD_HALF)


def _sell_price(price: float) -> float:
    return price * (1 - SPREAD_HALF)


def _annual_tax_data(year: int, current_price: float) -> tuple[float, float, float]:
    # estimated year to (AgE, Korrektur, foreign) per share in EUR
    estimated_age_rate = 0.01
    estimated_korrektur_factor = 0.8
    estimated_foreign_factor = 0.1

    annual_tax_data = {
        2019: (0.4, 0.32, 0.04),
        2020: (0.4, 0.32, 0.04),
        2021: (0.4, 0.32, 0.04),
        2022: (0.65, 0.52, 0.07),
        2023: (0.65, 0.52, 0.07),
        2024: (0.35, 0.28, 0.04),
        2025: (1.5965, 1.2962, 0.1559),
    }

    if year in annual_tax_data:
        return annual_tax_data[year]

    age = estimated_age_rate * current_price
    korrektur = estimated_korrektur_factor * age
    foreign = estimated_foreign_factor * age
    return age, korrektur, foreign


def _prices(start_year: int, start_month: int, months: int) -> list[float]:
    # data also embeds TER
    datapath = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

    assert 1 <= start_month <= 12
    assert 2003 <= start_year <= 2024
    df = pl.read_csv(datapath).with_columns(pl.col("Date").str.to_date("%m/%Y")).select(pl.col("Date"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    prices_df = df.filter(pl.col("Date") >= start_date).head(months)
    prices = prices_df["price"].to_list()
    assert len(prices) == months, "insufficient price data"
    return prices


def simulate_austrian_portfolio(
    monthly_savings: float,
    start_year: int,
    start_month: int,
    months: int,
) -> list[float]:
    monthly_savings -= TRANSACTION_FEE

    prices = _prices(start_year, start_month, months)

    total_shares = 0.0

    paid_tax = 0.0
    safe_from_tax = 0.0

    cash_in_hand_history = []
    current_date = datetime.date(start_year, start_month, 1)

    for price in prices:
        total_shares += monthly_savings / _buy_price(price)
        safe_from_tax += monthly_savings

        # advance time
        current_date += relativedelta(months=1)

        # annual tax event in january
        if current_date.month == 1:
            tax_year = current_date.year - 1
            age, korrektur, foreign = _annual_tax_data(tax_year, price)

            hypothetical_dividends = total_shares * age
            foreign_tax_refund = total_shares * foreign
            national_tax_refund = total_shares * korrektur

            paid_tax += max(0.0, hypothetical_dividends * KEST - foreign_tax_refund)
            safe_from_tax += national_tax_refund

        # assume we would liquidate today
        gross_value = total_shares * _sell_price(price)
        profit = gross_value - safe_from_tax
        exit_tax = profit * KEST if profit > 0 else 0.0
        net_cash_in_hand = gross_value - exit_tax - paid_tax
        cash_in_hand_history.append(net_cash_in_hand)

    return cash_in_hand_history


results = simulate_austrian_portfolio(monthly_savings=2000, start_year=2020, start_month=1, months=4)
print(results)
