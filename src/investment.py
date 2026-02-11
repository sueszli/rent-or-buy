def rent_monthly(t: int, starting_rent: float, annual_rent_growth: float) -> float:
    return starting_rent * (1 + annual_rent_growth) ** (t / 12)


def simulate_rent_strategy(
    months: int,
    starting_cash: float,
    monthly_savings: float,
    starting_rent: float,
    annual_rent_growth: float,
    annual_return: float,
) -> tuple[list[float], list[float]]:
    monthly_return = annual_return / 12

    portfolio = [0.0] * (months + 1)
    contributions = [0.0] * (months + 1)
    portfolio[0] = starting_cash
    contributions[0] = starting_cash

    for t in range(1, months + 1):
        rent = rent_monthly(t, starting_rent, annual_rent_growth)
        contribution = monthly_savings - rent
        portfolio[t] = portfolio[t - 1] * (1 + monthly_return) + contribution
        contributions[t] = contributions[t - 1] + contribution

    return portfolio, contributions
