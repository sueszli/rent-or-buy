import polars as pl
from plotnine import aes, element_text, geom_line, geom_text, ggplot, labs, scale_x_date, scale_y_continuous, theme, theme_minimal


def plot_equity_portfolio(df: pl.DataFrame):
    first_row = df.head(1)
    last_row = df.tail(1)
    (
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
            subtitle="Excluding tax and costs",
            x="Date",
            y="Cash in Hand (EUR)",
        )
        + theme(
            figure_size=(10, 6),
            axis_text_x=element_text(rotation=45, hjust=1),
            plot_title=element_text(size=16, weight="bold"),
        )
        + scale_y_continuous(labels=lambda label: [f"{x:,.0f}€" for x in label])
        + scale_x_date(expand=(0.1, 0.1))
    ).show()
