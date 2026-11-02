
import pandas as pd

# Read cleaned NSE dataset
df = pd.read_csv("results/reliance_combined_clean.csv")

df["Date"] = pd.to_datetime(df["Date"])

# Historical dataset
historical = df[
    (df["Date"] >= "2025-01-01") &
    (df["Date"] <= "2026-06-30")
].copy()

# Testing dataset
testing = df[
    (df["Date"] >= "2026-07-01") &
    (df["Date"] <= "2026-09-30")
].copy()

# Save separately
historical.to_csv(
    "results/reliance_historical.csv",
    index=False
)

testing.to_csv(
    "results/reliance_testing.csv",
    index=False
)

print("Historical records:", len(historical))
print("Testing records:", len(testing))

print("\nHistorical date range:")
print(historical["Date"].min(), "to", historical["Date"].max())

print("\nTesting date range:")
print(testing["Date"].min(), "to", testing["Date"].max())
