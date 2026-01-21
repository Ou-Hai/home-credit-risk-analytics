from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# ---------- CONFIG ----------
DB_URL = "postgresql+psycopg2://hc:hc_password@localhost:5432/homecredit"

DATA_DIR = Path("data/processed")
APP_TRAIN_PATH = DATA_DIR / "application_train_clean.parquet"
APP_TEST_PATH = DATA_DIR / "application_test_clean.parquet"
PREV_APP_PATH = DATA_DIR / "previous_application_clean.parquet"


# ---------- HELPERS ----------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase columns to match our mart table definitions."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def safe_replace_inf(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df


def ensure_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Keep only cols that exist; add missing cols as NaN."""
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    return df[cols]


# ---------- MAIN ----------
def main() -> None:
    engine = create_engine(DB_URL, hide_parameters=True)

    # ========== 1) LOAD fact_application ==========
    df_train = pd.read_parquet(APP_TRAIN_PATH)
    df_test = pd.read_parquet(APP_TEST_PATH)

    df_train = safe_replace_inf(normalize_columns(df_train))
    df_test = safe_replace_inf(normalize_columns(df_test))

    
    if "target" not in df_test.columns:
        df_test["target"] = np.nan

    df_app = pd.concat([df_train, df_test], ignore_index=True)

    fact_app_cols = [
        "sk_id_curr",
        "target",
        "name_contract_type",
        "amt_income_total",
        "amt_credit",
        "amt_annuity",
        "amt_goods_price",
        "days_birth",
        "days_employed",
        "flag_own_car",
        "flag_own_realty",
        "cnt_children",
        "region_population_relative",
        "ext_source_1",
        "ext_source_2",
        "ext_source_3",
    ]
    df_fact_application = ensure_columns(df_app, fact_app_cols)
    # --- coerce booleans to real True/False/NULL for Postgres ---
    yn_map = {"Y": True, "N": False, "y": True, "n": False}
    for col in ["flag_own_car", "flag_own_realty"]:
        df_fact_application[col] = (
        df_fact_application[col]
        .astype("string")
        .str.strip()
        .map(yn_map)
        .astype("boolean")
    )
    
    if "target" in df_fact_application.columns:
        df_fact_application["target"] = (
        pd.to_numeric(df_fact_application["target"], errors="coerce")
        .map({0: False, 1: True})
        .astype("boolean")
    )

    # ========== 2) BUILD dim_customer ==========
    dim_cols = [
        "sk_id_curr",
        "code_gender",
        "name_education_type",
        "name_income_type",
        "occupation_type",
        "organization_type",
        "name_family_status",
        "name_housing_type",
        "cnt_children",
        "region_population_relative",
    ]
    df_dim_customer = ensure_columns(df_app, dim_cols).drop_duplicates(subset=["sk_id_curr"])

    # ========== 3) BUILD fact_previous_loans (AGG from previous_application_clean) ==========
    df_prev = pd.read_parquet(PREV_APP_PATH)
    df_prev = safe_replace_inf(normalize_columns(df_prev))

   
    prev_need = [
        "sk_id_curr",
        "name_contract_status",
        "amt_credit",
        "amt_annuity",
        "days_decision",
    ]
    df_prev_base = ensure_columns(df_prev, prev_need)

   
    g = df_prev_base.groupby("sk_id_curr", dropna=False)

    prev_app_cnt = g.size().rename("prev_app_cnt")

 
    status = df_prev_base["name_contract_status"].astype("string")
    df_prev_base["is_approved"] = (status == "Approved").astype("int")
    df_prev_base["is_refused"] = (status == "Refused").astype("int")

    g2 = df_prev_base.groupby("sk_id_curr", dropna=False)
    prev_approved_cnt = g2["is_approved"].sum().rename("prev_approved_cnt")
    prev_refused_cnt = g2["is_refused"].sum().rename("prev_refused_cnt")

    prev_approved_rate = (prev_approved_cnt / prev_app_cnt).replace([np.inf, -np.inf], np.nan).rename("prev_approved_rate")

    prev_amt_credit_mean = g2["amt_credit"].mean().rename("prev_amt_credit_mean")
    prev_amt_credit_max = g2["amt_credit"].max().rename("prev_amt_credit_max")
    prev_amt_annuity_mean = g2["amt_annuity"].mean().rename("prev_amt_annuity_mean")
    prev_days_decision_min = g2["days_decision"].min().rename("prev_days_decision_min")

    df_fact_prev = pd.concat(
        [
            prev_app_cnt,
            prev_approved_cnt,
            prev_refused_cnt,
            prev_approved_rate,
            prev_amt_credit_mean,
            prev_amt_credit_max,
            prev_amt_annuity_mean,
            prev_days_decision_min,
        ],
        axis=1,
    ).reset_index()

 
    bureau_inst_cols = [
        "bureau_credit_cnt",
        "bureau_active_cnt",
        "bureau_closed_cnt",
        "bureau_sum_debt",
        "bureau_sum_overdue",
        "bureau_max_overdue",
        "bureau_credit_day_overdue_max",
        "inst_pay_cnt",
        "inst_late_cnt",
        "inst_late_rate",
        "inst_days_late_mean",
        "inst_days_late_max",
        "inst_amt_payment_sum",
        "inst_payment_ratio_mean",
    ]
    for c in bureau_inst_cols:
        if c not in df_fact_prev.columns:
            df_fact_prev[c] = np.nan

    # ========== 4) LOAD INTO POSTGRES ==========
    with engine.begin() as conn:
       
        conn.execute(text("TRUNCATE mart.fact_previous_loans, mart.dim_customer, mart.fact_application;"))

 
    df_fact_application.to_sql("fact_application", engine, schema="mart", if_exists="append", index=False, method="multi", chunksize=5000)
    df_dim_customer.to_sql("dim_customer", engine, schema="mart", if_exists="append", index=False, method="multi", chunksize=5000)
    df_fact_prev.to_sql("fact_previous_loans", engine, schema="mart", if_exists="append", index=False, method="multi", chunksize=5000)

    # ========== 5) QUICK CHECK ==========
    with engine.begin() as conn:
        res = conn.execute(text("""
            SELECT 'fact_application' AS t, COUNT(*) AS n FROM mart.fact_application
            UNION ALL SELECT 'dim_customer', COUNT(*) FROM mart.dim_customer
            UNION ALL SELECT 'fact_previous_loans', COUNT(*) FROM mart.fact_previous_loans
            ORDER BY t;
        """)).fetchall()
        print("Row counts:")
        for r in res:
            print(r)


if __name__ == "__main__":
    main()