import pandas as pd
from pathlib import Path

historical = pd.read_csv("results/reliance_historical.csv")
testing = pd.read_csv("results/reliance_testing.csv")

hist_news = pd.read_csv("results/historical_news_forecast_features.csv")
test_news = pd.read_csv("results/testing_news_forecast_features.csv")

for df in [historical, testing, hist_news, test_news]:
    df.columns = df.columns.str.strip()

historical["Date"] = pd.to_datetime(historical["Date"])
testing["Date"] = pd.to_datetime(testing["Date"])

hist_news["forecast_date"] = pd.to_datetime(hist_news["forecast_date"])
test_news["forecast_date"] = pd.to_datetime(test_news["forecast_date"])

stock = pd.concat([historical, testing], ignore_index=True)
stock = stock.sort_values("Date").drop_duplicates("Date")

news = pd.concat([hist_news, test_news], ignore_index=True)

data = stock.merge(
    news,
    left_on="Date",
    right_on="forecast_date",
    how="left"
)

data["target_date"] = data["Date"].shift(-1)
data["previous_close"] = pd.to_numeric(data["Close Price"], errors="coerce")
data["target_close"] = data["Close Price"].shift(-1)

data = data.dropna(subset=["target_date", "target_close"]).copy()

data["forecast_cutoff"] = (
    data["Date"].dt.strftime("%Y-%m-%d") + " 18:00 IST"
)

data = data.rename(columns={
    "Date": "forecast_date",
    "article_count": "article_count",
    "mean_tone": "mean_tone"
})

columns = [
    "forecast_date",
    "forecast_cutoff",
    "target_date",
    "previous_close",
    "target_close",
    "article_count",
    "mean_tone",
    "coverage_status"
]

data = data[columns]

Path("results").mkdir(exist_ok=True)

data.to_csv(
    "results/final_next_day_forecasting_dataset.csv",
    index=False
)

print("FINAL FORECASTING DATASET")
print("Total forecast rows:", len(data))
print("Historical rows:", (data["forecast_date"] < "2026-07-01").sum())
print("Testing rows:", (data["forecast_date"] >= "2026-07-01").sum())
print("\nCoverage status:")
print(data["coverage_status"].value_counts(dropna=False))
print("\nFirst 5 records:")
print(data.head().to_string(index=False))
print("\nLast 5 records:")
print(data.tail().to_string(index=False))
print("\nSaved: results/final_next_day_forecasting_dataset.csv")
