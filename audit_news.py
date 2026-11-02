
import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

files = sorted(folder.glob("reliance_news_*_week*.csv"))

print("WEEKLY NEWS FILE AUDIT")
print("-" * 75)

total_rows = 0

for file in files:
    try:
        df = pd.read_csv(file)
        rows = len(df)

        total_rows += rows

        required = {"DATE", "DocumentIdentifier", "V2Tone"}
        valid_columns = required.issubset(df.columns)

        status = "VALID" if valid_columns and rows > 0 else "CHECK"

        print(
            f"{file.name:45} "
            f"Rows: {rows:6} "
            f"Status: {status}"
        )

    except Exception as e:
        print(f"{file.name}: ERROR - {e}")

print("-" * 75)
print("Total files:", len(files))
print("Total records:", total_rows)
