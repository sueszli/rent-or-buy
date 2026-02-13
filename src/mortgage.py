def _upfront_costs(purchase_price: float, mortgage_amount: float) -> float:
    """
    initial costs in addition to the minimum down payment

    - https://www.oesterreich.gv.at/en/themen/bauen_und_wohnen/wohnen/8/Seite.210150
    - https://www.usp.gv.at/themen/steuern-finanzen/weitere-steuern-und-abgaben/grunderwerbsteuer.html
    """
    assert 0 <= purchase_price
    assert 0 <= mortgage_amount

    VALUE_ADDED_TAX = 1.20

    TRANSFER_TAX = 0.035 * purchase_price  # grunderwerbsteuer
    LAND_REGISTER_FEE = 0.011 * purchase_price + 81
    MORTGAGE_REGISTRY_FEE = 0.012 * mortgage_amount
    LAWYER_AND_NOTARY_FEE = 0.03 * purchase_price * VALUE_ADDED_TAX

    def agent_commission() -> float:
        if purchase_price <= 36336.42:
            return 0.04 * purchase_price * VALUE_ADDED_TAX
        elif purchase_price <= 48448.51:
            return 1453.46 * VALUE_ADDED_TAX
        else:
            return 0.03 * purchase_price * VALUE_ADDED_TAX

    return TRANSFER_TAX + LAND_REGISTER_FEE + MORTGAGE_REGISTRY_FEE + LAWYER_AND_NOTARY_FEE + agent_commission()


def _mortgage_amount(purchase_price: float, cash_savings: float) -> float:
    """
    how much we need to borrow

    - https://www.fma.gv.at/en/banks/residential-real-estate-lending/
    """
    assert 0 <= purchase_price
    assert 0 <= cash_savings

    LOAN_TO_COLlATERAL_RATIO = 0.90  # KIM-VO regulation
    min_down = purchase_price * 0.10

    # initial assumption for mortgage
    # so we can deduct upfront costs from cash savings
    assumed_mortgage = purchase_price * LOAN_TO_COLlATERAL_RATIO
    upfront = _upfront_costs(purchase_price, assumed_mortgage)
    available_down = cash_savings - upfront
    if available_down < min_down:
        raise ValueError("cash savings insufficient for minimum down payment and costs")
    mortgage = purchase_price - available_down

    # check again
    upfront = _upfront_costs(purchase_price, mortgage)
    available_down = cash_savings - upfront
    if available_down < min_down:
        raise ValueError("cash savings insufficient for minimum down payment and costs")
    mortgage = purchase_price - available_down

    return mortgage


def _interest_rate(down_payment_ratio: float) -> float:
    """
    interest rate is better with higher down payment, better credit score

    - https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/kredite/Hypothekarkredite_202501.pdf
    - https://www.oenb.at/en/Statistics/Charts/Chart-4.html
    """

    BASE_INTEREST_RATE = 0.034

    if down_payment_ratio >= 0.40:
        return BASE_INTEREST_RATE - 0.005  # common discount (estimate)
    elif down_payment_ratio >= 0.30:
        return BASE_INTEREST_RATE - 0.0025
    elif down_payment_ratio >= 0.20:
        return BASE_INTEREST_RATE  # standard rate
    else:
        return BASE_INTEREST_RATE + 0.005  # common penalty (estimate)


def _monthly_ownership_costs() -> float:
    """
    property maintenance, regardless of mortgage

    varies with energy efficiency, etc.

    - https://www.statistik.at/statistiken/bevoelkerung-und-soziales/wohnen/wohnkosten
    - https://www.ovi.at/aktuelles/detailansicht/anhebung-der-mindestruecklage-1-1-2026
    - https://www.wko.at/oe/information-consulting/immobilien-vermoegenstreuhaender/mindestruecklage-wohnungseigentumsgesetz
    - https://www.arbeiterkammer.at/haushaltsversicherungen
    """
    typical_apartment_size_m2 = 80.0

    bk_rate = 2.60  # operating costs (betriebskosten)
    reserve_rate = 1.12  # maintenance reserve (reparaturrücklage)
    energy_rate = 2.50  # energy costs (heizkosten, warmwasser, strom)
    insurance_rate = 0.30  # insurance costs (hausversicherung, haftpflicht, etc.)
    energy_rate = 0.20  # tax costs (grundsteuer, etc.)
    total_cost_per_m2 = bk_rate + reserve_rate + energy_rate + insurance_rate
    return total_cost_per_m2 * typical_apartment_size_m2


def _monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """
    how much to pay monthly to pay off the loan in given years

    formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
    where M = monthly payment, P = principal, r = monthly rate, n = number of payments

    - https://www.fma.gv.at/en/fma-issues-regulation-for-sustainable-lending-standards-for-residential-real-estate-financing-kim-v/
    """
    assert 0 < principal
    assert 0 <= annual_rate <= 1.0
    assert 0 < years <= 35, "mortgage over 35 years is not permitted under KIM-VO regulation"

    if annual_rate <= 1e-9:
        return principal / (years * 12)
    monthly_rate = annual_rate / 12.0
    assert monthly_rate > 0
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)


