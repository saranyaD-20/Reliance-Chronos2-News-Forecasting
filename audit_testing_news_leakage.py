import pandas as pd
from pathlib import Path

NEWS_FOLDER = Path("nse_data/news")

files = [
    NEWS_FOLDER / "reliance_news_july_2026.csv",
    NEWS_FOLDER / "reliance_news_august_2026.csv",
    NEWS_FOLDER / "reliance_news_september_2026.csv"
]

# Load raw GDELT news
frames = []

for file in files:
    df = pd.read_csv(file)
    frames.append(df[["DATE", "DocumentIdentifier", "V2Tone"]])

news = pd.concat(frames, ignore_index=True)

news["timestamp_utc"] = pd.to_datetime(
    news["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True,
    errors="coerce"
)

news = news.dropna(
    subset=["timestamp_utc", "DocumentIdentifier", "V2Tone"]
)

news["timestamp_ist"] = (
    news["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
)

news = news.drop_duplicates(
    "DocumentIdentifier",
    keep="first"
)

# Load NSE testing trading dates
stock = pd.read_csv("results/reliance_testing.csv")

stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()

dates = sorted(stock["Date"].dropna().unique())

cutoffs = pd.DataFrame({"forecast_date": dates})

cutoffs["cutoff"] = (
    cutoffs["forecast_date"]
    .dt.tz_localize("Asia/Kolkata")
    + pd.Timedelta(hours=18)
)

# Audit each forecast interval
audit_rows = []

for i, row in cutoffs.iterrows():

    upper = row["cutoff"]

    if i == 0:
        lower = upper - pd.Timedelta(days=1)
    else:
        lower = cutoffs.iloc[i - 1]["cutoff"]

    interval = news[
        (news["timestamp_ist"] > lower) &
        (news["timestamp_ist"] <= upper)
    ]

    audit_rows.append({
        "forecast_date": row["forecast_date"],
        "lower_boundary": lower,
        "upper_boundary": upper,
        "article_count": interval["DocumentIdentifier"].nunique(),
        "lower_boundary_leakage": (
            interval["timestamp_ist"] <= lower
        ).sum(),
        "upper_boundary_leakage": (
            interval["timestamp_ist"] > upper
        ).sum()
    })

audit = pd.DataFrame(audit_rows)

# Compare against saved corrected features
saved = pd.read_csv(
    "results/testing_news_forecast_features_corrected.csv"
)

saved["forecast_date"] = pd.to_datetime(saved["forecast_date"])
audit["forecast_date"] = pd.to_datetime(audit["forecast_date"])

comparison = audit.merge(
    saved[["forecast_date", "article_count"]],
    on="forecast_date",
    suffixes=("_audit", "_saved")
)

comparison["count_match"] = (
    comparison["article_count_audit"] ==
    comparison["article_count_saved"]
)

print("\nTESTING NEWS LEAKAGE AUDIT")
print("-" * 55)
print("Dates audited:", len(comparison))
print("Article count mismatches:", (~comparison["count_match"]).sum())
print("Lower-bound leakage:", comparison["lower_boundary_leakage"].sum())
print("Upper-bound leakage:", comparison["upper_boundary_leakage"].sum())

print("\nFirst 5 audit records:")
print(comparison.head().to_string(index=False))

comparison.to_csv(
    "results/testing_news_leakage_audit.csv",
    index=False
)

passed = (
    comparison["count_match"].all()
    and comparison["lower_boundary_leakage"].sum() == 0
    and comparison["upper_boundary_leakage"].sum() == 0
)

print("\nAUDIT STATUS:", "PASSED" if passed else "FAILED")
print("Saved: results/testing_news_leakage_audit.csv")