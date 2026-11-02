import pandas as pd

historical = pd.read_csv("results/historical_stock_news.csv")
testing = pd.read_csv("results/testing_stock_news.csv")

print("HISTORICAL UNMATCHED DATES")
missing = historical[historical["article_count"].isna()]

print(missing[["Date", "Close Price"]].to_string(index=False))
print("\nTotal:", len(missing))

print("\nTESTING PERIOD")
print("First date:", testing["Date"].min())
print("Last date:", testing["Date"].max())
print("Trading days:", len(testing))
