import pandas as pd

df = pd.read_csv("results/historical_stock_news.csv")

missing = df[df["article_count"].isna()]

print("CURRENT MISSING HISTORICAL NEWS DATES")
print(missing[["Date", "Close Price"]].to_string(index=False))
print("\nTotal missing:", len(missing))
