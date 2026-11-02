import pandas as pd

df = pd.read_csv("results/reliance_news_cleaned.csv")

print("Cleaned records:", len(df))
print("Unique URLs:", df["DocumentIdentifier"].nunique())

# Check timestamp parsing in the original raw files
from pathlib import Path

folder = Path("nse_data/news")
frames = []

for file in folder.glob("*.csv"):
    try:
        data = pd.read_csv(file)
        data.columns = data.columns.str.strip()

        required = {"DATE", "DocumentIdentifier", "V2Tone"}

        if required.issubset(data.columns):
            frames.append(data[["DATE", "DocumentIdentifier", "V2Tone"]])
    except Exception:
        pass

raw = pd.concat(frames, ignore_index=True)
raw = raw.drop_duplicates("DocumentIdentifier", keep="first")

parsed = pd.to_datetime(
    raw["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    errors="coerce",
    utc=True
)

print("\nUnique URLs before timestamp validation:", len(raw))
print("Invalid timestamps:", parsed.isna().sum())
print("Valid timestamps:", parsed.notna().sum())

print("\nInvalid timestamp examples:")
print(raw.loc[parsed.isna(), ["DATE", "DocumentIdentifier"]].head(10).to_string(index=False))
