import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from investment import rent_monthly, simulate_rent_strategy


def test_rent_monthly_at_t0():
    assert rent_monthly(0, 800, 0.03) == 800


def test_rent_monthly_at_t12():
    result = rent_monthly(12, 800, 0.03)
    expected = 800 * 1.03
    assert abs(result - expected) < 1e-9


def test_simulation_12_months():
    # hand calculation: C_0=100000, savings=3000/mo, rent=800/mo, r=0.07
    monthly_return = 0.07 / 12
    starting_cash = 100_000.0
    savings = 3_000.0
    rent = 800.0
    contribution = savings - rent  # 2200

    # compute expected values month by month
    expected_portfolio = starting_cash
    expected_contributions = starting_cash
    for t in range(1, 13):
        expected_portfolio = expected_portfolio * (1 + monthly_return) + contribution
        expected_contributions += contribution

    portfolio, contributions = simulate_rent_strategy(
        months=12,
        starting_cash=starting_cash,
        monthly_savings=savings,
        starting_rent=rent,
        annual_rent_growth=0.0,  # no growth for clean hand-calc
        annual_return=0.07,
    )

    assert abs(portfolio[12] - expected_portfolio) < 0.01
    assert abs(contributions[12] - expected_contributions) < 0.01

    # sanity: contributions = 100000 + 12 * 2200 = 126400
    assert abs(contributions[12] - 126_400.0) < 0.01
    # sanity: portfolio > contributions (positive returns)
    assert portfolio[12] > contributions[12]


def test_savings_less_than_rent():
    # savings=500 < rent=800 → contribution = -300/mo, portfolio shrinks
    portfolio, contributions = simulate_rent_strategy(
        months=12,
        starting_cash=10_000.0,
        monthly_savings=500.0,
        starting_rent=800.0,
        annual_rent_growth=0.0,
        annual_return=0.07,
    )

    assert len(portfolio) == 13
    assert len(contributions) == 13
    assert portfolio[0] == 10_000.0
    assert contributions[0] == 10_000.0
    # portfolio should decrease
    assert portfolio[12] < portfolio[0]
    # contributions track negative additions
    assert contributions[12] < contributions[0]
    # contributions = 10000 + 12 * (-300) = 6400
    assert abs(contributions[12] - 6_400.0) < 0.01
