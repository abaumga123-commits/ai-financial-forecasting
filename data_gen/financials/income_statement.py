#  =============================================================================
#  FILE NAME: income_statemen t.py
#  PURPOSE: Creates an Income Statement.
#  User-defined fuction: generate_income_statement
#  =============================================================================

#  Dependencies needed:
import numpy  as np
import pandas as pd
from src.data_gen.general_ledger import COA


def generate_income_statement(gl_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a rudimentary GAAP-style income statement from the general ledger.
    Uses debit/credit balances to compute:
      - Revenue (flagship + other)
      - COGS
      - Gross profit
      - Operating expenses (G&A + depreciation)
      - Operating income
      - Interest expense
      - Pretax income
      - Tax expense
      - Net income
    """

    # Helper: net balance for an account (credit - debit for revenue; debit - credit for expenses)
    def net_credit(acct):
        df = gl_df[gl_df["account"] == acct]
        return df["credit"].sum() - df["debit"].sum()

    def net_debit(acct):
        df = gl_df[gl_df["account"] == acct]
        return df["debit"].sum() - df["credit"].sum()

    # Revenue
    rev_flagship = net_credit(COA["REVENUE_FLAGSHIP"])
    rev_other = net_credit(COA["REVENUE_OTHER"])
    total_revenue = rev_flagship + rev_other

    # COGS
    cogs = net_debit(COA["COGS"])

    # Gross profit
    gross_profit = total_revenue - cogs

    # Operating expenses
    gna = net_debit(COA["GNA_EXPENSE"])
    depreciation = net_debit(COA["DEPRECIATION_EXPENSE"])
    operating_expenses = gna + depreciation

    # Operating income
    operating_income = gross_profit - operating_expenses

    # Interest expense
    interest_exp = net_debit(COA["INTEREST_EXPENSE"])

    # Pretax income
    pretax_income = operating_income - interest_exp

    # Tax expense (from GL)
    tax_exp = gl_df[
        (gl_df["account"] == COA["GNA_EXPENSE"]) &
        (gl_df["description"].str.contains("tax", case=False))
    ]["debit"].sum()

    # Net income
    net_income = pretax_income - tax_exp

    rows = [
        {"section": "Revenue", "label": "Flagship revenue", "amount": rev_flagship},
        {"section": "Revenue", "label": "Other revenue", "amount": rev_other},
        {"section": "Revenue", "label": "Total revenue", "amount": total_revenue},

        {"section": "COGS", "label": "Cost of goods sold", "amount": -cogs},
        {"section": "Gross Profit", "label": "Gross profit", "amount": gross_profit},

        {"section": "Operating Expenses", "label": "G&A expense", "amount": -gna},
        {"section": "Operating Expenses", "label": "Depreciation", "amount": -depreciation},
        {"section": "Operating Expenses", "label": "Total operating expenses", "amount": -operating_expenses},

        {"section": "Operating Income", "label": "Operating income", "amount": operating_income},

        {"section": "Other Income/Expense", "label": "Interest expense", "amount": -interest_exp},
        {"section": "Pretax Income", "label": "Income before taxes", "amount": pretax_income},

        {"section": "Taxes", "label": "Income tax expense", "amount": -tax_exp},
        {"section": "Net Income", "label": "Net income", "amount": net_income},
    ]

    return pd.DataFrame(rows)