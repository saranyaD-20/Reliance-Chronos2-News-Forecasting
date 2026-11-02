
import pandas as pd
import numpy as np
from pathlib import Path

# Load stock data
historical = pd.read_csv("results/reliance_historical.csv")
testing = pd.read_csv("results/reliance_testing.csv")

# Load news features
hist_news = pd.read_csv(
    "results/historical_news_forecast_features.csv"
)

test_news = pd.read_csv(
    "results/testing_news_forecast_features_corrected.csv"
)

# Clean column names
for df in [historical, testing, hist_news, test_news]:
    df.columns = df.columns.str.strip()

# Convert dates
historical["Date"] = pd.to_datetime(historical["Date"])
testing["Date"] = pd.to_datetime(testing["Date"])

hist_news["forecast_date"] = pd.to_datetime(
    hist_news["forecast_date"]
)
test_news["forecast_date"] = pd.to_datetime(
    test_news["forecast_date"]
)

# Combine stock data
stock = pd.concat(
    [historical, testing],
    ignore_index=True
)

stock = (
    stock.sort_values("Date")
    .drop_duplicates("Date")
    .reset_index(drop=True)
)

# Combine corrected news features
news = pd.concat(
    [hist_news, test_news],
    ignore_index=True
)

news = news.drop_duplicates(
    "forecast_date",
    keep="last"
)

# Merge stock and news
data = stock.merge(
    news,
    left_on="Date",
    right_on="forecast_date",
    how="left"
)

# Create next-trading-day target
data["target_date"] = data["Date"].shift(-1)

data["previous_close"] = pd.to_numeric(
    data["Close Price"],
    errors="coerce"
)

data["target_close"] = pd.to_numeric(
    data["Close Price"].shift(-1),
    errors="coerce"
)

data = data.dropna(
    subset=["target_date", "target_close"]
).copy()

# Forecast cutoff
data["forecast_cutoff"] = (
    data["Date"].dt.strftime("%Y-%m-%d")
    + " 18:00 IST"
)

# Preserve unavailable news as missing
data["article_count"] = pd.to_numeric(
    data["article_count"],
    errors="coerce"
)

data["mean_tone"] = pd.to_numeric(
    data["mean_tone"],
    errors="coerce"
)

# Apply zero tone only to available dates with zero articles
available_zero = (
    data["coverage_status"].eq("available")
    & data["article_count"].eq(0)
)

data.loc[available_zero, "mean_tone"] = 0

# Log transformation; missing counts remain missing
data["log_article_count"] = np.log1p(
    data["article_count"]
)

# Rename date column
data = data.drop(columns=["forecast_date"])

data = data.rename(
    columns={"Date": "forecast_date"}
)

# Select final columns
columns = [
    "forecast_date",
    "forecast_cutoff",
    "target_date",
    "previous_close",
    "target_close",
    "article_count",
    "log_article_count",
    "mean_tone",
    "coverage_status"
]

data = data[columns]

# Save corrected dataset separately
Path("results").mkdir(exist_ok=True)

output_file = (
    "results/final_next_day_forecasting_dataset_corrected.csv"
)

data.to_csv(output_file, index=False)

# Validation summary
print("CORRECTED FORECASTING DATASET")
print("Total forecast rows:", len(data))

print(
    "Historical rows:",
    (data["forecast_date"] < "2026-07-01").sum()
)

print(
    "Testing rows:",
    (data["forecast_date"] >= "2026-07-01").sum()
)

print("\nCoverage status:")
print(data["coverage_status"].value_counts(dropna=False))

print("\nMissing values:")
print(data[columns].isna().sum())

print("\nFirst 5 records:")
print(data.head().to_string(index=False))

print("\nLast 5 records:")
print(data.tail().to_string(index=False))

print("\nSaved:", output_file)
