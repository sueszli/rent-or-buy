from enum import Enum


def _net_special(gross_special_payments: float) -> float:
    assert 0 <= gross_special_payments < 1e12
    # social insurance
    sv_base = min(gross_special_payments, 12900.00)  # höchstbeitragsgrundlage sonderzahlungen, ASVG §108
    social_insurance = round(sv_base * 0.1707, 2)  # spacial payments rate
    assert social_insurance <= gross_special_payments

    # income tax
    taxable_base = gross_special_payments - social_insurance
    tax_free_amount = 620.00 * 2  # first 620 EUR of both payments are tax-free, EStG §67 (1) greibetrag
    taxed_amount = max(0.00, taxable_base - tax_free_amount)
    income_tax = round(taxed_amount * 0.06, 2)  # sechstel-tarif EStG §67 (1)

    net_salary = gross_special_payments - social_insurance - income_tax

    result = round(net_salary, 2)
    assert 0 <= result <= gross_special_payments + 0.01
    return result


def _tax_monthly(taxable_income: float) -> float:
    assert 0 <= taxable_income < 1e12
    tax_brackets = [
        (1037.33, 0.00),
        (1620.67, 0.20),
        (2704.00, 0.30),
        (5173.33, 0.40),
        (7760.00, 0.48),
        (float("inf"), 0.50),
    ]

    if taxable_income <= tax_brackets[0][0]:
        return 0.00

    income_tax = 0.00
    previous_limit = 0.00

    # progressive tax brackets, einkommensteuertarif, EStG § 33
    for limit, rate in tax_brackets:
        if taxable_income > previous_limit:
            taxable_in_bracket = min(taxable_income, limit) - previous_limit
            income_tax += taxable_in_bracket * rate
            previous_limit = limit

            if taxable_income <= limit:
                break

    # estimated tax deductibles, arbeitnehmerabsetzbetrag/berkehrsabsetzbetrag, EStG § 33
    income_tax = max(0.00, income_tax - 104.63)
    result = round(income_tax, 2)
    assert result >= 0
    return result


def _net_running(gross_salary_monthly: float) -> float:
    assert 0 <= gross_salary_monthly < 1e12
    gross = gross_salary_monthly

    # social insurance
    sv_base = min(gross, 6090.00)  # höchstbeitragsgrundlage, ASVG §108
    social_insurance = round(sv_base * 0.1812, 2)  # standard rate
    assert social_insurance <= gross

    # income tax
    taxable_income = gross - social_insurance
    income_tax = _tax_monthly(taxable_income)
    net_salary = gross - social_insurance - income_tax
    result = round(net_salary, 2)
    assert 0 <= result <= gross_salary_monthly + 0.01
    return result


def _net_salary_annual(annual_gross_salary: float) -> float:
    assert 0 <= annual_gross_salary < 1e13
    # based on: https://bruttonetto.arbeiterkammer.at/
    if annual_gross_salary <= 0:
        return 0

    # 12x running payments
    gross_monthly_running = annual_gross_salary / 14
    net_monthly = _net_running(gross_monthly_running)

    # 2x special payments (13th/14th)
    gross_special_payments = 2 * gross_monthly_running
    net_special = _net_special(gross_special_payments)

    result = 12 * net_monthly + net_special
    assert result >= 0
    return result


class IncomePercentile(Enum):
    # based on: https://www.levels.fyi/heatmap/europe/
    pct_10th = 28_600
    pct_25th = 43_000
    pct_50th = 58_300
    pct_75th = 74_100
    pct_90th = 91_300


def net_savings_monthly(income_annual: IncomePercentile, owns_property: bool = False) -> float:
    cost_of_living = {
        # single person in vienna, 1bd apartment, not overly frugal or lavish
        # based on:
        # - https://www.numbeo.com/cost-of-living/in/Vienna
        # - https://www.willhaben.at/iad/immobilien/mietwohnungen/wien
        "Housing": 0.00 if owns_property else 850.00,
        "Utilities": 290.00,  # energy + heating + internet + mobile
        "Groceries": 280.00,  # food
        "Transportation": 50.00,  # public transport annual pass, occasional taxi
        "Miscellaneous": 200.00,  # hygiene, clothing, social, repairs
    }

    # avg monthly savings, smoothing the 13th/14th salary over the year
    annual_expenses = sum(cost_of_living.values()) * 12
    net_annual_salary = _net_salary_annual(income_annual.value)
    return (net_annual_salary - annual_expenses) / 12
