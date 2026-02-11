# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "tqdm==4.66.4",
#     "deal==4.24.6",
#     "polars==1.38.1",
# ]
# ///

from portfolio import simulate_portfolio

r = simulate_portfolio(monthly_savings=1000, start_month="01/2020", months=12, real=False)
print(r)
