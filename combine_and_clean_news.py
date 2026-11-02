import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")
output = Path("results")

required = {"DATE", "DocumentIdentifier", "V2Tone"}
frames = []

for file in folder.glob("*.csv"):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        if required.issubset(df.columns):
            df = df[["DATE", "DocumentIdentifier", "V2Tone"]].copy()
            frames.append(df)
            print("Included:", file.name, "|", len(df), "rows")

    except Exception as e:
        print("Skipped:", file.name, "|", e)

news = pd.concat(frames, ignore_index=True)

print("\nRaw rows:", len(news))

# Remove duplicate URLs
news = news.drop_duplicates(
    subset=["DocumentIdentifier"],
    keep="first"
)

# Parse GDELT timestamps
news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    errors="coerce",
    utc=True
)

news = news.dropna(subset=["timestamp_utc"])

# Convert to Indian Standard Time
news["timestamp_ist"] = (
    news["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
)

# Keep project period
news = news[
    (news["timestamp_ist"] >= "2025-01-01") &
    (news["timestamp_ist"] < "2026-07-01")
].copy()

output.mkdir(exist_ok=True)

news.to_csv(
    output / "reliance_news_cleaned.csv",
    index=False
)

print("\nCLEANING COMPLETED")
print("Final rows:", len(news))
print("Unique URLs:", news["DocumentIdentifier"].nunique())
print("First date:", news["timestamp_ist"].min())
print("Last date:", news["timestamp_ist"].max())
print("Saved: results/reliance_news_cleaned.csv")
