import datetime
import pathlib

import polars as pl

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

# estimated year to (AgE, Korrektur, foreign) per share in EUR
ESTIMATED_AGE_RATE = 0.01
ESTIMATED_KORREKTUR_FACTOR = 0.8
ESTIMATED_FOREIGN_FACTOR = 0.1
ANNUAL_TAX_DATA = {
    2019: (0.4, 0.32, 0.04),
    2020: (0.4, 0.32, 0.04),
    2021: (0.4, 0.32, 0.04),
    2022: (0.65, 0.52, 0.07),
    2023: (0.65, 0.52, 0.07),
    2024: (0.35, 0.28, 0.04),
    2025: (1.5965, 1.2962, 0.1559),
}


def _buy_price(price: float) -> float:
    return price * (1 + SPREAD_HALF)


def _sell_price(price: float) -> float:
    return price * (1 - SPREAD_HALF)


def _prices(start_year: int, start_month: int, months: int) -> list[float]:
    # data also embeds TER
    datapath = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

    assert 1 <= start_month <= 12
    assert 2003 <= start_year <= 2024
    df = pl.read_csv(datapath).select(pl.col("Date").str.to_date("%m/%Y"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    baseline_date = (start_date - datetime.timedelta(days=1)).replace(day=1)
    prices_df = df.filter(pl.col("Date") >= baseline_date).head(months + 1)
    prices = prices_df["price"].to_list()
    assert len(prices) == months + 1, "insufficient price data"
    return prices


def simulate_austrian_portfolio(
    monthly_savings: float,
    start_year: int,
    start_month: int,
    months: int,
) -> list[dict]:
    prices = _prices(start_year, start_month, months)

    total_shares = 0.0
    tax_basis = 0.0
    cumulative_tax_paid = 0.0
    cash_in_hand_history = []

    current_date = datetime.date(start_year, start_month, 1)
    for t in range(1, months + 1):
        price_curr = prices[t]

        total_shares += monthly_savings / _buy_price(price_curr)
        tax_basis += monthly_savings

        # approximate next month
        current_date += datetime.timedelta(days=31)
        current_date = current_date.replace(day=1)

        # annual tax
        if current_date.month == 1:
            year = current_date.year - 1
            if year in ANNUAL_TAX_DATA:
                age, korrektur, foreign = ANNUAL_TAX_DATA[year]
            else:
                # conservative estimate based on year-end price
                age = ESTIMATED_AGE_RATE * price_curr
                korrektur = ESTIMATED_KORREKTUR_FACTOR * age
                foreign = ESTIMATED_FOREIGN_FACTOR * age

            # apply per share held
            total_age = age * total_shares
            total_foreign = foreign * total_shares
            net_kest = max(0, total_age * KEST - total_foreign)
            cumulative_tax_paid += net_kest
            tax_basis += korrektur * total_shares

        # hypothetical sell
        gross_value = total_shares * _sell_price(price_curr)
        profit = gross_value - tax_basis
        exit_tax = profit * KEST if profit > 0 else 0.0
        net_cash = gross_value - exit_tax - cumulative_tax_paid
        cash_in_hand_history.append(net_cash)

    return cash_in_hand_history


results = simulate_austrian_portfolio(monthly_savings=2000, start_year=2020, start_month=1, months=4)
print(results)
