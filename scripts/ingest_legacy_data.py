
from pathlib import Path
import os

import pandas as pd
from sqlalchemy import URL, create_engine, text
from dotenv import load_dotenv

# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

# Script: experiment/phase-0/ingest_legacy_data.py
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

load_dotenv(project_root / ".env")

data_path = (
    project_root
    / "data"
    / "raw"
    / "dynamic_supply_chain_logistics_dataset.csv"
)

# --------------------------------------------------
# 2. Database configuration
# --------------------------------------------------

db_host = os.getenv("DB_HOST", "cloud-sql-proxy")
db_port = int(os.getenv("DB_PORT", "5432"))
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

if not all([db_name, db_user, db_password]):
    raise ValueError("Missing database configuration in .env")

# --------------------------------------------------
# 3. Load the raw dataset
# --------------------------------------------------

print(f"Loading CSV from {data_path}...")

df = pd.read_csv(data_path)

print(f"Original dataset shape: {df.shape}")

# --------------------------------------------------
# 4. Map clean columns to legacy schema
# --------------------------------------------------

legacy_mapping = {
    "timestamp": "TS_UTC",
    "vehicle_gps_latitude": "V_LAT",
    "vehicle_gps_longitude": "V_LON",
    "iot_temperature": "IOT_TEMP_VAL_C",
    "cargo_condition_status": "CGO_COND_CD",
    "risk_classification": "RISK_CLS_TXT",
    "delay_probability": "DELAY_PROB_DEC",
    "port_congestion_level": "PRT_CNG_LVL",
    "route_risk_level": "RT_RSK_IDX"
}

# Validate expected source columns
missing_columns = set(legacy_mapping.keys()) - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing expected dataset columns: {missing_columns}"
    )

df_legacy = (
    df[list(legacy_mapping.keys())]
    .rename(columns=legacy_mapping)
)

df_legacy["SYS_INGEST_FLAG"] = "Y"

print(f"Transformed dataset shape: {df_legacy.shape}")

# --------------------------------------------------
# 5. Connect to GCP Cloud SQL PostgreSQL
# --------------------------------------------------

print("Connecting to GCP Cloud SQL PostgreSQL...")

connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME")
)


engine = create_engine(connection_url)

# --------------------------------------------------
# 6. Ingest data into PostgreSQL
# --------------------------------------------------

table_name = "tbl_sc_fleet_hist_raw"

print(f"Ingesting data into {table_name}...")

df_legacy.to_sql(
    name=table_name,
    con=engine,
    if_exists="replace",
    index=False,
    schema="public",
    chunksize=1000,
    method="multi"
)

print("Legacy data ingestion complete!")

# --------------------------------------------------
# 7. Verify inserted records
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text(
            "SELECT COUNT(*) FROM public.tbl_sc_fleet_hist_raw"
        )
    )

    total_records = result.scalar_one()

    print(f"Total records inserted: {total_records}")

engine.dispose()
