import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

required = {"DATE", "DocumentIdentifier", "V2Tone"}

all_data = []

print("\nNEWS FILE INVENTORY\n")

for file in sorted(folder.glob("*.csv")):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        if not required.issubset(df.columns):
            print(f"SKIPPED: {file.name} - Incorrect columns")
            continue

        df["source_file"] = file.name
        all_data.append(df[["DATE", "DocumentIdentifier", "V2Tone", "source_file"]])

        print(f"VALID: {file.name} | Rows: {len(df)}")

    except Exception as e:
        print(f"ERROR: {file.name} | {e}")

if not all_data:
    print("\nNo valid files found.")
    raise SystemExit

combined = pd.concat(all_data, ignore_index=True)

combined["timestamp_utc"] = pd.to_datetime(
    combined["DATE"].astype(str).str.zfill(14),
    format="%Y%m%d%H%M%S",
    errors="coerce",
    utc=True
)

combined = combined.dropna(subset=["timestamp_utc"])

print("\nTOTAL VALID ROWS:", len(combined))
print("UNIQUE URLS:", combined["DocumentIdentifier"].nunique())
print("DUPLICATE URL ROWS:", combined.duplicated("DocumentIdentifier").sum())
print("FIRST DATE:", combined["timestamp_utc"].min())
print("LAST DATE:", combined["timestamp_utc"].max())

print("\nRECOVERY FILES:")
for name in [
    "reliance_news_feb_missing.csv",
    "reliance_news_july_2025.csv",
    "reliance_news_august_2025.csv",
    "reliance_news_september_missing.csv"
]:
    print(name, "FOUND" if (folder / name).exists() else "NOT FOUND")

