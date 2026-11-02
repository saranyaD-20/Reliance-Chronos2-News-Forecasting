import pandas as pd

df = pd.read_csv("results/historical_news_forecast_features.csv")

print("HISTORICAL NEWS ALIGNMENT VALIDATION")
print("Total dates:", len(df))
print("Duplicate dates:", df["forecast_date"].duplicated().sum())
print("Unavailable dates:", (df["coverage_status"] == "unavailable").sum())
print("Negative article counts:", (pd.to_numeric(df["article_count"], errors="coerce") < 0).sum())

print("\nCoverage status counts:")
print(df["coverage_status"].value_counts(dropna=False))

print("\nRecords around the missing-data period:")
print(
    df[
        (df["forecast_date"] >= "2025-06-10") &
        (df["forecast_date"] <= "2025-07-04")
    ].to_string(index=False)
)
