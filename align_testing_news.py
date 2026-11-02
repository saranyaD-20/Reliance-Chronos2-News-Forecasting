import pandas as pd
from pathlib import Path

stock = pd.read_csv("results/reliance_testing.csv")
news = pd.read_csv("results/reliance_news_testing_cleaned.csv")

stock.columns = stock.columns.str.strip()
news.columns = news.columns.str.strip()

stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()

news["timestamp_ist"] = pd.to_datetime(
    news["timestamp_ist"], utc=True
).dt.tz_convert("Asia/Kolkata")

news = news.sort_values("timestamp_ist")

cutoffs = pd.DataFrame({
    "forecast_date": stock["Date"].dropna().sort_values().unique()
})

cutoffs["cutoff"] = (
    pd.to_datetime(cutoffs["forecast_date"])
    .dt.tz_localize("Asia/Kolkata")
    + pd.Timedelta(hours=18)
)

assigned = pd.merge_asof(
    news,
    cutoffs.sort_values("cutoff"),
    left_on="timestamp_ist",
    right_on="cutoff",
    direction="forward"
)

assigned = assigned.dropna(subset=["forecast_date"])

assigned["tone_score"] = pd.to_numeric(
    assigned["V2Tone"].astype(str).str.split(",").str[0],
    errors="coerce"
)

daily = (
    assigned.groupby("forecast_date")
    .agg(
        article_count=("DocumentIdentifier", "nunique"),
        mean_tone=("tone_score", "mean")
    )
    .reset_index()
)

daily["coverage_status"] = "available"

daily["forecast_date"] = pd.to_datetime(daily["forecast_date"])

# Include every testing trading date.
result = cutoffs[["forecast_date"]].merge(
    daily,
    on="forecast_date",
    how="left"
)

result["coverage_status"] = result["coverage_status"].fillna("unavailable")

result.to_csv(
    "results/testing_news_forecast_features.csv",
    index=False
)

print("TESTING NEWS ALIGNMENT")
print("Forecast dates:", len(result))
print("Dates with news:", result["article_count"].notna().sum())
print("Dates unavailable:", result["article_count"].isna().sum())
print("Unique assigned articles:", assigned["DocumentIdentifier"].nunique())

print("\nFirst 5 records:")
print(result.head().to_string(index=False))

print("\nSaved: results/testing_news_forecast_features.csv")
