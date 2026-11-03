import pandas as pd
import math
from supabase_client import supabase

files = [
    "results/historical_news_forecast_features.csv",
    "results/testing_news_forecast_features_corrected.csv"
]

frames = [pd.read_csv(file) for file in files]
df = pd.concat(frames, ignore_index=True)

df = df.drop_duplicates(subset=["forecast_date"], keep="last")
df = df.sort_values("forecast_date")

records = []

for _, row in df.iterrows():
    available = str(row["coverage_status"]).lower() == "available"

    count = None
    tone = None
    log_count = None

    if available and pd.notna(row["article_count"]):
        count = int(row["article_count"])
        log_count = math.log1p(count)

    if available and pd.notna(row["mean_tone"]):
        tone = float(row["mean_tone"])

    records.append({
        "trading_date": str(row["forecast_date"])[:10],
        "article_count": count,
        "log_article_count": log_count,
        "mean_tone": tone,
        "coverage_status": "available" if available else "unavailable"
    })

for start in range(0, len(records), 500):
    batch = records[start:start + 500]
    supabase.table("news_features").insert(batch).execute()

print("News-feature upload completed.")
print("Total records:", len(records))
print("Available:", sum(r["coverage_status"] == "available" for r in records))
print("Unavailable:", sum(r["coverage_status"] == "unavailable" for r in records))
