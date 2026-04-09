"""
Investor Return Calculator

Enter development cost, capital structure (debt/equity), hold period, and exit
value to calculate investor returns including IRR, equity multiple, and a
preferred return waterfall distribution.
"""


def calculate_irr(cashflows: list[float], guess: float = 0.1, tol: float = 1e-8,
                  max_iter: int = 1000) -> float | None:
    """Calculate IRR using Newton's method.

    Args:
        cashflows: List of cashflows where index 0 is the initial investment
                   (negative) and subsequent entries are periodic returns.
        guess: Initial IRR guess.
        tol: Convergence tolerance.
        max_iter: Maximum iterations.

    Returns:
        IRR as a decimal (e.g. 0.15 = 15%), or None if it doesn't converge.
    """
    rate = guess
    for _ in range(max_iter):
        npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-14:
            return None
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    return None


def calculate_waterfall(equity_invested: float, exit_equity_proceeds: float,
                        hold_years: int, pref_rate: float,
                        lp_split: float, gp_split: float) -> dict:
    """Calculate a preferred return waterfall distribution.

    Tiers:
      1. Return of Capital  – LPs get their equity back first.
      2. Preferred Return   – LPs receive the preferred return (compounded annually).
      3. GP Catch-Up        – GP catches up to their promote share of total profit.
      4. Remaining Split     – Remaining profit is split LP/GP per the promote.

    Args:
        equity_invested: Total equity contributed by LPs.
        exit_equity_proceeds: Total equity proceeds available at exit after debt repayment.
        hold_years: Number of years the investment is held.
        pref_rate: Annual preferred return rate (e.g. 0.08 for 8%).
        lp_split: LP share of profits above the pref (e.g. 0.80 for 80%).
        gp_split: GP share of profits above the pref (e.g. 0.20 for 20%).

    Returns:
        Dictionary with waterfall tier breakdowns and totals.
    """
    remaining = exit_equity_proceeds

    # Tier 1: Return of Capital
    return_of_capital = min(remaining, equity_invested)
    remaining -= return_of_capital

    # Tier 2: Preferred Return (compounded annually)
    accrued_pref = equity_invested * ((1 + pref_rate) ** hold_years - 1)
    pref_paid = min(remaining, accrued_pref)
    remaining -= pref_paid

    # Tier 3: GP Catch-Up — GP gets 100% until they have gp_split of total
    # profit distributed so far (pref_paid + catch-up amount).
    # catch_up = gp_split / (1 - gp_split) * pref_paid
    if gp_split < 1.0:
        catch_up_target = (gp_split / (1 - gp_split)) * pref_paid
    else:
        catch_up_target = remaining
    gp_catch_up = min(remaining, catch_up_target)
    remaining -= gp_catch_up

    # Tier 4: Remaining split
    lp_residual = remaining * lp_split
    gp_residual = remaining * gp_split

    # Totals
    total_to_lp = return_of_capital + pref_paid + lp_residual
    total_to_gp = gp_catch_up + gp_residual

    return {
        "return_of_capital": return_of_capital,
        "accrued_pref": accrued_pref,
        "pref_paid": pref_paid,
        "gp_catch_up": gp_catch_up,
        "lp_residual": lp_residual,
        "gp_residual": gp_residual,
        "total_to_lp": total_to_lp,
        "total_to_gp": total_to_gp,
    }


def calculate_investor_return(development_cost: float, exit_value: float,
                              debt_amount: float, equity_amount: float,
                              hold_years: int, pref_rate: float,
                              lp_split: float, gp_split: float) -> dict:
    """Calculate full investor return metrics.

    Args:
        development_cost: Total project cost.
        exit_value: Gross sale / exit value.
        debt_amount: Loan / debt used to finance the project.
        equity_amount: Equity invested by LPs.
        hold_years: Investment hold period in years.
        pref_rate: Annual preferred return to LPs.
        lp_split: LP share of profit above pref.
        gp_split: GP share of profit above pref (promote).

    Returns:
        Dictionary with all return metrics.
    """
    # Equity proceeds after repaying debt
    exit_equity_proceeds = exit_value - debt_amount
    total_profit = exit_equity_proceeds - equity_amount

    # ROI and equity multiple on equity invested
    roi_percent = (total_profit / equity_amount) * 100 if equity_amount else 0
    equity_multiple = exit_equity_proceeds / equity_amount if equity_amount else 0

    # IRR cashflows: equity out at year 0, equity proceeds in at final year
    cashflows = [-equity_amount] + [0.0] * (hold_years - 1) + [exit_equity_proceeds]
    irr = calculate_irr(cashflows)

    # Waterfall
    waterfall = calculate_waterfall(
        equity_amount, exit_equity_proceeds, hold_years, pref_rate,
        lp_split, gp_split,
    )

    return {
        "development_cost": development_cost,
        "debt_amount": debt_amount,
        "equity_amount": equity_amount,
        "exit_value": exit_value,
        "exit_equity_proceeds": exit_equity_proceeds,
        "hold_years": hold_years,
        "total_profit": total_profit,
        "roi_percent": roi_percent,
        "equity_multiple": equity_multiple,
        "irr": irr,
        "pref_rate": pref_rate,
        "lp_split": lp_split,
        "gp_split": gp_split,
        "waterfall": waterfall,
    }


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"


