import pandas as pd

df = pd.read_csv("results/reliance_news_cleaned.csv")

df["timestamp_ist"] = pd.to_datetime(df["timestamp_ist"])

# Create 6 PM IST cutoff for each calendar day
df["cutoff"] = (
    df["timestamp_ist"].dt.normalize()
    + pd.Timedelta(hours=18)
)

# Keep articles published by 6 PM
before_cutoff = df[
    df["timestamp_ist"] <= df["cutoff"]
].copy()

after_cutoff = df[
    df["timestamp_ist"] > df["cutoff"]
].copy()

before_cutoff.to_csv(
    "results/reliance_news_before_6pm.csv",
    index=False
)

print("6 PM CUTOFF COMPLETED")
print("Original articles:", len(df))
print("Available by 6 PM:", len(before_cutoff))
print("Excluded after 6 PM:", len(after_cutoff))
print("Saved: results/reliance_news_before_6pm.csv")
