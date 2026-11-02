


import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

files = [
    "reliance_news_2025_week28.csv",
    "reliance_news_2025_week29.csv",
    "reliance_news_2025_week30.csv",
    "reliance_news_2025_week31.csv",
    "reliance_news_2025_week32.csv",
    "reliance_news_2025_week33.csv",
    "reliance_news_2025_week34.csv",
    "reliance_news_2025_week35.csv",
]

for filename in files:
    path = folder / filename

    print("\n" + "=" * 65)
    print("FILE:", filename)

    df = pd.read_csv(path)

    print("Columns:", df.columns.tolist())
    print("Rows:", len(df))
    print(df.head(10).to_string(index=False))
