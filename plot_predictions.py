import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/testing_model_predictions.csv")
df["target_date"] = pd.to_datetime(df["target_date"])

plt.figure(figsize=(14, 7))

plt.plot(df["target_date"], df["target_close"],
         label="Actual Close", linewidth=2)

plt.plot(df["target_date"], df["naive_prediction"],
         label="Naive Prediction", linestyle="--")

plt.plot(df["target_date"], df["c0_prediction"],
         label="Chronos-2 Price Only", linestyle="--")

plt.plot(df["target_date"], df["c1_prediction"],
         label="Chronos-2 + News", linestyle="--")

plt.title("Reliance Industries: Actual vs Predicted Closing Prices")
plt.xlabel("Trading Date")
plt.ylabel("Closing Price (INR)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "results/actual_vs_predicted.png",
    dpi=300
)

plt.show()

print("Chart saved: results/actual_vs_predicted.png")
