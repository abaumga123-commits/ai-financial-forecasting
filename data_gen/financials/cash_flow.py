#  =============================================================================
#  FILE NAME: cash_flow.py
#  PURPOSE: Creates a cash flow statement. Calculates using the Indirect method.
#  User-defined fuction: generate_cash_flow_statement
#  =============================================================================

#  Dependencies needed:
import numpy  as np
import pandas as pd
from src.data_gen.general_ledger import COA


def generate_cash_flow_statement(gl_df: pd.DataFrame, bs_start: pd.DataFrame, bs_end: pd.DataFrame) -> pd.DataFrame:
    """
    Simple indirect-method cash flow using beginning and ending balance sheets + GL.
    Assumes bs_start and bs_end are outputs of generate_balance_sheet().
    """
    def get(bs, label):
        row = bs[(bs["label"] == label)]
        return row["amount"].sum() if not row.empty else 0.0

    # Helper: change in balance (end - start)
    def delta(label):
        return get(bs_end, label) - get(bs_start, label)

    # Net income approximated from retained earnings change minus owner flows
    re_start = get(bs_start, "Retained Earnings"  )
    re_end   = get(bs_end,   "Retained Earnings"  )
    oc_start = get(bs_start, "Owner Contributions")
    oc_end   = get(bs_end,   "Owner Contributions")
    od_start = get(bs_start, "Owner Distributions")
    od_end   = get(bs_end,   "Owner Distributions")

    change_re  = re_end - re_start
    change_oc  = oc_end - oc_start
    change_od  = od_end - od_start
    net_income = change_re + change_od - change_oc  # rough but consistent

    # Non-cash items
    dep_exp = gl_df[gl_df["account"] == COA["DEPRECIATION_EXPENSE"]]["debit"].sum()

    # Working capital changes (assets: inverse, liabilities: direct)
    change_ar          = delta("Accounts Receivable")
    change_inv         = delta("Inventory")
    change_prepaid     = delta("Prepaid Expenses")
    change_accrued_rev = delta("Accrued Revenue")

    change_ap            = delta("Accounts Payable")
    change_accrued_exp   = delta("Accrued Expenses")
    change_def_rev       = delta("Deferred Revenue")
    change_taxes_payable = delta("Taxes Payable")

    cfo = (
        net_income
        + dep_exp
        - change_ar
        - change_inv
        - change_prepaid
        - change_accrued_rev
        + change_ap
        + change_accrued_exp
        + change_def_rev
        + change_taxes_payable
    )

    # Investing: CapEx approximated as change in PPE + change in Accum Dep
    ppe_start = get(bs_start, "Property, Plant & Equipment")
    ppe_end   = get(bs_end, "Property, Plant & Equipment")
    ad_start  = get(bs_start, "Accumulated Depreciation")
    ad_end    = get(bs_end, "Accumulated Depreciation")
    capex     = (ppe_end - ppe_start) + (ad_end - ad_start)
    cfi       = -capex

    # Financing: debt + equity flows
    np_start    = get(bs_start, "Notes Payable")
    np_end      = get(bs_end, "Notes Payable")
    change_debt = np_end - np_start

    oc_flow = change_oc  # contributions increase equity
    od_flow = -change_od  # distributions reduce equity

    cff = change_debt + oc_flow + od_flow

    rows = [
        {"section": "Operating", "label": "Net income", "amount": net_income},
        {"section": "Operating", "label": "Depreciation", "amount": dep_exp},
        {"section": "Operating", "label": "Change in AR", "amount": -change_ar},
        {"section": "Operating", "label": "Change in Inventory", "amount": -change_inv},
        {"section": "Operating", "label": "Change in Prepaid Expenses", "amount": -change_prepaid},
        {"section": "Operating", "label": "Change in Accrued Revenue", "amount": -change_accrued_rev},
        {"section": "Operating", "label": "Change in AP", "amount": change_ap},
        {"section": "Operating", "label": "Change in Accrued Expenses", "amount": change_accrued_exp},
        {"section": "Operating", "label": "Change in Deferred Revenue", "amount": change_def_rev},
        {"section": "Operating", "label": "Change in Taxes Payable", "amount": change_taxes_payable},
        {"section": "Operating", "label": "Net cash from operating activities", "amount": cfo},

        {"section": "Investing", "label": "Capital expenditures", "amount": cfi},
        {"section": "Investing", "label": "Net cash from investing activities", "amount": cfi},

        {"section": "Financing", "label": "Change in debt", "amount": change_debt},
        {"section": "Financing", "label": "Owner contributions", "amount": oc_flow},
        {"section": "Financing", "label": "Owner distributions", "amount": od_flow},
        {"section": "Financing", "label": "Net cash from financing activities", "amount": cff},
    ]

    return pd.DataFrame(rows)