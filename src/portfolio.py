import deal

"""
Vanguard FTSE All-World UCITS ETF (USD) Accumulating (IE00BK5BQT80)

- data from curvo.eu/backtest/
- most "neutral" portfolio possible. dilutes US exposure slightly.
- must invest at least 10 years
- 
"""


@deal.pure
@deal.pre(lambda months, **_: 0 <= months <= 1200)
@deal.pre(lambda starting_cash, **_: 0 <= starting_cash <= 1e9)
@deal.pre(lambda annual_return, **_: -1 < annual_return <= 2.0)
@deal.ensure(lambda months, result, **_: len(result[0]) == len(result[1]) == months + 1)
@deal.ensure(lambda starting_cash, result, **_: result[0][0] == starting_cash and result[1][0] == starting_cash)
def simulate_portfolio(months: int, starting_cash: float, monthly_contribution: float, annual_return: float) -> tuple[list[float], list[float]]:
    monthly_return = annual_return / 12

    portfolio = [0.0] * (months + 1)
    contributions = [0.0] * (months + 1)
    portfolio[0] = starting_cash
    contributions[0] = starting_cash

    for t in range(1, months + 1):
        portfolio[t] = portfolio[t - 1] * (1 + monthly_return) + monthly_contribution
        contributions[t] = contributions[t - 1] + monthly_contribution

    return portfolio, contributions
