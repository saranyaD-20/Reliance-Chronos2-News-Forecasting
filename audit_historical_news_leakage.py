import pandas as pd
from pathlib import Path

# Load cleaned historical news
news = pd.read_csv("results/reliance_news_cleaned.csv")

news["timestamp_ist"] = pd.to_datetime(
    news["timestamp_ist"], utc=True
).dt.tz_convert("Asia/Kolkata")

news = news.dropna(
    subset=["timestamp_ist", "DocumentIdentifier", "V2Tone"]
)

news = news.drop_duplicates(
    "DocumentIdentifier", keep="first"
)

# Load historical NSE trading dates
stock = pd.read_csv("results/reliance_historical.csv")

stock["Date"] = pd.to_datetime(stock["Date"]).dt.normalize()

dates = sorted(stock["Date"].dropna().unique())

cutoffs = pd.DataFrame({"forecast_date": dates})

cutoffs["cutoff"] = (
    cutoffs["forecast_date"]
    .dt.tz_localize("Asia/Kolkata")
    + pd.Timedelta(hours=18)
)

# Check each forecast interval
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
        "article_count": interval["DocumentIdentifier"].nunique(),
        "lower_boundary_leakage": int(
            (interval["timestamp_ist"] <= lower).sum()
        ),
        "upper_boundary_leakage": int(
            (interval["timestamp_ist"] > upper).sum()
        )
    })

audit = pd.DataFrame(audit_rows)

# Compare with saved historical features
saved = pd.read_csv(
    "results/historical_news_forecast_features.csv"
)

saved["forecast_date"] = pd.to_datetime(saved["forecast_date"])
audit["forecast_date"] = pd.to_datetime(audit["forecast_date"])

comparison = audit.merge(
    saved[["forecast_date", "article_count", "coverage_status"]],
    on="forecast_date",
    suffixes=("_audit", "_saved")
)

comparison["count_match"] = (
    comparison["article_count_audit"] ==
    comparison["article_count_saved"]
)

# Exclude unavailable coverage dates from count comparison
available = comparison[
    comparison["coverage_status"] == "available"
]

print("\nHISTORICAL NEWS LEAKAGE AUDIT")
print("-" * 55)
print("Dates audited:", len(comparison))
print("Available dates:", len(available))
print("Unavailable dates:",
      comparison["coverage_status"].eq("unavailable").sum())
print("Article count mismatches:",
      (~available["count_match"]).sum())
print("Lower-bound leakage:",
      comparison["lower_boundary_leakage"].sum())
print("Upper-bound leakage:",
      comparison["upper_boundary_leakage"].sum())

comparison.to_csv(
    "results/historical_news_leakage_audit.csv",
    index=False
)

passed = (
    available["count_match"].all()
    and comparison["lower_boundary_leakage"].sum() == 0
    and comparison["upper_boundary_leakage"].sum() == 0
)

print("\nAUDIT STATUS:", "PASSED" if passed else "FAILED")
print("Saved: results/historical_news_leakage_audit.csv")