import os
from pathlib import Path

import pandas as pd

from dotenv import load_dotenv

from sqlalchemy import URL , create_engine , text

# Load environment variables

project_root = Path(__file__).resolve().parent.parent

load_dotenv(project_root /  ".env")

# Database connection

connection_url = URL.create(
      "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST", "cloud-sql-proxy"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME")
)


engine = create_engine(connection_url)

# Execute SQL Query

with engine.connect() as connection:

    result = connection.execute(
        text(
            "SELECT * FROM public.tbl_sc_fleet_hist_raw limit 1"
        )
    )

    total_records = result.scalar_one()

    print(f"Total records inserted: {total_records}")

engine.dispose()
