#  =============================================================================
#  FILE NAME: abc_costing.py
#  PURPOSE: Generates 100 producsts across several categories. Includes five
#  ABC drivers as shown in the COST_POOLS dict object.
#  User-defined fuction: generate_abc_costing
#  =============================================================================

COST_POOLS = { "machine_overhead":   "machine_hours",
               "labor_overhead":     "labor_hours",
               "setup_overhead":     "setups",
               "material_handling":  "material_moves",
               "quality_inspection": "inspections" }

def generate_abc_costing(products_df: pd.DataFrame,
                         random_state: int = 42) -> pd.DataFrame:
    """
    Generate ABC costing data for each SKU based on cost pools and cost drivers.
    Designed for Colab development and AWS productionization.
    """
    rng = np.random.default_rng(random_state)
    n = len(products_df)

    # --- Generate driver quantities per unit ---
    driver_data = {
        "machine_hours":  rng.uniform(0.1,   2.5, size=n),
        "labor_hours":    rng.uniform(0.05,  1.8, size=n),
        "setups":         rng.uniform(0.01, 0.20, size=n),
        "material_moves": rng.uniform(0.5,   5.0, size=n),
        "inspections":    rng.uniform(0.01, 0.10, size=n)  }

    # Flagship products consume more resources
    flagship_mask = products_df["is_flagship"].values
    for key in driver_data:
        driver_data[key][flagship_mask] *= rng.uniform(1.2, 1.6)

    driver_df = pd.DataFrame(driver_data)

    # --- Generate total cost pool amounts ---
    cost_pool_amounts = {
        "machine_overhead":   rng.uniform(200_000, 600_000),
        "labor_overhead":     rng.uniform(150_000, 450_000),
        "setup_overhead":     rng.uniform( 80_000, 200_000),
        "material_handling":  rng.uniform( 50_000, 150_000),
        "quality_inspection": rng.uniform( 40_000, 120_000) }

    # --- Compute overhead rates ---
    overhead_rates = {}
    for pool, driver in COST_POOLS.items():
        total_driver_qty = driver_df[driver].sum()
        overhead_rates[pool] = cost_pool_amounts[pool] / total_driver_qty

    # --- Compute unit overhead cost per SKU ---
    overhead_allocations = {}
    for pool, driver in COST_POOLS.items():
        overhead_allocations[f"{pool}_unit_cost"] = (
            driver_df[driver] * overhead_rates[pool]
        )

    overhead_df = pd.DataFrame(overhead_allocations)

    # --- Total ABC overhead per unit ---
    overhead_df["abc_overhead_unit_cost"] = overhead_df.sum(axis=1)

    # --- Merge with product master ---
    result = pd.concat([products_df.reset_index(drop=True),
                        driver_df,
                        overhead_df], axis=1)

    # --- Final standard cost (material + labor + overhead + ABC overhead) ---
    result["abc_standard_cost"] = (
          result["unit_cost_material"]
        + result["unit_cost_labor"]
        + result["unit_cost_overhead"]
        + result["abc_overhead_unit_cost"]
    ).round(2)

    return result, overhead_rates, cost_pool_amounts