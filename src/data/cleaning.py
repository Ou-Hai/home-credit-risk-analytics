from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


# -------------------------
# Utils
# -------------------------
def ensure_columns_exist(df: pd.DataFrame, cols: Iterable[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")


# -------------------------
# Previous application: placeholder handling
# -------------------------
def replace_placeholder_with_nan(
    df: pd.DataFrame,
    cols: Iterable[str],
    placeholder: float | int = 365243,
    add_indicator: bool = True,
    indicator_suffix: str = "_is_placeholder",
) -> pd.DataFrame:
    """
    Replace Home Credit placeholder value (e.g., 365243) with NaN for specified columns.
    Optionally add indicator columns that flag placeholder occurrences.
    """
    df = df.copy()
    ensure_columns_exist(df, cols)

    for col in cols:
        if add_indicator:
            df[f"{col}{indicator_suffix}"] = (df[col] == placeholder).astype("int8")
        df[col] = df[col].replace(placeholder, np.nan)

    return df


def clean_previous_application(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean previous_application table:
    - Replace 365243 placeholder in DAYS_* columns with NaN + add indicators.
    """
    placeholder_cols = [
        "DAYS_FIRST_DRAWING",
        "DAYS_FIRST_DUE",
        "DAYS_LAST_DUE_1ST_VERSION",
        "DAYS_LAST_DUE",
        "DAYS_TERMINATION",
    ]

    # Only keep columns that exist (defensive)
    cols = [c for c in placeholder_cols if c in df.columns]

    out = replace_placeholder_with_nan(df, cols=cols, placeholder=365243, add_indicator=True)
    return out


# -------------------------
# Application: age + outliers (income/credit)
# -------------------------
def add_age_features(
    df: pd.DataFrame,
    days_birth_col: str = "DAYS_BIRTH",
    age_col: str = "AGE_YEARS",
    flag_col: str = "AGE_OUTLIER",
    min_age: float = 18.0,
    max_age: float = 100.0,
) -> pd.DataFrame:
    """
    Add AGE_YEARS from DAYS_BIRTH and flag out-of-range ages.
    Out-of-range AGE_YEARS will be set to NaN; flag retained.
    """
    df = df.copy()
    ensure_columns_exist(df, [days_birth_col])

    df[age_col] = (-df[days_birth_col] / 365.25).round(1)
    df[flag_col] = ((df[age_col] < min_age) | (df[age_col] > max_age)).astype("int8")
    df.loc[df[flag_col] == 1, age_col] = np.nan
    return df


def winsorize_clip(
    df: pd.DataFrame,
    col: str,
    lower_q: float = 0.01,
    upper_q: float = 0.99,
) -> pd.DataFrame:
    """
    Clip a numeric column to [q_lower, q_upper] quantiles (winsorization).
    """
    df = df.copy()
    ensure_columns_exist(df, [col])

    lo = df[col].quantile(lower_q)
    hi = df[col].quantile(upper_q)
    df[col] = df[col].clip(lo, hi)
    return df


def clean_income(
    df: pd.DataFrame,
    income_col: str = "AMT_INCOME_TOTAL",
    flag_col: str = "INCOME_OUTLIER",
    lower_q: float = 0.01,
    upper_q: float = 0.99,
) -> pd.DataFrame:
    """
    Income cleaning:
    - Flag and set NaN for income <= 0
    - Clip extreme values using quantiles
    """
    df = df.copy()
    ensure_columns_exist(df, [income_col])

    df[flag_col] = (df[income_col] <= 0).astype("int8")
    df.loc[df[flag_col] == 1, income_col] = np.nan

    lo = df[income_col].quantile(lower_q)
    hi = df[income_col].quantile(upper_q)
    df[income_col] = df[income_col].clip(lo, hi)

    return df


def clean_credit_amount(
    df: pd.DataFrame,
    credit_col: str = "AMT_CREDIT",
    flag_col: str = "CREDIT_OUTLIER",
    lower_q: float = 0.01,
    upper_q: float = 0.99,
) -> pd.DataFrame:
    """
    Credit amount cleaning:
    - Flag and set NaN for credit <= 0
    - Clip extreme values using quantiles
    """
    df = df.copy()
    ensure_columns_exist(df, [credit_col])

    df[flag_col] = (df[credit_col] <= 0).astype("int8")
    df.loc[df[flag_col] == 1, credit_col] = np.nan

    lo = df[credit_col].quantile(lower_q)
    hi = df[credit_col].quantile(upper_q)
    df[credit_col] = df[credit_col].clip(lo, hi)

    return df


def clean_application(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal Day-3 application cleaning:
    - Add AGE_YEARS + AGE_OUTLIER
    - Clean AMT_INCOME_TOTAL (flag + clip)
    - Clean AMT_CREDIT (flag + clip)
    """
    out = df.copy()
    out = add_age_features(out)
    out = clean_income(out)
    out = clean_credit_amount(out)
    out = cast_dtypes_application(out)
    
    return out


def cast_dtypes_application(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast dtypes for application table:
    - binary flags -> int8
    - identifiers -> nullable Int64
    - object columns -> category
    """
    df = df.copy()

    # IDs
    if "SK_ID_CURR" in df.columns:
        df["SK_ID_CURR"] = pd.to_numeric(df["SK_ID_CURR"], errors="coerce").astype("Int64")

    # TARGET
    if "TARGET" in df.columns:
        df["TARGET"] = df["TARGET"].astype("int8")

    # Binary flags
    flag_cols = [c for c in df.columns if c.startswith("FLAG_")]
    for c in flag_cols:
        vals = df[c].dropna().unique()
        if set(vals).issubset({0, 1}):
            df[c] = df[c].astype("int8")

    # Engineered flags
    for c in ["AGE_OUTLIER", "INCOME_OUTLIER", "CREDIT_OUTLIER"]:
        if c in df.columns:
            df[c] = df[c].astype("int8")

    # Object → category
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype("category")

    return df
