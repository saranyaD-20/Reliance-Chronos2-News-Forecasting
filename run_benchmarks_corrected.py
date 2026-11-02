
import pandas as pd
import numpy as np
import torch

from chronos import Chronos2Pipeline
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

DATASET_FILE = RESULTS_DIR / "final_next_day_forecasting_dataset_corrected.csv"

PREDICTIONS_FILE = RESULTS_DIR / "testing_model_predictions_corrected.csv"

METRICS_FILE = RESULTS_DIR / "benchmark_metrics_corrected.csv"

REVISED_METRICS_FILE = RESULTS_DIR / "benchmark_metrics_revised_corrected.csv"


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

print("Loading Reliance forecasting dataset...")

df = pd.read_csv(DATASET_FILE)

df["forecast_date"] = pd.to_datetime(df["forecast_date"])

required_columns = [
    "forecast_date",
    "target_date",
    "previous_close",
    "target_close",
    "log_article_count",
    "mean_tone"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required dataset columns: {missing_columns}"
    )

# Select testing forecast origins
test = df[
    df["forecast_date"] >= "2026-07-01"
].copy()

test = test.sort_values(
    "forecast_date"
).reset_index(drop=True)

if test.empty:
    raise ValueError("No testing records found.")

print("Testing forecast dates:", len(test))


# --------------------------------------------------
# 3. LOAD CHRONOS-2
# --------------------------------------------------

print("\nLoading Chronos-2...")

CHRONOS_MODEL_ID = "amazon/chronos-2"

CHRONOS_REVISION = "29ec3766d36d6f73f0696f85560a422f50e8498c"

pipeline = Chronos2Pipeline.from_pretrained(
    CHRONOS_MODEL_ID,
    revision=CHRONOS_REVISION,
    device_map="cpu"
)

print("Chronos-2 model loaded successfully.")
print("Model ID:", CHRONOS_MODEL_ID)
print("Model revision:", CHRONOS_REVISION)

print("Chronos-2 model loaded successfully.")


# --------------------------------------------------
# 4. BUILD PAST-ONLY INPUTS
# --------------------------------------------------

c0_inputs = []
c1_inputs = []

print("\nPreparing forecasting inputs...")

for _, row in test.iterrows():

    history = df[
        df["forecast_date"] <= row["forecast_date"]
    ].sort_values("forecast_date")

    prices = history["previous_close"].to_numpy(
        dtype=np.float32
    )

    counts = history["log_article_count"].to_numpy(
        dtype=np.float32
    )

    tones = history["mean_tone"].to_numpy(
        dtype=np.float32
    )

    # C0: Price-only input
    c0_inputs.append({
        "target": torch.tensor(prices)
    })

    # C1: Price + news input
    c1_inputs.append({
        "target": torch.tensor(prices),
        "past_covariates": {
            "log_article_count": torch.tensor(counts),
            "mean_tone": torch.tensor(tones)
        }
    })


# --------------------------------------------------
# 5. C0: CHRONOS-2 PRICE-ONLY FORECAST
# --------------------------------------------------

print("\nRunning C0: Chronos-2 Price Only...")

_, c0_predictions = pipeline.predict_quantiles(
    c0_inputs,
    prediction_length=1,
    quantile_levels=[0.5]
)

c0_values = np.array([
    prediction[0, 0].item()
    for prediction in c0_predictions
])

print("C0 forecasting completed.")


# --------------------------------------------------
# 6. C1: CHRONOS-2 PRICE + NEWS FORECAST
# --------------------------------------------------

print("\nRunning C1: Chronos-2 Price + News...")

_, c1_predictions = pipeline.predict_quantiles(
    c1_inputs,
    prediction_length=1,
    quantile_levels=[0.5]
)

c1_values = np.array([
    prediction[0, 0].item()
    for prediction in c1_predictions
])

print("C1 forecasting completed.")


# --------------------------------------------------
# 7. NAIVE BASELINE
# --------------------------------------------------

naive_values = test[
    "previous_close"
].to_numpy(dtype=float)

actual = test[
    "target_close"
].to_numpy(dtype=float)

previous = test[
    "previous_close"
].to_numpy(dtype=float)


# --------------------------------------------------
# 8. CALCULATE EVALUATION METRICS
# --------------------------------------------------

def calculate_metrics(model_name, predictions):

    # Mean Absolute Error
    mae = np.mean(
        np.abs(actual - predictions)
    )

    # Root Mean Squared Error
    rmse = np.sqrt(
        np.mean((actual - predictions) ** 2)
    )

    # Actual and predicted price directions
    actual_direction = np.sign(
        actual - previous
    )

    predicted_direction = np.sign(
        predictions - previous
    )

    # Count predictions that indicate an upward or
    # downward movement. Zero-change predictions
    # are not directional calls.
    directional_mask = predicted_direction != 0

    directional_calls = int(
        np.sum(directional_mask)
    )

    # Directional accuracy is N/A when there are
    # no directional predictions.
    if directional_calls == 0:

        directional_accuracy = np.nan

    else:

        directional_accuracy = np.mean(
            actual_direction[directional_mask]
            == predicted_direction[directional_mask]
        ) * 100

    return {
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "Directional_Accuracy": directional_accuracy,
        "Directional_Calls": directional_calls
    }


# --------------------------------------------------
# 9. GENERATE MODEL COMPARISON
# --------------------------------------------------

metrics = pd.DataFrame([

    calculate_metrics(
        "Naive",
        naive_values
    ),

    calculate_metrics(
        "C0 Chronos-2 Price Only",
        c0_values
    ),

    calculate_metrics(
        "C1 Chronos-2 Price + News",
        c1_values
    )

])

# Calculate relative MAE change from C0 to C1
c0_mae = metrics.loc[
    metrics["Model"] == "C0 Chronos-2 Price Only",
    "MAE"
].iloc[0]

c1_mae = metrics.loc[
    metrics["Model"] == "C1 Chronos-2 Price + News",
    "MAE"
].iloc[0]

relative_change = (
    (c0_mae - c1_mae) / c0_mae
) * 100


# --------------------------------------------------
# 10. SAVE TESTING PREDICTIONS
# --------------------------------------------------

predictions = test[
    [
        "forecast_date",
        "target_date",
        "previous_close",
        "target_close"
    ]
].copy()

predictions["naive_prediction"] = naive_values

predictions["c0_prediction"] = c0_values

predictions["c1_prediction"] = c1_values

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

predictions.to_csv(
    PREDICTIONS_FILE,
    index=False
)


# --------------------------------------------------
# 11. SAVE REVISED METRICS
# --------------------------------------------------

# Both files use the same dashboard-compatible format.
metrics.to_csv(
    METRICS_FILE,
    index=False
)

metrics.to_csv(
    REVISED_METRICS_FILE,
    index=False
)


# --------------------------------------------------
# 12. DISPLAY FINAL RESULTS
# --------------------------------------------------

print("\n" + "=" * 65)
print("RELIANCE STOCK FORECASTING BENCHMARK RESULTS")
print("=" * 65)

print(
    metrics.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\nRelative MAE change (C0 to C1):")

print(f"{relative_change:.2f}%")

if relative_change > 0:
    print("Adding news reduced MAE.")

elif relative_change < 0:
    print("Adding news increased MAE.")

else:
    print("Adding news made no difference to MAE.")


# --------------------------------------------------
# 13. OUTPUT FILES
# --------------------------------------------------

print("\nSaved output files:")

print(PREDICTIONS_FILE)

print(METRICS_FILE)

print(REVISED_METRICS_FILE)

print("\nBenchmark execution completed.")


