#  =============================================================================
#  FILE NAME: macro.py
#  PURPOSE: Generates synthetic macroeconomic indicators for use as exogenous
#  regressors in forecasting and financial modeling.
#  USER-DEFINED FUNCTION: generate_macro_factors
#  =============================================================================

import numpy as np
import pandas as pd


def generate_macro_factors(
    start_date: str = "2022-01-01",
    n_months: int = 36,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic monthly macroeconomic indicators:
    - CPI inflation (YoY %)
    - Unemployment rate (%)
    - GDP growth (YoY %)
    - Consumer sentiment index (0–100)
    - Interest rates (short-term + long-term)
    - FX index (broad USD strength)
    - Industrial production index
    """

    rng = np.random.default_rng(seed)

    dates = pd.date_range(start=start_date, periods=n_months, freq="MS")

    # --- CPI inflation (YoY %) ---
    cpi = np.cumsum(rng.normal(loc=0.15, scale=0.10, size=n_months)) + 3.0
    cpi = np.clip(cpi, 1.0, 8.0)

    # --- Unemployment rate (%) ---
    unemployment = 4.5 + rng.normal(loc=0.0, scale=0.3, size=n_months)
    unemployment = np.clip(unemployment, 3.0, 8.0)

    # --- GDP growth (YoY %) ---
    gdp_growth = 2.0 + rng.normal(loc=0.0, scale=0.5, size=n_months)

    # --- Consumer sentiment index (0–100) ---
    sentiment = 70 + np.cumsum(rng.normal(loc=0.0, scale=1.5, size=n_months))
    sentiment = np.clip(sentiment, 40, 110)

    # --- Interest rates ---
    short_rate = 1.0 + np.cumsum(rng.normal(loc=0.02, scale=0.05, size=n_months))
    long_rate  = 2.0 + np.cumsum(rng.normal(loc=0.01, scale=0.03, size=n_months))

    short_rate = np.clip(short_rate, 0.0, 8.0)
    long_rate  = np.clip(long_rate, 1.0, 10.0)

    # --- FX index (USD strength) ---
    fx_index = 100 + np.cumsum(rng.normal(loc=0.0, scale=0.8, size=n_months))

    # --- Industrial production index ---
    ip_index = 105 + np.cumsum(rng.normal(loc=0.0, scale=0.6, size=n_months))

    df = pd.DataFrame({
        "date": dates,
        "cpi_inflation_yoy": cpi.round(2),
        "unemployment_rate": unemployment.round(2),
        "gdp_growth_yoy": gdp_growth.round(2),
        "consumer_sentiment": sentiment.round(1),
        "short_term_rate": short_rate.round(2),
        "long_term_rate": long_rate.round(2),
        "fx_index": fx_index.round(2),
        "industrial_production_index": ip_index.round(2),
    })

    return df