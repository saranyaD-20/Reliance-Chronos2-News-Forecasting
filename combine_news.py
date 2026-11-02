
import pandas as pd
from pathlib import Path

# Folder containing weekly GDELT CSV files
news_folder = Path("nse_data/news")

# Find weekly files only; exclude test CSV files
files = sorted(
    list(news_folder.glob("reliance_news_2025_week*.csv")) +
    list(news_folder.glob("reliance_news_2026_week*.csv"))
)

if not files:
    raise FileNotFoundError("No weekly news CSV files found.")

all_data = []

for file in files:
    print(f"Reading: {file.name}")

    df = pd.read_csv(file)

    # Clean column names
    df.columns = df.columns.str.strip()

    required_columns = [
        "DATE",
        "DocumentIdentifier",
        "V2Tone"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        print(f"Skipping {file.name}: missing columns {missing}")
        continue

    # Keep required original fields
    df = df[required_columns].copy()

    # Record the source weekly file
    df["source_file"] = file.name

    all_data.append(df)

if not all_data:
    raise ValueError("No valid weekly CSV files were found.")

# Combine all weekly datasets
combined = pd.concat(all_data, ignore_index=True)

# Save combined raw news data
output_folder = Path("results")
output_folder.mkdir(exist_ok=True)

output_file = output_folder / "reliance_news_combined_raw.csv"

combined.to_csv(output_file, index=False)

print("\nCOMBINATION COMPLETED")
print("Files processed:", len(all_data))
print("Total articles:", len(combined))
print("Output file:", output_file)
print("\nFirst five records:")
print(combined.head())