def display_results(r: dict) -> None:
    """Print a formatted summary of investor return metrics."""
    w = r["waterfall"]

    print("\n" + "=" * 58)
    print("           INVESTOR RETURN SUMMARY")
    print("=" * 58)

    print("\n  CAPITAL STRUCTURE")
    print("  " + "-" * 40)
    print(f"  Development Cost:    {format_currency(r['development_cost'])}")
    print(f"  Debt:                {format_currency(r['debt_amount'])}")
    print(f"  Equity:              {format_currency(r['equity_amount'])}")
    ltv = (r["debt_amount"] / r["development_cost"] * 100) if r["development_cost"] else 0
    print(f"  Loan-to-Cost:        {ltv:.1f}%")

    print(f"\n  EXIT  (Year {r['hold_years']})")
    print("  " + "-" * 40)
    print(f"  Gross Exit Value:    {format_currency(r['exit_value'])}")
    print(f"  Less Debt Repayment: {format_currency(r['debt_amount'])}")
    print(f"  Equity Proceeds:     {format_currency(r['exit_equity_proceeds'])}")

    print("\n  RETURNS")
    print("  " + "-" * 40)
    print(f"  Total Profit:        {format_currency(r['total_profit'])}")
    print(f"  ROI:                 {r['roi_percent']:,.2f}%")
    print(f"  Equity Multiple:     {r['equity_multiple']:.2f}x")
    irr_str = f"{r['irr'] * 100:.2f}%" if r["irr"] is not None else "N/A"
    print(f"  IRR:                 {irr_str}")

    print(f"\n  PREFERRED RETURN WATERFALL")
    print(f"  (Pref: {r['pref_rate']*100:.1f}%  |  "
          f"LP/GP Split: {r['lp_split']*100:.0f}/{r['gp_split']*100:.0f})")
    print("  " + "-" * 40)
    print(f"  1. Return of Capital (LP):  {format_currency(w['return_of_capital'])}")
    print(f"  2. Preferred Return (LP):   {format_currency(w['pref_paid'])}")
    print(f"     (Accrued pref:           {format_currency(w['accrued_pref'])})")
    print(f"  3. GP Catch-Up:             {format_currency(w['gp_catch_up'])}")
    print(f"  4. Remaining to LP:         {format_currency(w['lp_residual'])}")
    print(f"     Remaining to GP:         {format_currency(w['gp_residual'])}")
    print("  " + "-" * 40)
    print(f"  Total to LP:                {format_currency(w['total_to_lp'])}")
    print(f"  Total to GP:                {format_currency(w['total_to_gp'])}")

    lp_multiple = w["total_to_lp"] / r["equity_amount"] if r["equity_amount"] else 0
    lp_cashflows = [-r["equity_amount"]] + [0.0] * (r["hold_years"] - 1) + [w["total_to_lp"]]
    lp_irr = calculate_irr(lp_cashflows)
    lp_irr_str = f"{lp_irr * 100:.2f}%" if lp_irr is not None else "N/A"
    print(f"\n  LP Equity Multiple:         {lp_multiple:.2f}x")
    print(f"  LP IRR:                     {lp_irr_str}")

    print("=" * 58 + "\n")


def get_dollar_input(prompt: str) -> float:
    """Prompt the user for a dollar amount, handling invalid input."""
    while True:
        try:
            raw = input(prompt).strip().replace("$", "").replace(",", "")
            value = float(raw)
            if value < 0:
                print("  Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a numeric value.")


def get_int_input(prompt: str, minimum: int = 1) -> int:
    """Prompt the user for an integer."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value < minimum:
                print(f"  Please enter a number of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a whole number.")


def get_percent_input(prompt: str) -> float:
    """Prompt the user for a percentage and return as a decimal."""
    while True:
        try:
            raw = input(prompt).strip().replace("%", "")
            value = float(raw)
            if value < 0 or value > 100:
                print("  Please enter a value between 0 and 100.")
                continue
            return value / 100.0
        except ValueError:
            print("  Invalid input. Please enter a numeric value.")


def main():
    print("\n--- Investor Return Calculator ---\n")

    development_cost = get_dollar_input("Development Cost:          $")
    debt_amount = get_dollar_input("Debt Amount:               $")
    equity_amount = development_cost - debt_amount
    if equity_amount <= 0:
        print(f"\n  Equity = Cost - Debt = {format_currency(equity_amount)}")
        print("  Debt cannot exceed development cost. Please try again.\n")
        return
    print(f"  -> Equity Required:        {format_currency(equity_amount)}")

    exit_value = get_dollar_input("Exit Value:                $")
    hold_years = get_int_input("Hold Period (years):        ")
    pref_rate = get_percent_input("Preferred Return (%):       ")
    gp_split = get_percent_input("GP Promote / Split (%):     ")
    lp_split = 1.0 - gp_split

    results = calculate_investor_return(
        development_cost, exit_value, debt_amount, equity_amount,
        hold_years, pref_rate, lp_split, gp_split,
    )
    display_results(results)


if __name__ == "__main__":
    main()
