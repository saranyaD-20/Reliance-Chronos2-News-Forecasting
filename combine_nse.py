
import pandas as pd
import glob
import os

files = glob.glob("nse_data/*.csv")
dataframes = []

for file in files:
    df = pd.read_csv(file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Remove spaces from text columns
    df["Symbol"] = df["Symbol"].astype(str).str.strip()
    df["Series"] = df["Series"].astype(str).str.strip()

    dataframes.append(df)

# Combine all files
combined_df = pd.concat(dataframes, ignore_index=True)

# Keep only RELIANCE EQ records
combined_df = combined_df[
    (combined_df["Symbol"] == "RELIANCE") &
    (combined_df["Series"] == "EQ")
].copy()

# Convert dates
combined_df["Date"] = pd.to_datetime(
    combined_df["Date"],
    format="%d-%b-%Y",
    errors="coerce"
)

# Remove commas and convert closing prices to numbers
combined_df["Close Price"] = pd.to_numeric(
    combined_df["Close Price"].astype(str).str.replace(",", "", regex=False),
    errors="coerce"
)

# Remove invalid records
combined_df = combined_df.dropna(
    subset=["Date", "Close Price"]
)

# Remove duplicate dates
combined_df = combined_df.drop_duplicates(
    subset=["Date"],
    keep="first"
)

# Sort dates
combined_df = combined_df.sort_values("Date")

# Select required columns
clean_df = combined_df[
    ["Date", "Symbol", "Series", "Close Price"]
]

# Save output
os.makedirs("results", exist_ok=True)

clean_df.to_csv(
    "results/reliance_combined_clean.csv",
    index=False
)

print("\nDataset combined successfully!")
print("Total records:", len(clean_df))
print("First date:", clean_df["Date"].min())
print("Last date:", clean_df["Date"].max())
print("\nSeries count:")
print(clean_df["Series"].value_counts())
print("\nMissing values:")
print(clean_df.isnull().sum())
