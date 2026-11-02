import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("results/testing_model_predictions.csv")

df["naive_error"] = abs(
    df["target_close"] - df["naive_prediction"]
)

df["c0_error"] = abs(
    df["target_close"] - df["c0_prediction"]
)

df["c1_error"] = abs(
    df["target_close"] - df["c1_prediction"]
)

plt.figure(figsize=(14, 6))

plt.plot(df["target_date"], df["naive_error"], label="Naive Error")
plt.plot(df["target_date"], df["c0_error"], label="Chronos-2 Price Error")
plt.plot(df["target_date"], df["c1_error"], label="Chronos-2 + News Error")

plt.title("Reliance Forecasting: Absolute Error Comparison")
plt.xlabel("Trading Date")
plt.ylabel("Absolute Error (INR)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("results/model_error_comparison.png", dpi=300)
plt.show()

print("Error comparison chart saved successfully.")
