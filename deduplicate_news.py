import pandas as pd

df = pd.read_csv("results/news_date_audit.csv")

print("Original rows:", len(df))

# Remove duplicate article URLs
df = df.drop_duplicates(
    subset=["DocumentIdentifier"],
    keep="first"
)

print("Rows after deduplication:", len(df))
print("Unique URLs:", df["DocumentIdentifier"].nunique())

# Save verified raw records
df.to_csv(
    "results/reliance_news_deduplicated.csv",
    index=False
)

print("\nSaved: results/reliance_news_deduplicated.csv")
