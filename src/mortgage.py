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
    assert available_down >= min_down, "cash savings insufficient for minimum down payment and costs"
    mortgage = purchase_price - available_down

    # check again
    upfront = _upfront_costs(purchase_price, mortgage)
    available_down = cash_savings - upfront
    assert available_down >= min_down, "cash savings insufficient for minimum down payment and costs"
    mortgage = purchase_price - available_down

    return mortgage


def _interest_rate(down_payment_ratio: float) -> float:
    """
    interest rate is better with higher down payment, better credit score

    - https://wien.arbeiterkammer.at/beratung/konsumentenschutz/geld/kredite/Hypothekarkredite_202501.pdf
    - https://www.oenb.at/en/Statistics/Charts/Chart-4.html
    - https://www.fma.gv.at/en/fma-issues-regulation-for-sustainable-lending-standards-for-residential-real-estate-financing-kim-v/
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
    """
    assert 0 < principal
    assert 0 <= annual_rate <= 1.0
    assert 0 < years <= 35, "mortgage over 35 years is not permitted under KIM-VO regulation"

    num_payments = years * 12

    # handle 0% interest edge case
    if annual_rate <= 1e-9:
        return principal / num_payments

    monthly_rate = annual_rate / 12.0
    assert monthly_rate > 0

    # standard annuity formula
    factor = (1 + monthly_rate) ** num_payments
    return principal * (monthly_rate * factor) / (factor - 1)


def _simulate_payoff_years(
    mortgage_amount: float,
    annual_interest_rate: float,
    monthly_savings: float,
) -> float:
    """
    simulate month-by-month payoff considering

    you can pay a 1% penalty (HIKrG § 20) to exit a fixed-rate mortgage early

    - https://www.infina.at/ratgeber/finanzierung/laufzeit-kredit/
    - https://www.ris.bka.gv.at/NormDokument.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009367&Paragraf=20
    - https://www.arbeiterkammer.at/beratung/konsument/Geld/Kredite/Vorzeitige-Rueckzahlung-von-Krediten.html
    - https://www.infina.at/ratgeber/kredit-vorzeitig-zurueckzahlen/
    """
    STANDARD_TERM_YEARS = 25
    MAX_MONTHLY_PAYMENT = 10_000.0 / 12  # smoothed

    EARLY_EXIT_NOTICE_MONTHS = 6  # -----> is this even true????
    EARLY_EXIT_PENALTY_RATE = 0.01

    # paid off immediately
    if mortgage_amount <= 0:
        return 0.0

    monthly_mortgage_payment = _monthly_mortgage_payment(mortgage_amount, annual_interest_rate, STANDARD_TERM_YEARS)
    monthly_savings -= _monthly_ownership_costs()
    assert monthly_savings >= monthly_mortgage_payment, "insufficient monthly savings"
    monthly_excess = monthly_savings - monthly_mortgage_payment

    debt = mortgage_amount
    accumulated_savings = 0.0  # what we save up for a potential early exit
    accumulated_interest = 0.0  # what the bank earns for lending money
    month = 0

    while debt > 0:
        month += 1
        assert month <= 1000 * 12, "simulation did not converge"

        # pay regular monthly payment
        interest = debt * annual_interest_rate / 12.0
        assert interest >= 0, f"interest {interest} must be positive (debt={debt}, rate={annual_interest_rate / 12.0})"
        accumulated_interest += interest
        principal = monthly_mortgage_payment - interest
        principal = max(principal, 0.0)  # prevent negative if rate=0
        debt -= principal
        if debt <= 0:
            break

        # pay whatever we still have available (capped)
        extra_applied = min(monthly_excess, MAX_MONTHLY_PAYMENT, debt)
        debt -= extra_applied
        if debt <= 0:
            break

        # save the rest up for a potential early exit
        excess_saved = max(0.0, monthly_excess - MAX_MONTHLY_PAYMENT)
        accumulated_savings += excess_saved

        #
        # should we exit early?
        #

        excess_per_month = max(0.0, monthly_excess - MAX_MONTHLY_PAYMENT)
        projected_lump = accumulated_savings + EARLY_EXIT_NOTICE_MONTHS * excess_per_month

        # simulate loan during notice period with continued payments
        tmp_debt = debt
        tmp_interest = 0.0
        for _ in range(EARLY_EXIT_NOTICE_MONTHS):
            if tmp_debt <= 0:
                break
            temp_interest_month = tmp_debt * annual_interest_rate / 12.0
            tmp_interest += temp_interest_month
            temp_principal = monthly_mortgage_payment - temp_interest_month
            temp_principal = max(temp_principal, 0.0)
            temp_extra = min(MAX_MONTHLY_PAYMENT, tmp_debt - temp_principal)
            tmp_debt -= temp_principal + temp_extra

        penalty_cost = tmp_debt * EARLY_EXIT_PENALTY_RATE
        total_cost_to_exit = tmp_debt + penalty_cost

        # check if our saved lump sum covers the debt AND the penalty
        if projected_lump >= total_cost_to_exit:
            accumulated_interest += tmp_interest + penalty_cost
            return (month + EARLY_EXIT_NOTICE_MONTHS) / 12.0, accumulated_interest

    return month / 12.0


def estimate_mortgage_payoff_years(
    monthly_savings: float,
    cash_savings: float = 200_000.0,
    purchase_price: float = 500_000.0,
) -> float:
    """
    estimate how many years it takes to pay off a mortgage
    """
    assert monthly_savings > 0
    assert cash_savings >= 0
    assert purchase_price > 0

    # could we buy outright?
    cash_upfront = _upfront_costs(purchase_price, 0.0)
    remaining = purchase_price + cash_upfront - cash_savings
    if remaining <= 0:
        return 0.0

    # simulate mortgage payoff
    mortgage_amount = _mortgage_amount(purchase_price, cash_savings)
    upfront = _upfront_costs(purchase_price, mortgage_amount)
    down_payment = cash_savings - upfront
    down_payment_ratio = down_payment / purchase_price
    annual_interest_rate = _interest_rate(down_payment_ratio)
    payoff_years = _simulate_payoff_years(mortgage_amount, annual_interest_rate, monthly_savings)
    return payoff_years
