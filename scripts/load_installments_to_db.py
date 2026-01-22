from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# ---------- CONFIG ----------
DB_URL = "postgresql+psycopg2://hc:hc_password@localhost:5432/homecredit"
IN_PATH = Path("data/processed/installments_agg.parquet")
TABLE_NAME = "stg_installments_agg"
SCHEMA = "mart"


def main() -> None:
    df = pd.read_parquet(IN_PATH)

    engine = create_engine(DB_URL)

    df.to_sql(
        TABLE_NAME,
        engine,
        schema=SCHEMA,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f"✅ installments_agg loaded into {SCHEMA}.{TABLE_NAME}")
    print(df.head())


if __name__ == "__main__":
    main()
