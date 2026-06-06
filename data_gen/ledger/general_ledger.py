#  =============================================================================
#  FILE NAME: general_ledger.py
#  PURPOSE: Generates a GL to track impacts to the Income Statement, the Balance
#  Sheet, and the Cash Flow Statement.
#  User-defined fuction: generate_general_ledger
#  =============================================================================

# Dependencies needed:
import numpy as np
import pandas as pd


COA = { "CASH":                 "1000",
        "ACCOUNTS_RECEIVABLE":  "1100",
        "ACCRUED_REVENUE":      "1150",
        "INVENTORY":            "1200",
        "PREPAID_EXPENSES":     "1300",
        "PPE":                  "1500",
        "ACCUM_DEPRECIATION":   "1600",

        "ACCOUNTS_PAYABLE":     "2000",
        "ACCRUED_EXPENSES":     "2100",
        "DEFERRED_REVENUE":     "2200",
        "TAXES_PAYABLE":        "2300",
        "NOTES_PAYABLE":        "2500",
        "INTEREST_PAYABLE":     "2550",

        "REVENUE_FLAGSHIP":     "3000",
        "REVENUE_OTHER":        "3010",
        "COGS":                 "3100",

        "GNA_EXPENSE":          "4000",
        "DEPRECIATION_EXPENSE": "4100",
        "INTEREST_EXPENSE":     "4200",

        "RETAINED_EARNINGS":    "5000",
        "OWNER_CONTRIBUTIONS":  "5100",
        "OWNER_DISTRIBUTIONS":  "5200", }

