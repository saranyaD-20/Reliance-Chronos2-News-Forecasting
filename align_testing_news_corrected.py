import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

files = [
    folder / "reliance_news_july_2026.csv",
    folder / "reliance_news_august_2026.csv",
    folder / "reliance_news_september_2026.csv"
]

frames = []

for file in files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    frames.append(df[["DATE", "DocumentIdentifier", "V2Tone"]])
    print(file.name, ":", len(df), "rows")

news = pd.concat(frames, ignore_index=True)

news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True,
    errors="coerce"
)

news = news.dropna(subset=["timestamp_utc", "DocumentIdentifier", "V2Tone"])
news["timestamp_ist"] = news["timestamp_utc"].dt.tz_convert("Asia/Kolkata")

news = news.drop_duplicates("DocumentIdentifier", keep="first")
news = news.sort_values("timestamp_ist")

stock = pd.read_csv("results/reliance_testing.csv")
stock.columns = stock.columns.str.strip()
stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()

cutoffs = pd.DataFrame({
    "forecast_date": stock["Date"].dropna().sort_values().unique()
})

cutoffs["cutoff"] = (
    pd.to_datetime(cutoffs["forecast_date"])
    .dt.tz_localize("Asia/Kolkata")
    + pd.Timedelta(hours=18)
)

# Include only articles available by the final testing cutoff.
final_cutoff = cutoffs["cutoff"].max()
news = news[news["timestamp_ist"] <= final_cutoff].copy()

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

result = cutoffs[["forecast_date"]].merge(
    daily,
    on="forecast_date",
    how="left"
)

result["coverage_status"] = result["coverage_status"].fillna("unavailable")

result.to_csv(
    "results/testing_news_forecast_features_corrected.csv",
    index=False
)

print("\nCORRECTED TESTING NEWS ALIGNMENT")
print("Raw rows:", len(news))
print("Unique articles assigned:", assigned["DocumentIdentifier"].nunique())
print("Trading forecast dates:", len(result))
print("Dates with news:", result["article_count"].notna().sum())
print("Dates unavailable:", result["article_count"].isna().sum())
print("\nFirst 5 records:")
print(result.head().to_string(index=False))
print("\nSaved: results/testing_news_forecast_features_corrected.csv")
