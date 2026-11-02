import pandas as pd

df = pd.read_csv("results/historical_stock_news.csv")

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date")

print("HISTORICAL DATA CHECK")
print("Trading days:", len(df))
print("First date:", df["Date"].min())
print("Last date:", df["Date"].max())
print("Missing news dates:", df["article_count"].isna().sum())
print("Available news dates:", df["article_count"].notna().sum())

print("\nLast 5 historical records:")
print(df.tail().to_string(index=False))
