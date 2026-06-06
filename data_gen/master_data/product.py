#  =============================================================================
#  FILE NAME: product.py
#  PURPOSE: Generates 100 products across several categories. Includes 5
#  ABC drivers across 12 categories.
#  User-defined fuction: generate_products
#  =============================================================================

import numpy as np
import pandas as pd

CATEGORIES = [ "Electronics", "Home Goods", "Apparel", "Beauty",
               "Sports", "Automotive", "Office", "Toys",
               "Grocery", "Health", "Pet Supplies", "Outdoor" ]

ABC_DRIVERS = [ "machine_hours",
                "labor_hours",
                "setups",
                "material_moves",
                "inspections" ]

def generate_products(n_skus: int = 100, n_flagship: int = 8, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic product master data with realistic financial and operational attributes.
    Designed for Colab development and AWS productionization.
    """
    rng = np.random.default_rng(random_state)

    # --- SKU IDs ---
    sku_ids = [f"SKU-{i:04d}" for i in range(1, n_skus + 1)]

    # --- Flagship selection ---
    flagship_indices = set(rng.choice(n_skus, size=n_flagship, replace=False))

    # --- Categories ---
    categories = rng.choice(CATEGORIES, size=n_skus)

    # --- Vendors ---
    vendor_ids       = [f"VENDOR-{i:03d}" for i in range(1, 21)]  # 20 vendors
    primary_vendor   = rng.choice(vendor_ids, size=n_skus)
    secondary_vendor = rng.choice(vendor_ids, size=n_skus)

    # --- ABC Cost Drivers ---
    abc_drivers = rng.choice(ABC_DRIVERS, size=n_skus)

    # --- Cost Components ---
    material_cost = rng.uniform(2, 80, size=n_skus)
    labor_cost    = rng.uniform(1, 30, size=n_skus)
    overhead_cost = rng.uniform(1, 25, size=n_skus)

    # Flagship products have higher quality → higher cost
    flagship_mask = np.array([i in flagship_indices for i in range(n_skus)])
    material_cost[flagship_mask] *= 1.4
    labor_cost[flagship_mask]    *= 1.3
    overhead_cost[flagship_mask] *= 1.2

    standard_cost = material_cost + labor_cost + overhead_cost

    # --- Pricing ---
    base_price = standard_cost * rng.uniform(1.4, 2.2, size=n_skus)

    # Flagship products have premium pricing
    base_price[flagship_mask] *= 1.25

    price_elasticity = rng.uniform(-1.8, -0.4, size=n_skus)
    price_volatility = rng.uniform(0.01, 0.08, size=n_skus)

    # --- Supply Chain Attributes ---
    # Cast to float first to allow scaling, then back to int
    lead_time_days = rng.integers(5, 45, size=n_skus).astype(float)
    lead_time_days[flagship_mask] *= 0.8
    lead_time_days = lead_time_days.astype(int)

    safety_stock_units = rng.integers(20, 300, size=n_skus)
    reorder_point_units = (safety_stock_units * rng.uniform(1.2, 1.8, size=n_skus)).round().astype(int)

    # --- Shelf Life (for perishables) ---
    shelf_life_days = rng.integers(90, 720, size=n_skus)

    # --- Build DataFrame ---
    df = pd.DataFrame({
        "sku_id": sku_ids,
        "name": [f"Product {i}" for i in range(1, n_skus + 1)],
        "category":            categories,
        "is_flagship":         flagship_mask,
        "abc_cost_driver":     abc_drivers,
        "unit_cost_material":  material_cost.round(2),
        "unit_cost_labor":     labor_cost.round(2),
        "unit_cost_overhead":  overhead_cost.round(2),
        "standard_cost":       standard_cost.round(2),
        "base_price":          base_price.round(2),
        "price_elasticity":    price_elasticity.round(3),
        "price_volatility":    price_volatility.round(3),
        "lead_time_days":      lead_time_days,
        "safety_stock_units":  safety_stock_units.astype(int),
        "reorder_point_units": reorder_point_units.astype(int),
        "primary_vendor":      primary_vendor,
        "secondary_vendor":    secondary_vendor,
        "shelf_life_days":     shelf_life_days.astype(int),
    })

    return df