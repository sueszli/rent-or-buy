import polars as pl
from plotnine import aes, element_text, geom_line, geom_text, ggplot, labs, scale_x_date, scale_y_continuous, theme, theme_minimal

from equity import Products, simulate_equity_portfolio
from income import IncomePercentile
from real_estate import simulate_real_estate_portfolio


def plot_comparison(df: pl.DataFrame):
    last_rows = df.group_by("strategy").last()

    (
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
    ).show()


def run_comparison():
    INITIAL_LUMP_SUM = 100_000
    PROPERTY_PRICE = 400_000
    INCOME_PERCENTILE = IncomePercentile.pct_75th
    START_YEAR = 1994
    YEARS = 30

    equity_df = simulate_equity_portfolio(
        monthly_savings=INCOME_PERCENTILE.value,
        years=YEARS,
        start_year=START_YEAR,
        cash_savings=INITIAL_LUMP_SUM,
        product=Products.MSCI_WORLD,
    )
    equity_df = equity_df.with_columns(pl.lit("Equity ETF").alias("strategy"))
    print("\nequity strategy:")
    print(equity_df.head(1))
    print(equity_df.tail(1))

    real_estate_df = simulate_real_estate_portfolio(
        monthly_savings=INCOME_PERCENTILE.value,
        years=YEARS,
        start_year=START_YEAR,
        purchase_price=PROPERTY_PRICE,
        cash_savings=INITIAL_LUMP_SUM,
    )
    real_estate_df = real_estate_df.with_columns(pl.lit("Real Estate").alias("strategy"))
    print("\nreal estate strategy:")
    print(real_estate_df.head(1))
    print(real_estate_df.tail(1))

    combined_df = pl.concat([equity_df, real_estate_df])

    plot_comparison(combined_df)


if __name__ == "__main__":
    run_comparison()
