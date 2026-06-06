#  =============================================================================
#  FILE NAME: vendors.py
#  PURPOSE: Generates synthetic vendor master data with realistic supply-chain
#           and payment attributes.
#  USER-DEFINED FUNCTION: generate_vendors
#  =============================================================================

import numpy as np
import pandas as pd


def generate_vendors(
    n_vendors: int = 20,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic vendor master data with lead times, reliability, and payment terms.
    """

    rng = np.random.default_rng(random_state)

    vendor_ids = [f"VENDOR-{i:03d}" for i in range(1, n_vendors + 1)]
    names = [f"Vendor {i}" for i in range(1, n_vendors + 1)]

    # Lead time in days (shorter for more reliable vendors)
    base_lead_time = rng.integers(5, 45, size=n_vendors)
    reliability_score = rng.uniform(0.6, 0.99, size=n_vendors)
    lead_time_days = (base_lead_time * (1.2 - reliability_score)).round().astype(int)

    # Payment terms (Net 15–90)
    payment_terms_days = rng.integers(15, 90, size=n_vendors)

    # On-time delivery %
    on_time_delivery_pct = rng.uniform(0.80, 0.99, size=n_vendors)

    # Minimum order quantity
    min_order_qty = rng.integers(10, 500, size=n_vendors)

    df = pd.DataFrame({
        "vendor_id": vendor_ids,
        "name": names,
        "lead_time_days": lead_time_days,
        "payment_terms_days": payment_terms_days,
        "reliability_score": reliability_score.round(3),
        "on_time_delivery_pct": on_time_delivery_pct.round(3),
        "min_order_qty": min_order_qty.astype(int),
    })

    return df
