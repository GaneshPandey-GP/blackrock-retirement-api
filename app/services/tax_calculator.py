def calculate_tax(income: float) -> float:
    tax = 0.0

    if income <= 700000:
        return 0.0
    elif income <= 1000000:
        tax = (income - 700000) * 0.10
    elif income <= 1200000:
        tax = (300000 * 0.10) + (income - 1000000) * 0.15
    elif income <= 1500000:
        tax = (300000 * 0.10) + (200000 * 0.15) + (income - 1200000) * 0.20
    else:
        tax = (300000 * 0.10) + (200000 * 0.15) + (300000 * 0.20) + (income - 1500000) * 0.30

    return tax


def calculate_tax_benefit(invested: float, annual_wage: float) -> float:
    nps_deduction = min(invested, annual_wage * 0.10, 200000)
    tax_before = calculate_tax(annual_wage)
    tax_after = calculate_tax(annual_wage - nps_deduction)
    return round(tax_before - tax_after, 2)