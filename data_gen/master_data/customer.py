# =============================================================================
# FILE NAME: customer.py
# PURPOSE: Generates a synthetic customer master dataset for use in
# revenue simulation, forecasting, and knowledge graph linking. The
# revenue_potential field shows the granular bugdeted revenue which is aggregate
# in the Income Statement.
# User-defined function: generate_customers
# =============================================================================

import numpy as np
import pandas as pd


REGIONS = [ "Northeast", "Midwest", "South", "West",
            "Canada", "Europe", "Asia-Pacific" ]

INDUSTRIES = [ "Retail", "Manufacturing", "Healthcare", "Finance",
               "Technology", "Logistics", "Hospitality", "Energy" ]

CUSTOMER_TIERS = ["Enterprise", "Mid-Market", "SMB"]


def generate_customers(
    n_customers: int = 500,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Generate a synthetic customer master dataset with realistic attributes:
    - region
    - industry
    - customer tier
    - annual revenue potential
    - price sensitivity
    - churn risk
    - credit rating
    - payment behavior

    Parameters
    ----------
    n_customers : int
        Number of customers to generate.
    random_state : int
        RNG seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Customer master dataset.
    """
    rng = np.random.default_rng(random_state)

    customer_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]

    # --- Core attributes ---
    regions     = rng.choice(REGIONS,     size=n_customers)
    industries  = rng.choice(INDUSTRIES,  size=n_customers)
    tiers       = rng.choice(CUSTOMER_TIERS, size=n_customers, p=[0.15, 0.35, 0.50])

    # --- Revenue potential (higher for enterprise, lower for SMB) ---
    revenue_potential = np.zeros(n_customers)
    for i, tier in enumerate(tiers):
        if tier == "Enterprise":
            revenue_potential[i] = rng.uniform(500_000, 3_000_000)
        elif tier == "Mid-Market":
            revenue_potential[i] = rng.uniform(150_000, 800_000)
        else:  # SMB
            revenue_potential[i] = rng.uniform(20_000, 150_000)

    # --- Price sensitivity (elasticity) ---
    price_sensitivity = rng.uniform(-2.5, -0.3, size=n_customers)

    # --- Churn risk (Enterprise lowest, SMB highest) ---
    churn_risk = np.zeros(n_customers)
    for i, tier in enumerate(tiers):
        if tier == "Enterprise":
            churn_risk[i] = rng.uniform(0.01, 0.05)
        elif tier == "Mid-Market":
            churn_risk[i] = rng.uniform(0.03, 0.10)
        else:
            churn_risk[i] = rng.uniform(0.05, 0.20)

    # --- Credit rating (simple synthetic score) ---
    credit_rating = rng.normal(loc=680, scale=40, size=n_customers).clip(550, 800)

    # --- Payment behavior (days sales outstanding) ---
    dso = rng.normal(loc=38, scale=10, size=n_customers).clip(10, 90)

    df = pd.DataFrame({
        "customer_id":        customer_ids,
        "region":             regions,
        "industry":           industries,
        "customer_tier":      tiers,
        "revenue_potential":  revenue_potential.round(2),
        "price_sensitivity":  price_sensitivity.round(3),
        "churn_risk":         churn_risk.round(3),
        "credit_rating":      credit_rating.astype(int),
        "avg_dso_days":       dso.round(1),
    })

    return df