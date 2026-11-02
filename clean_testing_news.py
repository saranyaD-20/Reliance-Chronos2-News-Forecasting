import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

files = [
    folder / "reliance_news_july_2026.csv",
    folder / "reliance_news_august_2026.csv",
    folder / "reliance_news_september_2026.csv"
]

for file in files:
    if not file.exists():
        raise FileNotFoundError(f"Missing file: {file}")

frames = []

for file in files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    required = ["DATE", "DocumentIdentifier", "V2Tone"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"{file.name} is missing columns: {missing}")

    frames.append(df[required])
    print(f"{file.name}: {len(df)} rows")

news = pd.concat(frames, ignore_index=True)

news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True,
    errors="coerce"
)

news = news.dropna(subset=["timestamp_utc", "DocumentIdentifier", "V2Tone"])

news["timestamp_ist"] = news["timestamp_utc"].dt.tz_convert("Asia/Kolkata")

news = news.drop_duplicates(
    subset=["DocumentIdentifier"],
    keep="first"
)

start = pd.Timestamp("2026-07-01", tz="Asia/Kolkata")
end = pd.Timestamp("2026-10-01", tz="Asia/Kolkata")

news = news[
    (news["timestamp_ist"] >= start) &
    (news["timestamp_ist"] < end)
].copy()

news["article_date"] = news["timestamp_ist"].dt.strftime("%Y-%m-%d")

news["cutoff"] = news["timestamp_ist"].dt.normalize() + pd.Timedelta(hours=18)

before_cutoff = news[news["timestamp_ist"] <= news["cutoff"]].copy()

output = Path("results")
output.mkdir(exist_ok=True)

before_cutoff.to_csv(
    output / "reliance_news_testing_cleaned.csv",
    index=False
)

print("\nTEST NEWS CLEANING SUMMARY")
print("Combined rows:", sum(len(df) for df in frames))
print("Unique articles in test period:", len(news))
print("Available by 6 PM IST:", len(before_cutoff))
print("Excluded after 6 PM IST:", len(news) - len(before_cutoff))

if len(before_cutoff) > 0:
    print("First article:", before_cutoff["timestamp_ist"].min())
    print("Last article:", before_cutoff["timestamp_ist"].max())

print("\nSaved: results/reliance_news_testing_cleaned.csv")
