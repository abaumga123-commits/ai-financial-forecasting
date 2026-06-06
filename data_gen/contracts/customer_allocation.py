# =============================================================================
# FILE NAME: customer_allocation.py
# PURPOSE: Allocate budgeted revenue across customers based on revenue_potential.
# User-defined function: allocate_budget_to_customers
# =============================================================================

# Dependencies needed:
import numpy as np
import pandas as pd


def allocate_budget_to_customers(
    customers_df: pd.DataFrame,
    budget_is_df: pd.DataFrame,
    period_col: str = "period"
) -> pd.DataFrame:
    """
    Allocate budgeted revenue across customers proportionally to their
    revenue_potential. Works for annual, quarterly, or monthly budgets.

    Parameters
    ----------
    customers_df : pd.DataFrame
        Output of generate_customers(), must include:
        - customer_id
        - revenue_potential

    budget_is_df : pd.DataFrame
        Output of generate_budget_income_statement(), must include:
        - period
        - section == "Revenue"
        - label == "Total revenue"
        - amount

    period_col : str
        Column name representing the budget period (default: "period").

    Returns
    -------
    pd.DataFrame
        Customer-level budget allocation with columns:
        - customer_id
        - period
        - revenue_potential
        - allocation_weight
        - budgeted_revenue
    """

    # --- Extract total revenue by period ---
    budget_rev = (
        budget_is_df[
            (budget_is_df["section"] == "Revenue") &
            (budget_is_df["label"]   == "Total revenue")
        ][[period_col, "amount"]]
        .rename(columns={"amount": "total_budget_revenue"})
    )

    # --- Compute weights ---
    customers = customers_df.copy()
    customers["revenue_potential"] = customers["revenue_potential"].astype(float)

    total_potential = customers["revenue_potential"].sum()
    customers["allocation_weight"] = customers["revenue_potential"] / total_potential

    # --- Cross-join customers × periods ---
    customers["_tmp"]  = 1
    budget_rev["_tmp"] = 1

    alloc = customers.merge(budget_rev, on="_tmp").drop(columns="_tmp")

    # --- Allocate revenue ---
    alloc["budgeted_revenue"] = ( alloc["allocation_weight"] * alloc["total_budget_revenue"] )

    return alloc[ ["customer_id", period_col, "revenue_potential",
         "allocation_weight", "budgeted_revenue"] ]