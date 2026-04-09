"""
Investor Return Calculator

Enter a development cost and an exit value to calculate key return metrics
for an investor, including profit, ROI, and equity multiple.
"""


def calculate_investor_return(development_cost: float, exit_value: float) -> dict:
    """Calculate investor return metrics given a development cost and exit value.

    Args:
        development_cost: Total cost of development (investor's capital invested).
        exit_value: Total value at exit (sale price, valuation, etc.).

    Returns:
        Dictionary with profit, ROI percentage, and equity multiple.
    """
    profit = exit_value - development_cost
    roi_percent = (profit / development_cost) * 100 if development_cost != 0 else 0
    equity_multiple = exit_value / development_cost if development_cost != 0 else 0

    return {
        "development_cost": development_cost,
        "exit_value": exit_value,
        "profit": profit,
        "roi_percent": roi_percent,
        "equity_multiple": equity_multiple,
    }


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"


def display_results(results: dict) -> None:
    """Print a formatted summary of investor return metrics."""
    print("\n" + "=" * 50)
    print("       INVESTOR RETURN SUMMARY")
    print("=" * 50)
    print(f"  Development Cost:  {format_currency(results['development_cost'])}")
    print(f"  Exit Value:        {format_currency(results['exit_value'])}")
    print("-" * 50)
    print(f"  Profit / (Loss):   {format_currency(results['profit'])}")
    print(f"  ROI:               {results['roi_percent']:,.2f}%")
    print(f"  Equity Multiple:   {results['equity_multiple']:.2f}x")
    print("=" * 50 + "\n")


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


def main():
    print("\n--- Investor Return Calculator ---\n")

    development_cost = get_dollar_input("Enter development cost: $")
    exit_value = get_dollar_input("Enter exit value:        $")

    results = calculate_investor_return(development_cost, exit_value)
    display_results(results)


if __name__ == "__main__":
    main()
