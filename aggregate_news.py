import pandas as pd

df = pd.read_csv("results/reliance_news_before_6pm.csv")

# Extract the first value from GDELT V2Tone
df["tone_score"] = pd.to_numeric(
    df["V2Tone"].astype(str).str.split(",").str[0],
    errors="coerce"
)

# Convert timestamp to IST
df["timestamp_ist"] = pd.to_datetime(df["timestamp_ist"])

df["article_date"] = df["timestamp_ist"].dt.date

# Aggregate daily news features
daily = df.groupby("article_date").agg(
    article_count=("DocumentIdentifier", "nunique"),
    mean_tone=("tone_score", "mean")
).reset_index()

daily["mean_tone"] = daily["mean_tone"].round(4)

daily.to_csv(
    "results/reliance_daily_news_features.csv",
    index=False
)

print("DAILY NEWS FEATURES CREATED")
print("Number of dates:", len(daily))
print("Total articles:", daily["article_count"].sum())
print("\nFirst 10 records:")
print(daily.head(10).to_string(index=False))
print("\nSaved: results/reliance_daily_news_features.csv")
