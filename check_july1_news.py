import pandas as pd

df = pd.read_csv("results/reliance_news_cleaned.csv")

df["timestamp_ist"] = pd.to_datetime(df["timestamp_ist"])

july_1 = df[df["timestamp_ist"].dt.date == pd.Timestamp("2025-07-01").date()]

print("Articles available on July 1, 2025:", len(july_1))

if len(july_1) > 0:
    print(july_1[["timestamp_ist", "article_url", "tone"]].head(10).to_string(index=False))
