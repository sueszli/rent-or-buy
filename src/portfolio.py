import datetime
import pathlib

import polars as pl
from dateutil.relativedelta import relativedelta
from plotnine import aes, element_text, geom_line, geom_text, ggplot, labs, scale_x_date, scale_y_continuous, theme, theme_minimal

# product: Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)
#
# - equity ETF that tracks the entire world stock market.
# - most "neutral" portfolio possible. dilutes US exposure.
# - must invest at least 10 years to pay off

# based on:
# - https://curvo.eu/backtest/en
# - https://my.oekb.at/kapitalmarkt-services/kms-output/fonds-info/sd/af/f?isin=IE00BK5BQT80 (missing lots of data)
# - https://www.justetf.com/en/etf-profile.html?isin=IE00BK5BQT80
# - https://www.flatex.de/fileadmin/dateien_flatex/pdf/handel/gesamtliste_premium_etfs_de.pdf (no transaction fees, custody fees for flatex premium etfs)

SPREAD_HALF = 0.0012 / 2  # 0.06% spread cost each way
KEST = 0.275  # kapital ertragssteuer


def _buy_price(price: float) -> float:
    return price * (1 + SPREAD_HALF)


def _sell_price(price: float) -> float:
    return price * (1 - SPREAD_HALF)


def _prices(months: int, start_year: int, start_month: int) -> list[float]:
    # data also embeds TER
    datapath = pathlib.Path(__file__).parent.parent / "data" / "vwce-chart.csv"
    assert 1 * 12 <= months <= 20 * 12  # not much data available

    assert 1 <= start_month <= 12
    assert 2003 <= start_year <= 2024
    df = pl.read_csv(datapath).with_columns(pl.col("Date").str.to_date("%m/%Y")).select(pl.col("Date"), pl.col("^Vanguard.*$").alias("price")).sort("Date")
    start_date = datetime.date(start_year, start_month, 1)
    prices_df = df.filter(pl.col("Date") >= start_date).head(months)
    prices = prices_df["price"].to_list()
    assert len(prices) == months, f"insufficient price data. expected range {start_date} to {start_date + relativedelta(months=months)}. actual range {prices_df['Date'].min()} to {prices_df['Date'].max()}."
    return prices


def _annual_tax(year: int, total_shares: float, current_price: float) -> tuple[float, float, float]:
    # estimated year to (AgE, Korrektur, foreign) per share in EUR
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
        age_rate = current_price * 0.015 # expect 1.5% dividend yield
        step_up_rate = age_rate * 0.81  # prevent double taxation simulation (weighted by historic avg)
        foreign_rate = age_rate * 0.1  # expect 10% of AgE to be creditable foreign tax

    hypothetical_dividends = total_shares * age_rate
    foreign_tax_credit = total_shares * foreign_rate
    cost_basis_adjustment = total_shares * step_up_rate

    return hypothetical_dividends, foreign_tax_credit, cost_basis_adjustment


def simulate_portfolio(monthly_savings: float, years: int = 20, start_month: int = 1, start_year: int = 2004) -> pl.DataFrame:
    months = years * 12
    prices = _prices(months, start_month, start_year)

    total_shares = 0.0
    safe_from_tax = 0.0

    payout_history = []
    dates = []
    current_date = datetime.date(start_year, start_month, 1)

    for price in prices:
        # buy shares
        total_shares += monthly_savings / _buy_price(price)
        safe_from_tax += monthly_savings

        # advance time
        dates.append(current_date)
        current_date += relativedelta(months=1)

        # annual tax event in january
        if current_date.month == 1:
            tax_year = current_date.year - 1
            hypothetical_dividends, foreign_tax_refund, national_tax_refund = _annual_tax(tax_year, total_shares, price)

            # sell shares to pay tax. models opportunity cost
            tax_due = max(0.0, hypothetical_dividends * KEST - foreign_tax_refund)

            safe_from_tax += national_tax_refund

            if tax_due > 0 and total_shares > 0:
                shares_to_sell = tax_due / _sell_price(price)
                safe_from_tax *= 1.0 - (shares_to_sell / total_shares)
                total_shares -= shares_to_sell

        # how much if we would liquidate today?
        gross_value = total_shares * _sell_price(price)
        taxable_value = gross_value - safe_from_tax
        exit_tax = taxable_value * KEST if taxable_value > 0 else 0.0

        payout = gross_value - exit_tax
        payout_history.append(payout)

    return pl.DataFrame({"date": dates, "payout": payout_history})


def plot_portfolio(df: pl.DataFrame):
    first_row = df.head(1)
    last_row = df.tail(1)

    p = (
        ggplot(df, aes(x="date", y="payout"))
        + geom_line(color="#2c3e50", size=1)
        + geom_text(
            first_row,
            aes(label="payout"),
            va="bottom",
            ha="center",
            size=10,
            format_string="{:,.0f}€",
            nudge_y=20000,
        )
        + geom_text(
            last_row,
            aes(label="payout"),
            va="bottom",
            ha="center",
            size=10,
            format_string="{:,.0f}€",
            nudge_y=20000,
        )
        + theme_minimal()
        + labs(
            title="FTSE All-World Portfolio Value Over Time",
            subtitle="Excluding capital gains tax and transaction costs",
            x="Date",
            y="Net Cash in Hand (EUR)",
        )
        + theme(
            figure_size=(10, 6),
            axis_text_x=element_text(rotation=45, hjust=1),
            plot_title=element_text(size=16, weight="bold"),
        )
        + scale_y_continuous(labels=lambda label: [f"{x:,.0f}€" for x in label])
        + scale_x_date(expand=(0.1, 0.1))
    )
    p.show()


plot_portfolio(simulate_portfolio(monthly_savings=1000.0, years=20, start_year=2004, start_month=1))
