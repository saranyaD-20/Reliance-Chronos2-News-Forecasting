
import pandas as pd

# Read test news
df = pd.read_csv("nse_data/news/reliance_news_test.csv")

# Convert timestamps to IST
df["article_timestamp"] = pd.to_datetime(
    df["article_timestamp"], utc=True
)

df["article_timestamp"] = (
    df["article_timestamp"].dt.tz_convert("Asia/Kolkata")
)

# Extract article date
df["article_date"] = df["article_timestamp"].dt.date

# Keep only articles published by 6 PM IST
df = df[
    df["article_timestamp"].dt.hour.le(18)
    & (
        df["article_timestamp"].dt.hour.lt(18)
        | df["article_timestamp"].dt.minute.eq(0)
          & df["article_timestamp"].dt.second.eq(0)
    )
].copy()

# Remove duplicate URLs
df = df.drop_duplicates(
    subset=["article_url"]
)

# Calculate daily news features
daily_news = df.groupby("article_date").agg(
    article_count=("article_url", "count"),
    mean_tone=("tone", "mean")
).reset_index()

# Save daily news
daily_news.to_csv(
    "nse_data/news/daily_news_test.csv",
    index=False
)

print("Daily news aggregation completed!")
print(daily_news)
