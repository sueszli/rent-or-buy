import polars as pl
from plotnine import aes, element_text, geom_line, geom_text, ggplot, labs, scale_x_date, scale_y_continuous, theme, theme_minimal

from equity import Products, simulate_equity_portfolio
from income import IncomePercentile
from real_estate import estimate_mortgage_payoff_years, simulate_real_estate_portfolio


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
    print(equity_df.head(1))
    print(equity_df.tail(1))

    real_estate_df = simulate_real_estate_portfolio(
        monthly_savings=INCOME,
        years=YEARS,
        start_year=START_YEAR,
        purchase_price=PROPERTY_PRICE,
        cash_savings=INITIAL_LUMP_SUM,
    ).with_columns(pl.lit("Real Estate").alias("strategy"))
    print("--- real estate strategy:")
    print(real_estate_df.head(1))
    print(real_estate_df.tail(1))

    plot_comparison(pl.concat([equity_df, real_estate_df]))


if __name__ == "__main__":
    run_comparison()
