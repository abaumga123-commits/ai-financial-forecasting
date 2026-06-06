# =============================================================================
# FILE NAME: opening_balance_sheet.py
# PURPOSE: Generates an opening balance sheet to seed subsequent forecasting
# impacts to period-ending balances and to enable metrics for MD&A discussion
# and working capital planning.
# User-defined function: generate_opening_balance_sheet
# =============================================================================

import numpy as np
import pandas as pd
from src.data_gen.general_ledger import COA


def generate_opening_balance_sheet(
    seed: int = 42,
    scale: float = 1.0
) -> pd.DataFrame:
    """
    Create a synthetic opening balance sheet using realistic mid-market
    financial proportions. This serves as the 'beginning of period' BS
    for cash flow modeling and forecasting.

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    scale : float
        Scaling factor to make the company larger or smaller.

    Returns
    -------
    pd.DataFrame
        Balance sheet with columns: section, label, amount.
    """
    rng = np.random.default_rng(seed)

    # --- Assets ---
    cash                =  rng.uniform(200_000, 800_000) * scale
    ar                  =  rng.uniform(300_000, 900_000) * scale
    accrued_revenue     =  rng.uniform(20_000, 80_000)   * scale
    inventory           =  rng.uniform(400_000, 1_200_000) * scale
    prepaid_expenses    =  rng.uniform(30_000, 120_000)  * scale
    ppe                 =  rng.uniform(1_000_000, 3_000_000) * scale
    accum_dep           = -rng.uniform(200_000, 600_000) * scale  # contra-asset

    # --- Liabilities ---
    ap                  = -rng.uniform(250_000, 700_000) * scale
    accrued_expenses    = -rng.uniform(80_000, 200_000)  * scale
    deferred_revenue    = -rng.uniform(40_000, 120_000)  * scale
    taxes_payable       = -rng.uniform(20_000, 90_000)   * scale
    notes_payable       = -rng.uniform(500_000, 1_500_000) * scale
    interest_payable    = -rng.uniform(10_000, 40_000)   * scale

    # --- Equity ---
    owner_contrib       = -rng.uniform(1_000_000, 3_000_000) * scale
    owner_distrib       =  rng.uniform(50_000, 200_000) * scale  # debit balance
    retained_earnings   = -rng.uniform(300_000, 900_000) * scale

    rows = [
        # Assets
        {"section": "Assets", "label": "Cash",                         "amount": cash},
        {"section": "Assets", "label": "Accounts Receivable",          "amount": ar},
        {"section": "Assets", "label": "Accrued Revenue",              "amount": accrued_revenue},
        {"section": "Assets", "label": "Inventory",                    "amount": inventory},
        {"section": "Assets", "label": "Prepaid Expenses",             "amount": prepaid_expenses},
        {"section": "Assets", "label": "Property, Plant & Equipment",  "amount": ppe},
        {"section": "Assets", "label": "Accumulated Depreciation",     "amount": accum_dep},

        # Liabilities
        {"section": "Liabilities", "label": "Accounts Payable",        "amount": ap},
        {"section": "Liabilities", "label": "Accrued Expenses",        "amount": accrued_expenses},
        {"section": "Liabilities", "label": "Deferred Revenue",        "amount": deferred_revenue},
        {"section": "Liabilities", "label": "Taxes Payable",           "amount": taxes_payable},
        {"section": "Liabilities", "label": "Notes Payable",           "amount": notes_payable},
        {"section": "Liabilities", "label": "Interest Payable",        "amount": interest_payable},

        # Equity
        {"section": "Equity", "label": "Owner Contributions",          "amount": owner_contrib},
        {"section": "Equity", "label": "Owner Distributions",          "amount": owner_distrib},
        {"section": "Equity", "label": "Retained Earnings",            "amount": retained_earnings},
    ]

    return pd.DataFrame(rows)