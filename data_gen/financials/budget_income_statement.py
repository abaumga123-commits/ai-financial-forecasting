# =============================================================================
# FILE NAME: budget_income_statement.py
# PURPOSE: Generates a synthetic annual monthly budgeted
# income statement aligned with the COA and actuals schema.
# User-defined function: generate_budget_income_statement
# =============================================================================

# Dependencies needed:
import numpy  as np
import pandas as pd
from src.data_gen.general_ledger import COA


def generate_budget_income_statement(
    year: int      = 2022,
    scale: float   = 1.0,
    seed: int      = 42,
    frequency: str = "annual"  # "annual", "quarterly", or "monthly"
) -> pd.DataFrame:
    """
    Create a synthetic budgeted income statement for the given year.
    Produces revenue, COGS, operating expenses, interest, taxes, and net income.

    Parameters
    ----------
    year : int
        Budget year.
    scale : float
        Scaling factor to make the company larger or smaller.
    seed : int
        Random seed for reproducibility.
    frequency : str
        "annual", "quarterly", or "monthly" budget granularity.

    Returns
    -------
    pd.DataFrame
        Budgeted income statement with columns:
        period, section, label, amount.
    """
    rng = np.random.default_rng(seed)

    # --- Revenue assumptions ---
    flagship_revenue = rng.uniform(8_000_000, 15_000_000) * scale
    other_revenue    = rng.uniform(5_000_000, 10_000_000) * scale
    total_revenue    = flagship_revenue + other_revenue

    # --- COGS ---
    cogs_pct = rng.uniform(0.45, 0.60)
    cogs = total_revenue * cogs_pct

    # --- Operating expenses ---
    gna_expense       = rng.uniform(1_500_000, 3_000_000) * scale
    depreciation      = rng.uniform(300_000, 600_000) * scale
    operating_expense = gna_expense + depreciation

    # --- Operating income ---
    operating_income = total_revenue - cogs - operating_expense

    # --- Interest expense ---
    interest_expense = rng.uniform(80_000, 200_000) * scale

    # --- Pretax income ---
    pretax_income = operating_income - interest_expense

    # --- Taxes ---
    tax_rate = 0.21
    tax_expense = max(0, pretax_income * tax_rate)

    # --- Net income ---
    net_income = pretax_income - tax_expense

    # --- Build base rows ---
    base_rows = [
        ("Revenue", "Flagship revenue", flagship_revenue),
        ("Revenue", "Other revenue",    other_revenue),
        ("Revenue", "Total revenue",    total_revenue),

        ("COGS", "Cost of goods sold", -cogs),
        ("Gross Profit", "Gross profit", total_revenue - cogs),

        ("Operating Expenses", "G&A expense",        -gna_expense),
        ("Operating Expenses", "Depreciation",       -depreciation),
        ("Operating Expenses", "Total operating expenses", -operating_expense),

        ("Operating Income", "Operating income", operating_income),

        ("Other Income/Expense", "Interest expense", -interest_expense),
        ("Pretax Income", "Income before taxes", pretax_income),

        ("Taxes", "Income tax expense", -tax_expense),
        ("Net Income", "Net income", net_income),
    ]

    # --- Determine periods ---
    if frequency == "annual":
        periods = [f"{year}"]
    elif frequency == "quarterly":
        periods = [f"{year}-Q1", f"{year}-Q2", f"{year}-Q3", f"{year}-Q4"]
    elif frequency == "monthly":
        periods = [f"{year}-{m:02d}" for m in range(1, 12 + 1)]
    else:
        raise ValueError("frequency must be 'annual', 'quarterly', or 'monthly'")

    # --- Allocate amounts across periods ---
    df_rows = []
    for period in periods:
        for section, label, amount in base_rows:
            df_rows.append({
                "period": period,
                "section": section,
                "label": label,
                "amount": amount / len(periods)
            })

    return pd.DataFrame(df_rows)