from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

IN_PATH = RAW_DIR / "installments_payments.csv"
OUT_PATH = OUT_DIR / "installments_agg.parquet"


def main() -> None:
    # ---------- LOAD ----------
    inst = pd.read_csv(IN_PATH)

    # ---------- CLEAN ----------
    inst = inst.copy()
    inst.columns = inst.columns.str.lower()

    cols = [
        "sk_id_curr",
        "sk_id_prev",
        "amt_instalment",
        "amt_payment",
        "days_instalment",
        "days_entry_payment",
    ]
    inst = inst[cols]

    # ---------- FEATURE ENGINEERING ----------
    inst["late_days"] = inst["days_entry_payment"] - inst["days_instalment"]

    inst["late_flag"] = (inst["late_days"] > 0).astype("int")

    inst["payment_ratio"] = inst["amt_payment"] / inst["amt_instalment"].replace(0, np.nan)

    # ---------- AGGREGATE (to applicant grain) ----------
    agg = (
        inst.groupby("sk_id_curr")
        .agg(
            inst_pay_cnt=("sk_id_prev", "count"),
            inst_late_cnt=("late_flag", "sum"),
            inst_late_rate=("late_flag", "mean"),
            inst_days_late_mean=("late_days", lambda x: x[x > 0].mean()),
            inst_days_late_max=("late_days", lambda x: x[x > 0].max()),
            inst_amt_payment_sum=("amt_payment", "sum"),
            inst_amt_instalment_sum=("amt_instalment", "sum"),
            inst_payment_ratio_mean=("payment_ratio", "mean"),
        )
        .reset_index()
    )

    agg["inst_days_late_mean"] = agg["inst_days_late_mean"].fillna(0)
    agg["inst_days_late_max"] = agg["inst_days_late_max"].fillna(0)

    agg["inst_payment_ratio_mean"] = agg["inst_payment_ratio_mean"].fillna(0)

    # ---------- SAVE ----------
    OUT_DIR.mkdir(exist_ok=True)
    agg.to_parquet(OUT_PATH, index=False)

    print(f"✅ Installments aggregation saved to {OUT_PATH}")
    print(agg.head())


if __name__ == "__main__":
    main()
