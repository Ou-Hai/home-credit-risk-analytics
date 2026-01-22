import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# ---------- CONFIG ----------
DB_URL = "postgresql+psycopg2://hc:hc_password@localhost:5432/homecredit"
DATA_PATH = Path("data/processed/bureau_agg.parquet")

# ---------- LOAD ----------
df = pd.read_parquet(DATA_PATH)

# ---------- CONNECT ----------
engine = create_engine(DB_URL)

# ---------- WRITE ----------
df.to_sql(
    name="stg_bureau_agg",
    con=engine,
    schema="mart",
    if_exists="replace",
    index=False,
)

print("✅ bureau_agg loaded into mart.stg_bureau_agg")
print(df.head())
