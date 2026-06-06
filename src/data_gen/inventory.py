#  =============================================================================
#  FILE NAME: inventory.py
#  PURPOSE: Generates an inventory subledger beginning Jan 1, 2022 to initialize
#  beginning inventory stock, track purchases, and track inventory outflow.
#  Ledger keeps records on date, sku num, quantity, unit cost, and other artifacts.
#  User-defined fuction: generate_inventory_subledger
#  =============================================================================

# Dependencies needed:
import numpy  as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple

def generate_inventory_subledger(
    products_abc_df: pd.DataFrame,
    start_date: str = "2022-01-01",
    n_days: int = 365,
    location_id: str = "WH-001",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic inventory subledger with receipts, issues, and adjustments
    using weighted-average cost. Input is the products + ABC costing dataframe.
    """
    rng = np.random.default_rng(random_state)
    start_dt = datetime.fromisoformat(start_date)

    records = []
    txn_counter = 1

    # --- Demand model ---
    n = len(products_abc_df)
    is_flagship = products_abc_df["is_flagship"].values

    # Base demand: flagship SKUs have higher velocity
    base_demand = rng.uniform(2, 15, size=n)
    base_demand[is_flagship] *= rng.uniform(1.5, 3.0)

    # --- Initial inventory ---
    init_inventory = (products_abc_df["safety_stock_units"].values
                      * rng.uniform(0.8, 1.4, size=n)).astype(int)

    # State tracking
    on_hand  = init_inventory.astype(float)
    avg_cost = products_abc_df["abc_standard_cost"].values.astype(float)

    # Open purchase orders: (arrival_day_idx, sku_idx, qty, unit_cost)
    open_pos = []

    for day_idx in range(n_days):
        current_date = start_dt + timedelta(days=day_idx)

        # --- Process arriving POs ---
        arrivals_today = [po for po in open_pos if po[0] == day_idx]
        open_pos = [po for po in open_pos if po[0] != day_idx]

        for arrival_day, sku_idx, qty, unit_cost in arrivals_today:
            old_qty = on_hand[sku_idx]
            old_cost = avg_cost[sku_idx]

            new_qty = old_qty + qty
            new_cost = (
                (old_qty * old_cost + qty * unit_cost) / new_qty
                if new_qty > 0 else old_cost )

            on_hand[sku_idx] = new_qty
            avg_cost[sku_idx] = new_cost

            records.append({
                "txn_id":        f"TXN-{txn_counter:07d}",
                "date":          current_date.date().isoformat(),
                "sku_id":        products_abc_df.loc[sku_idx, "sku_id"],
                "location_id":   location_id,
                "txn_type":      "receipt",
                "quantity":      float(qty),
                "unit_cost":     float(unit_cost),
                "extended_cost": float(qty * unit_cost),
                "po_id":         f"PO-{arrival_day:05d}-{sku_idx:04d}",
                "so_id":         None,
            })
            txn_counter += 1

        # --- Daily demand + issues ---
        for sku_idx in range(n):
            sku = products_abc_df.loc[sku_idx, "sku_id"]
            demand_mean = base_demand[sku_idx]
            demand = max(0, rng.poisson(demand_mean))

            qty_available = on_hand[sku_idx]
            qty_issued = min(qty_available, demand)

            if qty_issued > 0:
                on_hand[sku_idx] -= qty_issued
                unit_cost = avg_cost[sku_idx]

                records.append({
                    "txn_id":        f"TXN-{txn_counter:07d}",
                    "date":          current_date.date().isoformat(),
                    "sku_id":        sku,
                    "location_id":   location_id,
                    "txn_type":      "issue",
                    "quantity":      -float(qty_issued),
                    "unit_cost":      float(unit_cost),
                    "extended_cost": -float(qty_issued * unit_cost),
                    "po_id":         None,
                    "so_id":         f"SO-{day_idx:05d}-{sku_idx:04d}",
                })
                txn_counter += 1

        # --- Reorder logic ---
        for sku_idx in range(n):
            sku_row       = products_abc_df.iloc[sku_idx]
            reorder_point = sku_row["reorder_point_units"]
            safety_stock  = sku_row["safety_stock_units"]
            lead_time     = int(sku_row["lead_time_days"])

            if on_hand[sku_idx] <= reorder_point:
                target_level = safety_stock * 2.5
                qty_to_order = max(0, int(target_level - on_hand[sku_idx]))
                if qty_to_order <= 0:
                    continue

                base_cost = sku_row["abc_standard_cost"]
                unit_cost = float(base_cost * rng.uniform(0.95, 1.05))

                arrival_day = day_idx + max(1, lead_time)
                open_pos.append((arrival_day, sku_idx, qty_to_order, unit_cost))

    return pd.DataFrame(records)