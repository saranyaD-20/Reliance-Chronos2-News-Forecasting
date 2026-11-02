import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")
required = {"DATE", "DocumentIdentifier", "V2Tone"}

frames = []

for file in folder.glob("reliance_news_2025_week*.csv"):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        if required.issubset(df.columns):
            df["source_file"] = file.name
            frames.append(df[["DATE", "DocumentIdentifier", "V2Tone", "source_file"]])

    except Exception as e:
        print("Error:", file.name, e)

if not frames:
    print("No valid raw news files found.")
    raise SystemExit

news = pd.concat(frames, ignore_index=True)

news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    errors="coerce",
    utc=True
)

news = news.dropna(subset=["timestamp_utc"])

news["date_ist"] = (
    news["timestamp_utc"]
    .dt.tz_convert("Asia/Kolkata")
    .dt.date
)

print("TOTAL RAW ROWS:", len(news))
print("UNIQUE URLS:", news["DocumentIdentifier"].nunique())
print("DUPLICATE URL ROWS:", news.duplicated("DocumentIdentifier").sum())
print("FIRST IST DATE:", news["date_ist"].min())
print("LAST IST DATE:", news["date_ist"].max())

print("\nDATE RANGE BY FILE:")
for filename, group in news.groupby("source_file"):
    print(
        filename,
        "|",
        group["date_ist"].min(),
        "to",
        group["date_ist"].max(),
        "| rows:",
        len(group)
    )

print("\nSAVED DATE AUDIT")
news.to_csv("results/news_date_audit.csv", index=False)
