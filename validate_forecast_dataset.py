import pandas as pd

df = pd.read_csv(
    "results/testing_next_day_forecast_dataset_preliminary.csv"
)

df["forecast_date"] = pd.to_datetime(df["forecast_date"])
df["target_date"] = pd.to_datetime(df["target_date"])

print("FORECAST DATASET VALIDATION")
print("Total forecast rows:", len(df))
print("Duplicate forecast dates:", df["forecast_date"].duplicated().sum())
print("Duplicate target dates:", df["target_date"].duplicated().sum())
print("Target after forecast date:",
      (df["target_date"] > df["forecast_date"]).all())
print("Missing target prices:", df["target_close"].isna().sum())
print("Missing previous prices:", df["previous_close"].isna().sum())

print("\nLast 5 forecast rows:")
print(df.tail().to_string(index=False))
