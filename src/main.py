# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "tqdm==4.66.4",
#     "deal==4.24.6",
#     "polars==1.38.1",
# ]
# ///

from portfolio import simulate_portfolio

print("--- Nominal (Real=False) ---")
r_nominal = simulate_portfolio(monthly_savings=1000, start_month="01/2020", months=12, real=False)
print("Portfolio Values:", r_nominal.values[-1])
print("Cost Basis:", r_nominal.cost_basis[-1])

print("\n--- Real (Real=True) ---")
r_real = simulate_portfolio(monthly_savings=1000, start_month="01/2020", months=12, real=True)
print("Portfolio Values:", r_real.values[-1])
print("Cost Basis:", r_real.cost_basis[-1])

print("\n--- Check ---")
print(f"Values match? {r_nominal.values[-1] == r_real.values[-1]}")
print("Expected: False (Real should be smaller)")
