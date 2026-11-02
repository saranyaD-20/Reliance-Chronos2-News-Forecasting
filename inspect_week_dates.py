import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

for file in sorted(folder.glob("reliance_news_2025_week*.csv")):
    try:
        df = pd.read_csv(file, usecols=["DATE"], dtype=str)

        dates = pd.to_datetime(
            df["DATE"].str.zfill(14),
            format="%Y%m%d%H%M%S",
            errors="coerce"
        )

        valid_dates = dates.dropna()

        if len(valid_dates):
            print(
                f"{file.name}: "
                f"{valid_dates.min()} to {valid_dates.max()} "
                f"| Rows: {len(df)}"
            )
        else:
            print(f"{file.name}: No valid dates")

    except Exception as e:
        print(f"{file.name}: ERROR - {e}")
