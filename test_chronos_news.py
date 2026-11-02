import pandas as pd
import numpy as np
from chronos import Chronos2Pipeline

df = pd.read_csv("results/final_next_day_forecasting_dataset.csv")
df["forecast_date"] = pd.to_datetime(df["forecast_date"])

# Use the first testing forecast origin
test_dates = df[df["forecast_date"] >= "2026-07-01"]
forecast_date = test_dates.iloc[0]["forecast_date"]

# Use only information available on or before this forecast date
history = df[df["forecast_date"] <= forecast_date].copy()

prices = history["previous_close"].to_numpy(dtype=np.float32)

article_count = history["article_count"].to_numpy(dtype=np.float32)
mean_tone = history["mean_tone"].to_numpy(dtype=np.float32)

# Preserve missing historical news as NaN
print("Forecast origin:", forecast_date.date())
print("Price observations:", len(prices))
print("News observations:", len(article_count))
print("Missing news values:", np.isnan(article_count).sum())

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2",
    device_map="cpu"
)

inputs = [{
    "target": prices,
    "past_covariates": {
        "article_count": article_count,
        "mean_tone": mean_tone
    }
}]

quantiles, median = pipeline.predict_quantiles(
    inputs,
    prediction_length=1,
    quantile_levels=[0.5]
)

prediction = median[0][0, 0].item()

print("\nNEWS-AUGMENTED FORECAST")
print("Predicted next closing price: Rs.", round(prediction, 2))
