import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")
frames = []

for file in folder.glob("*.csv"):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        required = {"DATE", "DocumentIdentifier", "V2Tone"}

        if required.issubset(df.columns):
            frames.append(df[["DATE", "DocumentIdentifier", "V2Tone"]])
    except Exception:
        pass

news = pd.concat(frames, ignore_index=True)
news = news.drop_duplicates("DocumentIdentifier")

news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True
)

news["timestamp_ist"] = news["timestamp_utc"].dt.tz_convert(
    "Asia/Kolkata"
)

excluded = news[
    (news["timestamp_ist"] < "2025-01-01") |
    (news["timestamp_ist"] >= "2026-07-01")
]

print("Excluded records:", len(excluded))
print("\nExcluded dates:")
print(excluded["timestamp_ist"].dt.date.value_counts().sort_index())
