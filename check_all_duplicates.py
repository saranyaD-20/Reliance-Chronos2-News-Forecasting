import pandas as pd

df = pd.read_csv("results/news_date_audit.csv")

# Include recovery files separately
from pathlib import Path

folder = Path("nse_data/news")
files = list(folder.glob("*.csv"))

frames = []

for file in files:
    try:
        data = pd.read_csv(file)
        data.columns = data.columns.str.strip()

        required = {"DATE", "DocumentIdentifier", "V2Tone"}

        if required.issubset(data.columns):
            frames.append(data[["DATE", "DocumentIdentifier", "V2Tone"]])

    except Exception as e:
        print("Error:", file.name, e)

all_news = pd.concat(frames, ignore_index=True)

duplicates = all_news[
    all_news.duplicated("DocumentIdentifier", keep=False)
]

summary = duplicates.groupby("DocumentIdentifier").agg(
    occurrences=("DocumentIdentifier", "size"),
    different_dates=("DATE", "nunique"),
    different_tones=("V2Tone", "nunique")
)

print("TOTAL RAW ROWS:", len(all_news))
print("UNIQUE URLS:", all_news["DocumentIdentifier"].nunique())
print("DUPLICATE ROWS:", len(duplicates))

print(
    "URLs with conflicting dates:",
    (summary["different_dates"] > 1).sum()
)

print(
    "URLs with conflicting tones:",
    (summary["different_tones"] > 1).sum()
)

print("\nDuplicate occurrence distribution:")
print(summary["occurrences"].value_counts().to_string())

