import datetime
import pathlib

import polars as pl

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"

# dividends
# - https://my.oekb.at/kapitalmarkt-services/kms-output/fonds-info/sd/af/f?isin=IE00BK5BQT80
MONTHLY_YIELD = 0.015 / 12  # tax on dividends, even if reinvested (ausschüttungsgleiche erträge, AgE)

# costs
# - https://www.justetf.com/en/etf-profile.html?isin=IE00BK5BQT80
# - https://www.flatex.de/fileadmin/dateien_flatex/pdf/handel/gesamtliste_premium_etfs_de.pdf
TRANSACTION_FEE = 0.0  # per trade. premium etf
SPREAD_HALF = 0.0012 / 2
KEST = 0.275  # tax on gains. (kapital ertragsteuer)


def _buy_price(price: float) -> float:
    return price * (1 + SPREAD_HALF)


def _sell_price(price: float) -> float:
    return price * (1 - SPREAD_HALF)


def _prices(start_year: int, start_month: int, months: int) -> list[float]:
    assert 1 <= start_month <= 12
    assert 2003 <= start_year <= 2024
    df = pl.read_csv(DATA_PATH).select(pl.col("Date").str.to_date("%m/%Y"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    baseline_date = (start_date - datetime.timedelta(days=1)).replace(day=1)  # to access prices[t-1] later
    prices_df = df.filter(pl.col("Date") >= baseline_date).head(months + 1)
    prices = prices_df["price"].to_list()
    assert len(prices) == months + 1, "insufficient price data"


def simulate_portfolio(
    monthly_savings: float,
    start_year: int,
    start_month: int,
    months: int,
) -> list[float]:
    prices = _prices(start_year, start_month, months)

    total_shares = 0.0
    tax_basis = 0.0
    cash_in_hand_history = []

    for t in range(1, months + 1):
        # price_prev = prices[t - 1]
        price_curr = prices[t]
        # returns = price_curr / price_prev

        total_shares += monthly_savings / _buy_price(price_curr)

        # AgE smoothed over months
        current_market_value = total_shares * price_curr
        monthly_age = current_market_value * MONTHLY_YIELD
        tax_basis += monthly_savings + monthly_age

        # hypothetical sell
        gross_value = total_shares * _sell_price(price_curr)
        profit = gross_value - tax_basis
        exit_tax = profit * KEST if profit > 0 else 0.0
        net_cash = gross_value - exit_tax
        cash_in_hand_history.append(net_cash)

    return cash_in_hand_history


r = simulate_portfolio(monthly_savings=2000, start_year=2020, start_month=1, months=4)
print(r)
