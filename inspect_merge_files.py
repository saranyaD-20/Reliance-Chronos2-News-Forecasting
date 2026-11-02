import pandas as pd

files = [
    "results/reliance_historical.csv",
    "results/reliance_testing.csv",
    "results/reliance_daily_news_features.csv"
]

for file in files:
    print("\n" + "=" * 60)
    print("FILE:", file)

    df = pd.read_csv(file)

    df.columns = df.columns.str.strip()

    print("Columns:", list(df.columns))
    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))
    print("Total rows:", len(df))
