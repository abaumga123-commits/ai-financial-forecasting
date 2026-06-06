# =============================================================================
# FILE NAME: data_generator.py
# PURPOSE: Master orchestrator for generating the full synthetic enterprise
# dataset: customers, contracts, macro, budget, GL, financials, KG.
# User-defined function: generate_full_dataset
# =============================================================================

import pandas as pd

from src.data_gen.opening_balance_sheet import generate_opening_balance_sheet
from src.data_gen.budget_income_statement import generate_budget_income_statement
from src.data_gen.customer import generate_customers
from src.data_gen.customer_contracts import generate_customer_contracts
from src.data_gen.customer_budget_allocation import allocate_budget_to_customers
from src.data_gen.macro import generate_macro_factors
from src.data_gen.knowledge_graph import build_knowledge_graph

from src.data_gen.general_ledger import generate_general_ledger
from src.data_gen.balance_sheet import generate_balance_sheet
from src.data_gen.cash_flow import generate_cash_flow_statement
from src.data_gen.income_statement import generate_income_statement


def generate_full_dataset(
    year: int = 2022,
    n_customers: int = 500,
    seed: int = 42,
    monthly: bool = True
) -> dict:
    """
    Generate the full synthetic enterprise dataset including:
    - Opening balance sheet
    - Budgeted income statement (annual or monthly)
    - Customer master
    - Customer contracts
    - Customer-level budget allocation
    - Macroeconomic factors
    - General ledger simulation
    - Monthly financial statements
    - Knowledge graph

    Parameters
    ----------
    year : int
        Base year for budget and simulation.
    n_customers : int
        Number of customers to generate.
    seed : int
        RNG seed.
    monthly : bool
        Whether to generate monthly financial statements.

    Returns
    -------
    dict
        Dictionary containing all generated datasets.
    """

    # -------------------------------------------------------------------------
    # 1. Opening Balance Sheet
    # -------------------------------------------------------------------------
    opening_bs = generate_opening_balance_sheet(seed=seed)

    # -------------------------------------------------------------------------
    # 2. Budget Income Statement
    # -------------------------------------------------------------------------
    freq = "monthly" if monthly else "annual"
    budget_is = generate_budget_income_statement(
        year=year,
        frequency=freq,
        seed=seed
    )

    # -------------------------------------------------------------------------
    # 3. Customer Master
    # -------------------------------------------------------------------------
    customers = generate_customers(
        n_customers=n_customers,
        random_state=seed
    )

    # -------------------------------------------------------------------------
    # 4. Customer Contracts
    # -------------------------------------------------------------------------
    contracts = generate_customer_contracts(
        customers_df=customers,
        random_state=seed
    )

    # -------------------------------------------------------------------------
    # 5. Customer-Level Budget Allocation
    # -------------------------------------------------------------------------
    customer_budget = allocate_budget_to_customers(
        customers_df=customers,
        budget_is_df=budget_is
    )

    # -------------------------------------------------------------------------
    # 6. Macroeconomic Factors
    # -------------------------------------------------------------------------
    macro = generate_macro_factors(
        start_date=f"{year}-01-01",
        n_months=36,
        seed=seed
    )

    # -------------------------------------------------------------------------
    # 7. General Ledger Simulation
    # -------------------------------------------------------------------------
    gl = generate_general_ledger(
        customers_df=customers,
        contracts_df=contracts,
        customer_budget_df=customer_budget,
        macro_df=macro,
        seed=seed
    )

    # -------------------------------------------------------------------------
    # 8. Monthly Financial Statements
    # -------------------------------------------------------------------------
    monthly_is = generate_income_statement(gl)
    monthly_bs = generate_balance_sheet(gl, opening_bs)
    monthly_cf = generate_cash_flow_statement(monthly_bs)

    # -------------------------------------------------------------------------
    # 9. Knowledge Graph
    # -------------------------------------------------------------------------
    kg = build_knowledge_graph(
        customers_df=customers,
        contracts_df=contracts,
        macro_df=macro,
        budget_is_df=budget_is,
        customer_budget_df=customer_budget
    )

    # -------------------------------------------------------------------------
    # 10. Return everything
    # -------------------------------------------------------------------------
    return {
        "opening_balance_sheet": opening_bs,
        "budget_income_statement": budget_is,
        "customers": customers,
        "contracts": contracts,
        "customer_budget": customer_budget,
        "macro": macro,
        "general_ledger": gl,
        "monthly_income_statement": monthly_is,
        "monthly_balance_sheet": monthly_bs,
        "monthly_cash_flow": monthly_cf,
        "knowledge_graph": kg,
    }