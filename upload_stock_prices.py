import pandas as pd
from supabase_client import supabase

csv_path = "results/reliance_combined_clean.csv"
df = pd.read_csv(csv_path)

records = [
    {
        "trading_date": str(row["Date"])[:10],
        "close_price": float(row["Close Price"])
    }
    for _, row in df.iterrows()
]

for start in range(0, len(records), 500):
    batch = records[start:start + 500]
    supabase.table("stock_prices").insert(batch).execute()

print(f"Successfully uploaded {len(records)} stock-price records.")
