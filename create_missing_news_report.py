import pandas as pd

df = pd.read_csv("results/historical_stock_news.csv")

missing = df[df["article_count"].isna()][["Date", "Close Price"]].copy()

missing["reason"] = "News data unavailable in collected GDELT files"

missing.to_csv("results/historical_missing_news_dates.csv", index=False)

print("Missing-news report saved.")
print("Total missing dates:", len(missing))
print(missing.to_string(index=False))
