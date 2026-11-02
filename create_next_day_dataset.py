import pandas as pd
from pathlib import Path

# Load historical and testing stock data
historical = pd.read_csv("results/reliance_historical.csv")
testing = pd.read_csv("results/reliance_testing.csv")

# Load historical and testing daily news features
historical_news = pd.read_csv("results/reliance_daily_news_features.csv")
testing_news = pd.read_csv("results/reliance_daily_news_testing_features.csv")

# Standardize column names
for df in [historical, testing, historical_news, testing_news]:
    df.columns = df.columns.str.strip()

# Combine all stock trading dates
stock = pd.concat([historical, testing], ignore_index=True)

stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()
stock["Close Price"] = pd.to_numeric(stock["Close Price"], errors="coerce")

stock = stock.dropna(subset=["Date", "Close Price"])
stock = stock.sort_values("Date").drop_duplicates("Date").reset_index(drop=True)

# Combine news features
news = pd.concat(
    [historical_news, testing_news],
    ignore_index=True
)

news["article_date"] = pd.to_datetime(news["article_date"]).dt.normalize()

news = news.drop_duplicates("article_date", keep="last")

# Merge news onto stock trading dates
merged = stock.merge(
    news,
    left_on="Date",
    right_on="article_date",
    how="left"
)

# Keep missing news as missing; do not replace it with zero
merged["news_available"] = merged["article_count"].notna()

# Create next-trading-day target
merged["forecast_date"] = merged["Date"]
merged["target_date"] = merged["Date"].shift(-1)
merged["previous_close"] = merged["Close Price"]
merged["target_close"] = merged["Close Price"].shift(-1)

# Remove the final row because it has no next trading-day target
forecast = merged.dropna(subset=["target_date", "target_close"]).copy()

forecast = forecast.rename(columns={
    "article_count": "same_day_article_count",
    "mean_tone": "same_day_mean_tone"
})

forecast["forecast_cutoff"] = (
    forecast["forecast_date"].dt.strftime("%Y-%m-%d") + " 18:00 IST"
)

# Keep forecast origins within the required testing period
test_start = pd.Timestamp("2026-07-01")
test_end = pd.Timestamp("2026-09-30")

test_forecast = forecast[
    (forecast["forecast_date"] >= test_start) &
    (forecast["forecast_date"] <= test_end)
].copy()

columns = [
    "forecast_date",
    "forecast_cutoff",
    "target_date",
    "previous_close",
    "target_close",
    "same_day_article_count",
    "same_day_mean_tone",
    "news_available"
]

output = Path("results")
output.mkdir(exist_ok=True)

test_forecast[columns].to_csv(
    output / "testing_next_day_forecast_dataset_preliminary.csv",
    index=False
)

print("NEXT-TRADING-DAY DATASET SUMMARY")
print("Forecast rows:", len(test_forecast))
print("First forecast date:", test_forecast["forecast_date"].min())
print("Last forecast date:", test_forecast["forecast_date"].max())
print("First target date:", test_forecast["target_date"].min())
print("Last target date:", test_forecast["target_date"].max())
print("\nFirst 10 rows:")
print(test_forecast[columns].head(10).to_string(index=False))
print("\nSaved: results/testing_next_day_forecast_dataset_preliminary.csv")
