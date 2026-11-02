import pandas as pd

df = pd.read_csv("results/final_next_day_forecasting_dataset.csv")

print("MODEL INPUT CHECK")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())
print("Missing prices:", df[["previous_close", "target_close"]].isna().sum().sum())
print("Missing news rows:", df["coverage_status"].eq("unavailable").sum())
print("Testing rows:", (pd.to_datetime(df["forecast_date"]) >= "2026-07-01").sum())

print("\nTesting sample:")
print(df.tail(5).to_string(index=False))
