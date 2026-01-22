from pathlib import Path
import pandas as pd
import numpy as np

# ---------- PATHS ----------
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

# ---------- LOAD ----------
bureau = pd.read_csv(RAW_DIR / "bureau.csv")

# ---------- CLEAN ----------
bureau = bureau.copy()
bureau.columns = bureau.columns.str.lower()

cols = [
    "sk_id_curr",
    "sk_id_bureau",
    "credit_active",
    "amt_credit_sum_debt",
    "amt_credit_sum_overdue",
    "amt_credit_max_overdue",
]
bureau = bureau[cols]

# ---------- AGGREGATE ----------
bureau_agg = (
    bureau
    .groupby("sk_id_curr")
    .agg(
        bureau_credit_cnt=("sk_id_bureau", "count"),
        bureau_active_cnt=("credit_active", lambda x: (x == "Active").sum()),
        bureau_closed_cnt=("credit_active", lambda x: (x == "Closed").sum()),
        bureau_sum_debt=("amt_credit_sum_debt", "sum"),
        bureau_sum_overdue=("amt_credit_sum_overdue", "sum"),
        bureau_max_overdue=("amt_credit_max_overdue", "max"),
    )
    .reset_index()
)

# ---------- OPTIONAL: replace NaN with 0 for sums ----------
num_cols = [
    "bureau_sum_debt",
    "bureau_sum_overdue",
    "bureau_max_overdue",
]
bureau_agg[num_cols] = bureau_agg[num_cols].fillna(0)

# ---------- SAVE ----------
OUT_DIR.mkdir(exist_ok=True)
out_path = OUT_DIR / "bureau_agg.parquet"
bureau_agg.to_parquet(out_path, index=False)

print(f"✅ Bureau aggregation saved to {out_path}")
print(bureau_agg.head())
