import pandas as pd

df = pd.read_csv("results/reliance_news_testing_cleaned.csv")

df["tone_score"] = pd.to_numeric(
    df["V2Tone"].astype(str).str.split(",").str[0],
    errors="coerce"
)

daily = (
    df.groupby("article_date")
    .agg(
        article_count=("DocumentIdentifier", "nunique"),
        mean_tone=("tone_score", "mean")
    )
    .reset_index()
)

daily.to_csv(
    "results/reliance_daily_news_testing_features.csv",
    index=False
)

print("DAILY TESTING NEWS FEATURES")
print("Dates with news:", len(daily))
print("Total articles:", daily["article_count"].sum())
print(daily.head(10).to_string(index=False))
print("\nSaved: results/reliance_daily_news_testing_features.csv")
