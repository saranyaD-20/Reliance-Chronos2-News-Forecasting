
import pandas as pd
from pathlib import Path

# Load combined news data
input_file = Path("results/reliance_news_combined_raw.csv")
df = pd.read_csv(input_file)

print("Original records:", len(df))

# Remove empty URLs and timestamps
df = df.dropna(subset=["DATE", "DocumentIdentifier", "V2Tone"])

# Remove spaces from URLs
df["DocumentIdentifier"] = (
    df["DocumentIdentifier"].astype(str).str.strip()
)

# Remove duplicate article URLs
df = df.drop_duplicates(
    subset=["DocumentIdentifier"],
    keep="first"
)

# Convert GDELT DATE to UTC timestamp
df["article_timestamp_utc"] = pd.to_datetime(
    df["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True,
    errors="coerce"
)

# Remove invalid timestamps
df = df.dropna(subset=["article_timestamp_utc"])

# Convert UTC to Indian Standard Time
df["article_timestamp_ist"] = (
    df["article_timestamp_utc"]
    .dt.tz_convert("Asia/Kolkata")
)

# Extract IST article date
df["article_date_ist"] = (
    df["article_timestamp_ist"].dt.date
)

# Save cleaned article-level dataset
output_file = Path("results/reliance_news_cleaned.csv")
df.to_csv(output_file, index=False)

print("\nCLEANING COMPLETED")
print("Cleaned records:", len(df))
print("Output file:", output_file)

print("\nFirst five records:")
print(
    df[
        [
            "DocumentIdentifier",
            "article_timestamp_utc",
            "article_timestamp_ist",
            "article_date_ist",
            "V2Tone"
        ]
    ].head()
)
