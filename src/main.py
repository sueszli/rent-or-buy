from datetime import datetime

import plotille
import polars as pl
from plotnine import aes, element_text, geom_line, geom_text, ggplot, labs, scale_x_date, scale_y_continuous, theme, theme_minimal

from equity import Products, simulate_equity_portfolio
from income import IncomePercentile
from real_estate import estimate_mortgage_payoff_years, simulate_real_estate_portfolio


def plot_comparison(df: pl.DataFrame):
    last_rows = df.group_by("strategy").last()

    p = (
        ggplot(df, aes(x="date", y="payout", color="strategy"))
        + geom_line(size=1)
        + geom_text(
            last_rows,
            aes(label="payout"),
            va="bottom",
            ha="right",
            size=10,
            format_string="{:,.0f}€",
            nudge_y=20000,
            show_legend=False,
        )
        + theme_minimal()
        + labs(title="Equity vs Real Estate Portfolio Value Over Time", subtitle="Comparison of two strategies (initial lump sum + monthly savings)", x="Date", y="Net Worth (EUR)", color="Strategy")
        + theme(
            figure_size=(10, 6),
            axis_text_x=element_text(rotation=45, hjust=1),
            plot_title=element_text(size=16, weight="bold"),
            legend_position="bottom",
        )
        + scale_y_continuous(labels=lambda label: [f"{x:,.0f}€" for x in label])
        + scale_x_date(expand=(0.1, 0.1))
    )

    p.save(f"assets/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    p.show()


def plot_comparison_ascii(df: pl.DataFrame):
    fig = plotille.Figure()
    fig.width = 80
    fig.height = 30

    for (name,), data in df.group_by(["strategy"]):
        data = data.sort("date")
        x = data["date"].dt.year() + (data["date"].dt.month() - 1) / 12.0
        y = data["payout"]
        fig.plot(x, y, label=str(name))

    print(fig.show(legend=True))


def run_comparison():
    INITIAL_LUMP_SUM = 130_000
    PROPERTY_PRICE = 500_000
    INCOME = IncomePercentile.pct_75th.value / 12
    START_YEAR = 1994
    YEARS = int(estimate_mortgage_payoff_years(INCOME, INITIAL_LUMP_SUM, PROPERTY_PRICE)) + 10

    equity_df = simulate_equity_portfolio(
        monthly_savings=INCOME,
        years=YEARS,
        start_year=START_YEAR,
        cash_savings=INITIAL_LUMP_SUM,
        product=Products.MSCI_WORLD,
    ).with_columns(pl.lit("Equity ETF").alias("strategy"))
    print("--- equity strategy:")
    print(equity_df.head(1).row(0))
    print(equity_df.tail(1).row(0))

    real_estate_df = simulate_real_estate_portfolio(
        monthly_savings=INCOME,
        years=YEARS,
        start_year=START_YEAR,
        purchase_price=PROPERTY_PRICE,
        cash_savings=INITIAL_LUMP_SUM,
    ).with_columns(pl.lit("Real Estate").alias("strategy"))
    print("--- real estate strategy:")
    print(real_estate_df.head(1).row(0))
    print(real_estate_df.tail(1).row(0))

    df = pl.concat([equity_df, real_estate_df])
    return df


if __name__ == "__main__":
    df = run_comparison()
    plot_comparison_ascii(df)
    plot_comparison(df)
