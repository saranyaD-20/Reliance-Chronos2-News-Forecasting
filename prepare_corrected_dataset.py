import pandas as pd
import numpy as np

source = "results/final_next_day_forecasting_dataset_corrected.csv"

df = pd.read_csv(source)

# Apply log1p only where article counts are available.
df["log_article_count"] = np.log1p(df["article_count"])

# Zero tone is valid only when coverage is available
# and the article count is genuinely zero.
known_zero = (
    (df["coverage_status"] == "available") &
    (df["article_count"] == 0)
)

df.loc[known_zero, "mean_tone"] = 0.0

df.to_csv(source, index=False)

print("CORRECTED DATASET PREPARED")
print("Total rows:", len(df))
print("New feature: log_article_count")
print("Unavailable news rows preserved:",
      (df["coverage_status"] == "unavailable").sum())
print("Missing log features:", df["log_article_count"].isna().sum())
print("\nFirst 5 records:")
print(df.head().to_string(index=False))
print("\nSaved:", source)