def _simulate_payoff_years(
    mortgage_amount: float,
    annual_interest_rate: float,
    monthly_savings: float,
    monthly_ownership_costs: float,
) -> tuple[float, float]:
    """
    simulate month-by-month payoff considering prepayment rules and 10-year option to fully pay off with notice
    returns (years, total_interest_paid)
    """

    STANDARD_TERM_YEARS = 25
    ANNUAL_EXTRA_LIMIT_WITHOUT_PENALTY = 10000.0
    NOTICE_MONTHS_FOR_PREPAY = 6

    if mortgage_amount <= 0:
        return 0.0, 0.0

    monthly_interest_rate = annual_interest_rate / 12.0
    monthly_mortgage_payment = _monthly_mortgage_payment(mortgage_amount, annual_interest_rate, STANDARD_TERM_YEARS)
    available_for_mortgage = monthly_savings - monthly_ownership_costs
    if available_for_mortgage < monthly_mortgage_payment:
        raise ValueError("monthly savings insufficient for mortgage and ownership costs")

    extra_available = available_for_mortgage - monthly_mortgage_payment
    monthly_extra_max = ANNUAL_EXTRA_LIMIT_WITHOUT_PENALTY / 12.0

    balance = mortgage_amount
    accumulated_savings = 0.0
    month = 0
    total_interest = 0.0

    while balance > 0:
        month += 1
        if month > 1000 * 12:
            raise ValueError("simulation did not converge")

        # monthly interest and principal from standard payment
        interest = balance * monthly_interest_rate
        assert interest >= 0, f"Interest {interest} must be positive (balance={balance}, rate={monthly_interest_rate})"
        total_interest += interest
        principal = monthly_mortgage_payment - interest
        principal = max(principal, 0.0)  # prevent negative if rate=0
        balance -= principal
        if balance <= 0:
            break

        # apply extra principal without penalty (capped)
        extra_applied = min(extra_available, monthly_extra_max, balance)
        balance -= extra_applied
        if balance <= 0:
            break

        # accumulate savings beyond what can be applied without penalty
        excess_saved = max(0.0, extra_available - monthly_extra_max)
        accumulated_savings += excess_saved

        # after 10 years, check for penalty-free full prepayment with notice
        if month >= 120:
            excess_per_month = max(0.0, extra_available - monthly_extra_max)
            projected_lump = accumulated_savings + NOTICE_MONTHS_FOR_PREPAY * excess_per_month

            # simulate balance during notice period with continued payments
            temp_balance = balance
            temp_interest = 0.0
            for _ in range(NOTICE_MONTHS_FOR_PREPAY):
                if temp_balance <= 0:
                    break
                temp_interest_month = temp_balance * monthly_interest_rate
                temp_interest += temp_interest_month
                temp_principal = monthly_mortgage_payment - temp_interest_month
                temp_principal = max(temp_principal, 0.0)
                temp_extra = min(monthly_extra_max, temp_balance - temp_principal)
                temp_balance -= temp_principal + temp_extra

            if projected_lump >= max(temp_balance, 0.0):
                total_interest += temp_interest
                return (month + NOTICE_MONTHS_FOR_PREPAY) / 12.0, total_interest

    return month / 12.0, total_interest


def estimate_mortgage_payoff_years(
    monthly_savings: float,
    cash_savings: float = 200_000.0,
    purchase_price: float = 500_000.0,
) -> float:
    """
    estimate how many years it takes to pay off a mortgage
    """

    RENT_PER_M2 = 21.0  # based on 2025 data, approx €21 per m² including costs
    TYPICAL_PRICE_FOR_COSTS = 500000.0
    TYPICAL_APARTMENT_SIZE_M2 = 80.0

    assert monthly_savings > 0
    assert cash_savings >= 0
    assert purchase_price > 0

    # could we buy outright?
    cash_upfront = _upfront_costs(purchase_price, 0.0)
    remaining = purchase_price + cash_upfront - cash_savings
    if remaining <= 0:
        return 0.0

    # could we save up instead of getting a mortgage?
    scale_factor = purchase_price / TYPICAL_PRICE_FOR_COSTS
    apartment_size = TYPICAL_APARTMENT_SIZE_M2 * scale_factor
    rent = RENT_PER_M2 * apartment_size
    effective_monthly_save = monthly_savings - rent
    if effective_monthly_save > 0:
        save_months = remaining / effective_monthly_save
        save_years = save_months / 12.0
    else:
        save_months = 0.0
        save_years = float("inf")

    try:
        # simulate mortgage payoff
        mortgage_amount = _mortgage_amount(purchase_price, cash_savings)
        upfront = _upfront_costs(purchase_price, mortgage_amount)
        down_payment = cash_savings - upfront
        down_payment_ratio = down_payment / purchase_price
        annual_interest_rate = _interest_rate(down_payment_ratio)
        monthly_ownership_costs = _monthly_ownership_costs()
        payoff_years, total_interest = _simulate_payoff_years(
            mortgage_amount,
            annual_interest_rate,
            monthly_savings,
            monthly_ownership_costs,
        )

        extra_fees = upfront - cash_upfront
        mortgage_cost = total_interest + extra_fees
        save_benefit = (rent - monthly_ownership_costs) * (save_months if save_years < float("inf") else 0)
        if mortgage_cost > save_benefit:
            return save_years if save_years < float("inf") else payoff_years
        else:
            return payoff_years

    except Exception:
        # fall back to other option if mortgage simulation fails
        return save_years if save_years < float("inf") else float("inf")
