import pandas as pd

# Read deduplicated news
df = pd.read_csv("results/reliance_news_deduplicated.csv")

# Convert UTC timestamps to IST
df["timestamp_utc"] = pd.to_datetime(
    df["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    utc=True
)

df["date_ist"] = (
    df["timestamp_utc"]
    .dt.tz_convert("Asia/Kolkata")
    .dt.date
)

# Expected project period
start = pd.Timestamp("2025-01-01").date()
end = pd.Timestamp("2026-06-30").date()

expected_dates = set(
    pd.date_range(start, end, freq="D").date
)

available_dates = set(df["date_ist"])

missing_dates = sorted(expected_dates - available_dates)

print("Expected calendar days:", len(expected_dates))
print("Dates with news:", len(available_dates & expected_dates))
print("Dates without matching articles:", len(missing_dates))

print("\nMissing date ranges:")

if missing_dates:
    missing_df = pd.DataFrame({"date": missing_dates})
    missing_df["group"] = (
        missing_df["date"].diff().dt.days.ne(1).cumsum()
    )

    for _, group in missing_df.groupby("group"):
        print(group["date"].iloc[0], "to", group["date"].iloc[-1])

print("\nSaved missing dates.")

pd.DataFrame({"missing_date": missing_dates}).to_csv(
    "results/missing_news_dates.csv",
    index=False
)
