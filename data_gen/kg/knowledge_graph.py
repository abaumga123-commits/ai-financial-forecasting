# =============================================================================
# FILE NAME: knowledge_graph.py
# PURPOSE: Build a simple knowledge graph from core data_gen entities:
# customers, contracts, macro factors, and financial statements.
# User-defined function: build_knowledge_graph
# =============================================================================

# Dependencies needed:
import pandas as pd
from typing import Dict, Any


def build_knowledge_graph(
    customers_df: pd.DataFrame,
    contracts_df: pd.DataFrame,
    macro_df:     pd.DataFrame,
    budget_is_df: pd.DataFrame,
    customer_budget_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Build a lightweight knowledge graph representation as dictionaries of nodes
    and edges. This is meant for LLM reasoning, feature engineering, and
    exploratory analysis—not for heavy graph DB workloads.

    Parameters
    ----------
    customers_df : pd.DataFrame
        Output of generate_customers().
    contracts_df : pd.DataFrame
        Output of generate_customer_contracts().
    macro_df : pd.DataFrame
        Output of generate_macro_factors().
    budget_is_df : pd.DataFrame
        Output of generate_budget_income_statement().
    customer_budget_df : pd.DataFrame
        Output of allocate_budget_to_customers().

    Returns
    -------
    Dict[str, Any]
        A dictionary with:
        - "nodes": dict of node tables
        - "edges": dict of edge tables
    """

    nodes = { "customers": customers_df.copy(),
              "contracts": contracts_df.copy(),
              "macro":     macro_df.copy(),
              "budget_income_statement": budget_is_df.copy(),
              "customer_budget": customer_budget_df.copy() }

    # --- Edges ---

    # Customer ↔ Contract
    edges_customer_contract = contracts_df[["customer_id", "contract_start", "contract_end"]].copy()
    edges_customer_contract.rename(columns={
        "customer_id":    "from_customer_id",
        "contract_start": "contract_start",
        "contract_end":   "contract_end",
    }, inplace=True)

    # Customer ↔ Budget
    edges_customer_budget = customer_budget_df[["customer_id", "period", "budgeted_revenue"]].copy()
    edges_customer_budget.rename(columns={
        "customer_id":      "from_customer_id",
        "period":           "period",
        "budgeted_revenue": "to_budgeted_revenue",
    }, inplace=True)

    # Macro ↔ Budget (by date/period alignment)
    macro_period = macro_df.copy()
    macro_period["period"] = macro_period["date"].dt.to_period("M").astype(str)

    edges_macro_budget = (
        macro_period.merge(
            budget_is_df[["period", "section", "label", "amount"]],
            on="period",
            how="inner"
        )
    )

    edges = {
        "customer_contract": edges_customer_contract,
        "customer_budget": edges_customer_budget,
        "macro_budget": edges_macro_budget,
    }

    return {
        "nodes": nodes,
        "edges": edges,
    }