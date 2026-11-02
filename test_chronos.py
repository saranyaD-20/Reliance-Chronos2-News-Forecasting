import torch
from chronos import Chronos2Pipeline

print("Loading Amazon Chronos-2...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2",
    device_map="cpu"
)

print("Model loaded successfully!")

context = torch.tensor([
    1221.25, 1241.80, 1251.15, 1218.00,
    1240.85, 1265.50, 1270.20, 1260.00
], dtype=torch.float32)

quantiles, median = pipeline.predict_quantiles(
    [context],
    prediction_length=1,
    quantile_levels=[0.5]
)

forecast = median[0][0, 0].item()

print("\nChronos-2 one-day forecast:")
print(f"Predicted price: Rs. {forecast:.2f}")