def generate_general_ledger(
    inventory_df: pd.DataFrame,
    products_df: pd.DataFrame,
    random_state: int = 42,
    tax_rate: float = 0.21,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    gl_records = []
    je_counter = 1

    inv = inventory_df.merge(
        products_df[["sku_id", "base_price", "is_flagship"]],
        on="sku_id",
        how="left"
    )

    # --- Core operating events: inventory + sales ---
    for _, row in inv.iterrows():
        date          = row["date"]
        sku           = row["sku_id"]
        qty           = row["quantity"]
        extended_cost = row["extended_cost"]

        # Inventory receipt: DR Inventory / CR AP
        if row["txn_type"] == "receipt":
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["INVENTORY"],
                "debit":       abs(extended_cost),
                "credit":      0.0,
                "description": f"Inventory receipt for {sku}",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["ACCOUNTS_PAYABLE"],
                "debit":       0.0,
                "credit":      abs(extended_cost),
                "description": f"AP accrual for PO on {sku}",
            })
            je_counter += 1

        # Inventory issue + sale: DR COGS / CR Inventory; DR AR / CR Revenue
        elif row["txn_type"] == "issue":
            # COGS
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["COGS"],
                "debit":       abs(extended_cost),
                "credit":      0.0,
                "description": f"COGS for sale of {sku}",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["INVENTORY"],
                "debit":       0.0,
                "credit":      abs(extended_cost),
                "description": f"Inventory relief for {sku}",
            })
            je_counter += 1

            # Revenue
            sale_price   = row["base_price"] * rng.uniform(0.95, 1.10)
            revenue      = abs(qty) * sale_price
            revenue_acct = COA["REVENUE_FLAGSHIP"] if row["is_flagship"] else COA["REVENUE_OTHER"]

            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["ACCOUNTS_RECEIVABLE"],
                "debit":       revenue,
                "credit":      0.0,
                "description": f"AR for sale of {sku}",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     revenue_acct,
                "debit":       0.0,
                "credit":      revenue,
                "description": f"Revenue for sale of {sku}",
            })
            je_counter += 1

    gl_df = pd.DataFrame(gl_records)

    # --- Cash receipts: DR Cash / CR AR ---
    ar_entries = gl_df[gl_df["account"] == COA["ACCOUNTS_RECEIVABLE"]]
    for _, row in ar_entries.iterrows():
        if rng.random() < 0.85:
            amount = row["debit"]
            date = row["date"]
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["CASH"],
                "debit":       amount,
                "credit":      0.0,
                "description": "Cash receipt",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["ACCOUNTS_RECEIVABLE"],
                "debit":       0.0,
                "credit":      amount,
                "description": "AR settlement",
            })
            je_counter += 1

    # --- Cash disbursements: DR AP / CR Cash ---
    ap_entries = gl_df[gl_df["account"] == COA["ACCOUNTS_PAYABLE"]]
    for _, row in ap_entries.iterrows():
        if rng.random() < 0.80:
            amount = row["credit"]
            date   = row["date"]
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["ACCOUNTS_PAYABLE"],
                "debit":       amount,
                "credit":      0.0,
                "description": "AP payment",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["CASH"],
                "debit":       0.0,
                "credit":      amount,
                "description": "Cash disbursement",
            })
            je_counter += 1

    # --- Monthly accrued expenses: DR G&A / CR Accrued Expenses ---
    gl_tmp = pd.DataFrame(gl_records)
    months = sorted(set(gl_tmp["date"]))
    months = sorted({d[:7] for d in months})
    for m in months:
        accrual = rng.uniform(5_000, 25_000)
        date    = f"{m}-28"
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        date,
            "account":     COA["GNA_EXPENSE"],
            "debit":       accrual,
            "credit":      0.0,
            "description": "Monthly accrued expenses",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        date,
            "account":     COA["ACCRUED_EXPENSES"],
            "debit":       0.0,
            "credit":      accrual,
            "description": "Accrued expenses liability",
        })
        je_counter += 1

    # --- Simple prepaids: DR Prepaid / CR Cash (once per quarter) ---
    gl_tmp = pd.DataFrame(gl_records)
    unique_dates = sorted(set(gl_tmp["date"]))
    if unique_dates:
        quarters = sorted({d[:4] + "-Q" + str((int(d[5:7]) - 1)//3 + 1) for d in unique_dates})
        for q in quarters:
            year   = q[:4]
            qnum   = int(q[-1])
            month  = (qnum - 1) * 3 + 1
            date   = f"{year}-{month:02d}-05"
            amount = rng.uniform(10_000, 40_000)
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["PREPAID_EXPENSES"],
                "debit":       amount,
                "credit":      0.0,
                "description": "Prepaid expense (e.g., insurance)",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["CASH"],
                "debit":       0.0,
                "credit":      amount,
                "description": "Cash paid for prepaids",
            })
            je_counter += 1

    # --- CapEx + depreciation ---
    gl_tmp = pd.DataFrame(gl_records)
    if unique_dates:
        mid_date = sorted(unique_dates)[len(unique_dates)//2]
        capex_amount = rng.uniform(50_000, 150_000)
        # CapEx: DR PPE / CR Cash
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        mid_date,
            "account":     COA["PPE"],
            "debit":       capex_amount,
            "credit":      0.0,
            "description": "Capital expenditure",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        mid_date,
            "account":     COA["CASH"],
            "debit":       0.0,
            "credit":      capex_amount,
            "description": "Cash paid for CapEx",
        })
        je_counter += 1

        # Depreciation: DR Depreciation Expense / CR Accumulated Depreciation (monthly)
        months = sorted({d[:7] for d in unique_dates})
        monthly_dep = capex_amount / max(36, len(months))  # simple straight-line
        for m in months:
            date = f"{m}-28"
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["DEPRECIATION_EXPENSE"],
                "debit":       monthly_dep,
                "credit":      0.0,
                "description": "Monthly depreciation",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["ACCUM_DEPRECIATION"],
                "debit":       0.0,
                "credit":      monthly_dep,
                "description": "Accumulated depreciation",
            })
            je_counter += 1

    # --- Debt: simple note payable + interest ---
    if unique_dates:
        start_date  = sorted(unique_dates)[0]
        debt_amount = rng.uniform(100_000, 300_000)
        # Initial borrowing: DR Cash / CR Notes Payable
        gl_records.append({
            "je_id":      f"JE-{je_counter:07d}",
            "date":       start_date,
            "account":    COA["CASH"],
            "debit":       debt_amount,
            "credit":      0.0,
            "description": "Debt proceeds",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        start_date,
            "account":     COA["NOTES_PAYABLE"],
            "debit":       0.0,
            "credit":      debt_amount,
            "description": "Notes payable",
        })
        je_counter += 1

        # Interest accruals: DR Interest Expense / CR Interest Payable (monthly)
        months = sorted({d[:7] for d in unique_dates})
        annual_rate = 0.06
        monthly_rate = annual_rate / 12
        for m in months:
            date = f"{m}-28"
            interest = debt_amount * monthly_rate
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["INTEREST_EXPENSE"],
                "debit":       interest,
                "credit":      0.0,
                "description": "Interest expense",
            })
            gl_records.append({
                "je_id":       f"JE-{je_counter:07d}",
                "date":        date,
                "account":     COA["INTEREST_PAYABLE"],
                "debit":       0.0,
                "credit":      interest,
                "description": "Interest payable",
            })
            je_counter += 1

    # --- Owner contributions & distributions ---
    if unique_dates:
        first_date = sorted(unique_dates)[0]
        last_date  = sorted(unique_dates)[-1]

        contrib = rng.uniform(200_000, 500_000)
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        first_date,
            "account":     COA["CASH"],
            "debit":       contrib,
            "credit":      0.0,
            "description": "Owner contribution",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        first_date,
            "account":     COA["OWNER_CONTRIBUTIONS"],
            "debit":       0.0,
            "credit":      contrib,
            "description": "Owner equity contribution",
        })
        je_counter += 1

        dist = rng.uniform(50_000, 150_000)
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        last_date,
            "account":     COA["OWNER_DISTRIBUTIONS"],
            "debit":       dist,
            "credit":      0.0,
            "description": "Owner distribution",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        last_date,
            "account":     COA["CASH"],
            "debit":       0.0,
            "credit":      dist,
            "description": "Cash paid to owner",
        })
        je_counter += 1

    # --- Taxes & retained earnings close ---
    gl_final = pd.DataFrame(gl_records)

    total_revenue  = gl_final[gl_final["account"].isin([COA["REVENUE_FLAGSHIP"], COA["REVENUE_OTHER"]])]["credit"].sum()
    total_cogs     = gl_final[gl_final["account"] == COA["COGS"]]["debit"].sum()
    total_gna      = gl_final[gl_final["account"] == COA["GNA_EXPENSE"]]["debit"].sum()
    total_dep      = gl_final[gl_final["account"] == COA["DEPRECIATION_EXPENSE"]]["debit"].sum()
    total_interest = gl_final[gl_final["account"] == COA["INTEREST_EXPENSE"]]["debit"].sum()

    pretax_income = total_revenue - total_cogs - total_gna - total_dep - total_interest
    taxes         = max(0, pretax_income * tax_rate)
    net_income    = pretax_income - taxes

    if not gl_final.empty:
        end_date = gl_final["date"].max()
        # Tax expense & taxes payable
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        end_date,
            "account":     COA["GNA_EXPENSE"],
            "debit":       taxes,
            "credit":      0.0,
            "description": "Income tax expense",
        })
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        end_date,
            "account":     COA["TAXES_PAYABLE"],
            "debit":       0.0,
            "credit":      taxes,
            "description": "Taxes payable",
        })
        je_counter += 1

        # Close net income to retained earnings
        gl_records.append({
            "je_id":       f"JE-{je_counter:07d}",
            "date":        end_date,
            "account":     COA["RETAINED_EARNINGS"],
            "debit":       0.0,
            "credit":      net_income,
            "description": "Close net income to retained earnings",
        })

    return pd.DataFrame(gl_records)