GROSS_INCOME_BY_PERCENTILE = {
    # data from levels.fyi
    "10th": 28_600,
    "25th": 43_000,
    "50th": 58_300,
    "75th": 74_100,
    "90th": 91_300,
}

EXPENSES_BREAKDOWN = {
    # vienna
    # adjusted from numbeo.com: single, central 1bedroom
    "Housing": 800.00,
    "Utilities": 150.00,
    "Groceries": 280.00,
    "Transportation": 40.00,
    "Subscriptions": 40.00,
    "Discretionary": 70.00,
    "Miscellaneous": 50.00,
}

ANNUAL_EXPENSES = sum(EXPENSES_BREAKDOWN.values()) * 12
