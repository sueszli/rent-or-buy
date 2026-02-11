import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from net_savings import IncomePercentile, _net_running, _net_salary_annual, _net_special, _tax_monthly, net_savings_monthly

# --- _tax_monthly ---


def test_tax_monthly_below_first_bracket():
    # income <= 1037.33 → 0 tax
    assert _tax_monthly(1000.00) == 0.00
    assert _tax_monthly(0.00) == 0.00
    assert _tax_monthly(1037.33) == 0.00


def test_tax_monthly_in_second_bracket():
    # income 1200: taxable in bracket = 1200 - 1037.33 = 162.67 * 0.20 = 32.534
    # minus deductible 104.63 → max(0, 32.534 - 104.63) = 0
    assert _tax_monthly(1200.00) == 0.00


def test_tax_monthly_in_third_bracket():
    # income 2000:
    # bracket 1: 1037.33 * 0.00 = 0
    # bracket 2: (1620.67 - 1037.33) * 0.20 = 583.34 * 0.20 = 116.668
    # bracket 3: (2000 - 1620.67) * 0.30 = 379.33 * 0.30 = 113.799
    # total = 230.467, minus 104.63 = 125.837, rounded = 125.84
    assert _tax_monthly(2000.00) == 125.84


def test_tax_monthly_high_income():
    # income 8000 (above all finite brackets):
    # bracket 1: 1037.33 * 0.00 = 0
    # bracket 2: 583.34 * 0.20 = 116.668
    # bracket 3: 1083.33 * 0.30 = 324.999
    # bracket 4: 2469.33 * 0.40 = 987.732
    # bracket 5: 2586.67 * 0.48 = 1241.6016
    # bracket 6: (8000 - 7760) * 0.50 = 120.0
    # total = 2791.0006, minus 104.63 = 2686.3706, rounded = 2686.37
    assert _tax_monthly(8000.00) == 2686.37


# --- _net_special ---


def test_net_special_small_amount():
    # gross = 2000: sv_base = min(2000, 12900) = 2000, SI = 2000 * 0.1707 = 341.40
    # taxable = 2000 - 341.40 = 1658.60, tax_free = 1240
    # taxed = max(0, 1658.60 - 1240) = 418.60, tax = 418.60 * 0.06 = 25.12 (rounded)
    # net = 2000 - 341.40 - 25.12 = 1633.48
    assert _net_special(2000.00) == 1633.48


def test_net_special_above_sv_cap():
    # gross = 15000: sv_base = min(15000, 12900) = 12900, SI = 12900 * 0.1707 = 2202.03
    # taxable = 15000 - 2202.03 = 12797.97, tax_free = 1240
    # taxed = 12797.97 - 1240 = 11557.97, tax = 11557.97 * 0.06 = 693.48 (rounded)
    # net = 15000 - 2202.03 - 693.48 = 12104.49
    assert _net_special(15000.00) == 12104.49


def test_net_special_very_small():
    # gross = 1000: SI = 1000 * 0.1707 = 170.70
    # taxable = 829.30, tax_free = 1240, taxed = max(0, 829.30 - 1240) = 0
    # net = 1000 - 170.70 - 0 = 829.30
    assert _net_special(1000.00) == 829.30


# --- _net_running ---


def test_net_running_low_salary():
    # gross = 2000: sv_base = min(2000, 6090) = 2000, SI = 2000 * 0.1812 = 362.40
    # taxable = 2000 - 362.40 = 1637.60
    # tax = _tax_monthly(1637.60)
    #   bracket2: (1620.67 - 1037.33) * 0.20 = 116.668
    #   bracket3: (1637.60 - 1620.67) * 0.30 = 16.93 * 0.30 = 5.079
    #   total = 121.747 - 104.63 = 17.117 → 17.12
    # net = 2000 - 362.40 - 17.12 = 1620.48
    assert _net_running(2000.00) == 1620.48


def test_net_running_above_sv_cap():
    # gross = 7000: sv_base = min(7000, 6090) = 6090, SI = 6090 * 0.1812 = 1103.51 (rounded)
    # taxable = 7000 - 1103.51 = 5896.49
    # tax = _tax_monthly(5896.49)
    #   bracket1: 1037.33 * 0 = 0
    #   bracket2: 583.34 * 0.20 = 116.668
    #   bracket3: 1083.33 * 0.30 = 324.999
    #   bracket4: (5173.33 - 2704) * 0.40 = 2469.33 * 0.40 = 987.732
    #   bracket5: (5896.49 - 5173.33) * 0.48 = 723.16 * 0.48 = 347.1168
    #   total = 1776.5158 - 104.63 = 1671.8858 → 1671.89
    # net = 7000 - 1103.51 - 1671.89 = 4224.60
    result = _net_running(7000.00)
    # allow small rounding tolerance due to chained rounding
    assert abs(result - 4224.60) <= 0.02


# --- _net_salary_annual ---


def test_net_salary_annual_zero():
    assert _net_salary_annual(0) == 0
    assert _net_salary_annual(-1000) == 0


def test_net_salary_annual_median():
    # gross_annual = 58300 (pct_50th)
    # monthly_running = 58300 / 14 = 4164.285714...
    # net_monthly = _net_running(4164.285714...)
    # gross_special = 2 * 4164.285714... = 8328.571428...
    # net_special = _net_special(8328.571428...)
    # annual = 12 * net_monthly + net_special
    result = _net_salary_annual(58_300)
    # cross-check: median salary should yield roughly 36k-42k net
    assert 36_000 < result < 42_000


# --- net_savings_monthly ---


def test_net_savings_monthly_renter():
    result = net_savings_monthly(IncomePercentile.pct_50th, owns_property=False)
    # expenses for renter: (850 + 290 + 280 + 50 + 200) * 12 = 1670 * 12 = 20040
    # net annual for 58300 gross is ~38k-40k, so savings ~18k-20k/yr → ~1500-1700/mo
    assert result > 0


def test_net_savings_monthly_owner():
    result = net_savings_monthly(IncomePercentile.pct_50th, owns_property=True)
    # expenses for owner: (0 + 290 + 280 + 50 + 200) * 12 = 820 * 12 = 9840
    # owner saves more than renter (no housing cost)
    assert result > 0


def test_owner_saves_more_than_renter():
    renter = net_savings_monthly(IncomePercentile.pct_50th, owns_property=False)
    owner = net_savings_monthly(IncomePercentile.pct_50th, owns_property=True)
    assert owner > renter
    # difference should be exactly 850 (the housing cost)
    assert abs((owner - renter) - 850.00) < 0.01


def test_net_savings_monthly_low_income():
    # lowest percentile renter: might still be positive or close to zero
    result = net_savings_monthly(IncomePercentile.pct_10th, owns_property=False)
    # 28600 gross → ~20k net → 20040 expenses → near zero savings
    assert isinstance(result, float)


def test_net_savings_increases_with_income():
    results = [net_savings_monthly(p, owns_property=False) for p in IncomePercentile]
    for i in range(1, len(results)):
        assert results[i] > results[i - 1]
