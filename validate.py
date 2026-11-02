
import pandas as pd

# 1. Read NSE dataset
df = pd.read_csv("01-01-2025-TO-30-06-2025-RELIANCE-ALL-N.csv")

# 2. Remove extra spaces from column names
df.columns = df.columns.str.strip()

# 3. Keep only Reliance equity records
df = df[
    (df["Symbol"] == "RELIANCE") &
    (df["Series"] == "EQ")
].copy()

# 4. Convert Date into datetime format
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%b-%Y"
)

# 5. Convert Close Price into numeric values
df["Close Price"] = pd.to_numeric(
    df["Close Price"],
    errors="coerce"
)

# 6. Sort dates from oldest to newest
df = df.sort_values("Date")

# 7. Remove duplicate dates
df = df.drop_duplicates(subset=["Date"])

# 8. Select required columns
clean_df = df[
    ["Date", "Symbol", "Series", "Close Price"]
].copy()

# 9. Check final dataset
print("\nClean Dataset:")
print(clean_df.head())

print("\nDataset Information:")
print(clean_df.info())

print("\nMissing Values:")
print(clean_df.isnull().sum())

print("\nDate Range:")
print(clean_df["Date"].min())
print(clean_df["Date"].max())

# 10. Save cleaned dataset
clean_df.to_csv(
    "results/reliance_clean_jan_jun_2025.csv",
    index=False
)

print("\nClean dataset saved successfully!")
