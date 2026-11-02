import pandas as pd

# Load datasets
historical = pd.read_csv("results/reliance_historical.csv")
testing = pd.read_csv("results/reliance_testing.csv")
news = pd.read_csv("results/reliance_daily_news_features.csv")

# Clean column names
for df in [historical, testing, news]:
    df.columns = df.columns.str.strip()

# Convert dates
historical["Date"] = pd.to_datetime(historical["Date"])
testing["Date"] = pd.to_datetime(testing["Date"])
news["article_date"] = pd.to_datetime(news["article_date"])

# Rename news date column
news = news.rename(columns={"article_date": "Date"})

# Merge separately
historical_merged = historical.merge(
    news,
    on="Date",
    how="left"
)

testing_merged = testing.merge(
    news,
    on="Date",
    how="left"
)

# Sort by date
historical_merged = historical_merged.sort_values("Date")
testing_merged = testing_merged.sort_values("Date")

# Save outputs
historical_merged.to_csv(
    "results/historical_stock_news.csv",
    index=False
)

testing_merged.to_csv(
    "results/testing_stock_news.csv",
    index=False
)

# Display results
print("HISTORICAL MERGE")
print("Rows:", len(historical_merged))
print("News matched:", historical_merged["article_count"].notna().sum())
print("News unmatched:", historical_merged["article_count"].isna().sum())

print("\nTESTING MERGE")
print("Rows:", len(testing_merged))
print("News matched:", testing_merged["article_count"].notna().sum())
print("News unmatched:", testing_merged["article_count"].isna().sum())

print("\nHISTORICAL SAMPLE")
print(historical_merged.head(10).to_string(index=False))

print("\nSaved:")
print("results/historical_stock_news.csv")
print("results/testing_stock_news.csv")
