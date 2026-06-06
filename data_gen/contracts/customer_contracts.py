#  =============================================================================
#  FILE NAME: customer_contracts.py
#  PURPOSE: Generates synthetic B2B customer contracts with realistic commercial
#  terms, renewal cycles, churn risk, committed volumes, and pricing.
#  USER-DEFINED FUNCTION: generate_customer_contracts
#  =============================================================================

import numpy as np
import pandas as pd
from datetime import timedelta


SEASONALITY_PROFILES = {
    "flat":      [1.00] * 12,
    "q4_peak":   [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.10, 1.15, 1.20, 1.40, 1.60, 1.80],
    "summer":    [1.20, 1.25, 1.30, 1.10, 1.00, 0.95, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15],
    "winter":    [1.40, 1.35, 1.20, 1.00, 0.90, 0.85, 0.80, 0.85, 0.90, 1.00, 1.10, 1.25],
}


def generate_customer_contracts(
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    n_contracts_per_customer: int = 2,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic customer contracts linking customers to products with
    realistic commercial terms and renewal/churn behavior.
    """

    rng = np.random.default_rng(random_state)

    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["sku_id"].tolist()

    contracts = []

    for cust_id in customer_ids:

        for _ in range(n_contracts_per_customer):

            contract_id = f"CONTRACT-{cust_id}-{rng.integers(1000, 9999)}"
            product_id = rng.choice(product_ids)

            # Contract duration
            start_year = rng.choice([2024, 2025, 2026])
            start_month = rng.integers(1, 13)
            start_date = pd.Timestamp(start_year, start_month, 1)

            duration_months = rng.integers(12, 36)
            end_date = start_date + pd.DateOffset(months=int(duration_months))

            # Commercial terms
            annual_volume = rng.uniform(5_000, 250_000)
            price_per_unit = rng.uniform(10, 250)

            # Renewal / churn behavior
            renewal_probability = rng.uniform(0.55, 0.95)
            churn_probability = 1 - renewal_probability

            # Pricing floors
            price_floor = price_per_unit * rng.uniform(0.80, 0.95)
            discount_rate = rng.uniform(0.00, 0.20)

            # Seasonality
            seasonality_key = rng.choice(list(SEASONALITY_PROFILES.keys()))
            seasonality_profile = SEASONALITY_PROFILES[seasonality_key]

            contracts.append({
                "contract_id": contract_id,
                "customer_id": cust_id,
                "product_id": product_id,
                "start_date": start_date,
                "end_date": end_date,
                "annual_volume": round(annual_volume, 2),
                "price_per_unit": round(price_per_unit, 2),
                "price_floor": round(price_floor, 2),
                "discount_rate": round(discount_rate, 3),
                "renewal_probability": round(renewal_probability, 3),
                "churn_probability": round(churn_probability, 3),
                "seasonality_key": seasonality_key,
                "seasonality_profile": seasonality_profile,
            })

    return pd.DataFrame(contracts)