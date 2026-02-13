import polars as pl

from mortgage import estimate_mortgage_payoff_years
from net_savings import IncomePercentile, net_savings_monthly
from portfolio import simulate_portfolio

INCOME = IncomePercentile.pct_75th

#
# mortgage
#

CASH_SAVINGS = 100_000
PURCHASE_PRICE = 400_000

monthly_savings = net_savings_monthly(income_annual=INCOME, pays_rent=False)
payoff_yrs = estimate_mortgage_payoff_years(monthly_savings=monthly_savings, cash_savings=CASH_SAVINGS, purchase_price=PURCHASE_PRICE)
print(f"morgage worth {PURCHASE_PRICE} EUR paid off in {payoff_yrs:.2f} years")  # ----> purchase price is wrong

#
# portfolio
#

monthly_savings = net_savings_monthly(income_annual=INCOME, pays_rent=True)  # ----> monthly savings is wrong
df = simulate_portfolio(monthly_savings=monthly_savings, years=payoff_yrs, start_year=2000)
max_date = df.select(pl.col("date").max()).item()
value = df.filter(pl.col("date") == max_date)["payout"].item()
print(value)


"""
todo:

- find historic rent inflation data
- find historic real estate inflation data

print plot:

- investment A) tracks value of real estate x pct paid off -> net worth
- investment B) tracks value of portfolio x num shares we have -> net worth
"""
