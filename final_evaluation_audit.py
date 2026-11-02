import pandas as pd
import numpy as np

pred = pd.read_csv("results/testing_model_predictions.csv")
data = pd.read_csv("results/final_next_day_forecasting_dataset.csv")

pred["forecast_date"] = pd.to_datetime(pred["forecast_date"])
data["forecast_date"] = pd.to_datetime(data["forecast_date"])

test_data = data[data["forecast_date"] >= "2026-07-01"].copy()

print("FINAL MODEL EVALUATION AUDIT")
print("-" * 45)

print("Prediction records:", len(pred))
print("Expected testing records:", len(test_data))
print("Duplicate forecast dates:", pred["forecast_date"].duplicated().sum())

date_match = (
    pred["forecast_date"].reset_index(drop=True)
    == test_data["forecast_date"].reset_index(drop=True)
).all()

print("Forecast dates match:", date_match)

print("Actual target prices match:", np.allclose(
    pred["target_close"], test_data["target_close"]
))

print("Previous closing prices match:", np.allclose(
    pred["previous_close"], test_data["previous_close"]
))

print("Unavailable testing news:",
      test_data["coverage_status"].eq("unavailable").sum())

actual = pred["target_close"].to_numpy()
previous = pred["previous_close"].to_numpy()

models = {
    "Naive": pred["naive_prediction"].to_numpy(),
    "C0 Chronos-2 Price Only": pred["c0_prediction"].to_numpy(),
    "C1 Chronos-2 Price + News": pred["c1_prediction"].to_numpy()
}

actual_direction = np.sign(actual - previous)
results = []

for name, forecast in models.items():
    predicted_direction = np.sign(forecast - previous)
    calls = predicted_direction != 0

    accuracy = (
        np.mean(actual_direction[calls] == predicted_direction[calls]) * 100
        if calls.sum() else np.nan
    )

    results.append({
        "Model": name,
        "MAE": np.mean(np.abs(actual - forecast)),
        "RMSE": np.sqrt(np.mean((actual - forecast) ** 2)),
        "Directional_Accuracy": accuracy,
        "Directional_Calls": int(calls.sum())
    })

metrics = pd.DataFrame(results)

print("\nREVISED PERFORMANCE METRICS")
print(metrics.to_string(index=False))

metrics.to_csv("results/benchmark_metrics_revised.csv", index=False)

print("\nSaved: results/benchmark_metrics_revised.csv")

if date_match:
    print("\nAUDIT PASSED: Forecast dates match.")
else:
    print("\nAUDIT FAILED: Forecast dates do not match.")
