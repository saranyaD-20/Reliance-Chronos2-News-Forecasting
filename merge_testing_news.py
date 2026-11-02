import pandas as pd

stock = pd.read_csv("results/testing_stock_news.csv")
news = pd.read_csv("results/reliance_daily_news_testing_features.csv")

stock.columns = stock.columns.str.strip()
news.columns = news.columns.str.strip()

stock["Date"] = pd.to_datetime(stock["Date"]).dt.strftime("%Y-%m-%d")

merged = stock.drop(
    columns=["article_count", "mean_tone"],
    errors="ignore"
).merge(
    news,
    left_on="Date",
    right_on="article_date",
    how="left"
)

missing = merged["article_count"].isna()

merged["news_available"] = ~missing

merged.to_csv(
    "results/testing_stock_news_preliminary.csv",
    index=False
)

print("TESTING MERGE SUMMARY")
print("Trading days:", len(merged))
print("Dates with news:", int((~missing).sum()))
print("Dates without news:", int(missing.sum()))

print("\nDates without news:")
print(merged.loc[missing, "Date"].to_string(index=False))

print("\nSaved: results/testing_stock_news_preliminary.csv")
