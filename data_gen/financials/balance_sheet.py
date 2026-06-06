#  =============================================================================
#  FILE NAME: balance_sheet.py
#  PURPOSE: Creates a balance sheet for use in ongoing forecast impacts.
#  User-defined fuction: generate_balance_sheet
#  =============================================================================

#  Dependencies needed:
import numpy  as np
import pandas as pd
from src.data_gen.general_ledger import COA


def generate_balance_sheet(gl_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ending balances by account and classify into a rudimentary balance sheet.
    """
    # Net balance per account (debit - credit)
    balances = (
        gl_df.groupby("account")[["debit", "credit"]]
        .sum()
        .assign(balance=lambda x: x["debit"] - x["credit"])
        .reset_index()
    )

    def bal(acct_code):
        row = balances[balances["account"] == acct_code]
        return row["balance"].iloc[0] if not row.empty else 0.0

    bs_rows = []

    # Assets
    assets = [ ("Cash", COA["CASH"]),
               ("Accounts Receivable", COA["ACCOUNTS_RECEIVABLE"]),
               ("Accrued Revenue", COA["ACCRUED_REVENUE"]),
               ("Inventory", COA["INVENTORY"]),
               ("Prepaid Expenses", COA["PREPAID_EXPENSES"]),
               ("Property, Plant & Equipment", COA["PPE"]), ]
    
    contra_assets = [ ("Accumulated Depreciation", COA["ACCUM_DEPRECIATION"]) ]

    for label, code in assets:
        bs_rows.append({"section": "Assets", "label": label, "amount": bal(code)})
    for label, code in contra_assets:
        bs_rows.append({"section": "Assets", "label": label, "amount": bal(code)})

    # Liabilities
    liabilities = [ ("Accounts Payable", COA["ACCOUNTS_PAYABLE"]),
                    ("Accrued Expenses", COA["ACCRUED_EXPENSES"]),
                    ("Deferred Revenue", COA["DEFERRED_REVENUE"]),
                    ("Taxes Payable", COA["TAXES_PAYABLE"]),
                    ("Notes Payable", COA["NOTES_PAYABLE"]),
                    ("Interest Payable", COA["INTEREST_PAYABLE"]) ]
    for label, code in liabilities:
        bs_rows.append({"section": "Liabilities", "label": label, "amount": -bal(code)})

    # Equity
    equity = [
        ("Owner Contributions", COA["OWNER_CONTRIBUTIONS"]),
        ("Owner Distributions", COA["OWNER_DISTRIBUTIONS"]),
        ("Retained Earnings",   COA["RETAINED_EARNINGS"]) ]
    
    for label, code in equity:
        bs_rows.append({"section": "Equity", "label": label, "amount": -bal(code)})

    bs_df = pd.DataFrame(bs_rows)

    return bs_df