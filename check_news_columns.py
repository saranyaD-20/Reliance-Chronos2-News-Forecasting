import pandas as pd
from pathlib import Path

folder = Path("nse_data/news")

required_columns = {
    "DATE",
    "DocumentIdentifier",
    "V2Tone"
}

for file in sorted(folder.glob("*.csv")):
    try:
        df = pd.read_csv(file, nrows=5)
        columns = set(df.columns.str.strip())

        if required_columns.issubset(columns):
            print(f"VALID: {file.name}")
        else:
            print(f"INVALID: {file.name}")
            print("  Found columns:", list(df.columns))

    except Exception as e:
        print(f"ERROR: {file.name} - {e}")
