import pandas as pd
from pathlib import Path

# Load historical trading dates and cleaned article-level news
stock = pd.read_csv("results/reliance_historical.csv")
news = pd.read_csv("results/reliance_news_cleaned.csv")

stock.columns = stock.columns.str.strip()
news.columns = news.columns.str.strip()

stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()
news["timestamp_ist"] = pd.to_datetime(news["timestamp_ist"], utc=True).dt.tz_convert("Asia/Kolkata")

# Historical news collection has a known coverage gap.
# Do not interpret missing source coverage as zero articles.
stock_dates = sorted(stock["Date"].dropna().unique())

news["available_at"] = news["timestamp_ist"]

# Assign each article to the first NSE trading-day cutoff
# at or after its publication time.
cutoffs = pd.DataFrame({
    "forecast_date": stock_dates
})

cutoffs["cutoff"] = (
    pd.to_datetime(cutoffs["forecast_date"])
    .dt.tz_localize("Asia/Kolkata")
    + pd.Timedelta(hours=18)
)

news = news.sort_values("available_at")
cutoffs = cutoffs.sort_values("cutoff")

assigned = pd.merge_asof(
    news,
    cutoffs,
    left_on="available_at",
    right_on="cutoff",
    direction="forward"
)

# Keep articles assigned to a historical trading-day forecast.
assigned = assigned.dropna(subset=["forecast_date"])

# Calculate tone using the first V2Tone component.
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

daily["forecast_date"] = pd.to_datetime(daily["forecast_date"])

# Mark known historical GDELT coverage gap.
gap_start = pd.Timestamp("2025-06-15")
gap_end = pd.Timestamp("2025-07-01")

daily["coverage_status"] = "available"

# Preserve missing coverage separately.
gap_dates = pd.DataFrame({
    "forecast_date": pd.to_datetime(stock_dates)
})

gap_dates = gap_dates[
    (gap_dates["forecast_date"] >= gap_start) &
    (gap_dates["forecast_date"] <= gap_end)
]

daily = pd.concat([
    daily,
    gap_dates.assign(
        article_count=pd.NA,
        mean_tone=pd.NA,
        coverage_status="unavailable"
    )
], ignore_index=True)

daily = daily.drop_duplicates("forecast_date", keep="last")

output = Path("results")
output.mkdir(exist_ok=True)

daily.sort_values("forecast_date").to_csv(
    output / "historical_news_forecast_features.csv",
    index=False
)

print("HISTORICAL NEWS ALIGNMENT")
print("Forecast dates with features:", len(daily))
print("Unavailable coverage dates:", (daily["coverage_status"] == "unavailable").sum())
print("Total assigned articles:", assigned["DocumentIdentifier"].nunique())
print("\nFirst 5 rows:")
print(daily.head().to_string(index=False))
print("\nSaved: results/historical_news_forecast_features.csv")
