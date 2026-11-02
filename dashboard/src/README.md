# FORECAST-001: News-Augmented Reliance Stock Benchmark

## Project Overview

This project evaluates whether historical financial news features improve next-day Reliance Industries stock price forecasting using Amazon Chronos-2.

The benchmark compares three forecasting approaches:

- **Naive baseline:** Uses the previous trading day's closing price.
- **C0 – Price Only:** Uses historical Reliance closing prices with Chronos-2.
- **C1 – Price + News:** Uses historical closing prices and past-only news features with Chronos-2.

This is a research benchmark, not an investment recommendation.

## Technology Stack

### Backend and Machine Learning
- Python
- FastAPI
- Chronos-2 (`amazon/chronos-2`)
- PyTorch
- Pandas and NumPy
- Matplotlib

### Frontend
- React
- TypeScript
- Vite
- Recharts

### Data Sources
- NSE Reliance historical equity data
- GDELT Global Knowledge Graph news data

## Project Structure

```text
Reliance_Forecasting_Project/
├── dashboard/
│   ├── public/
│   └── src/
├── nse_data/
│   └── news/
├── results/
│   ├── final_next_day_forecasting_dataset_corrected.csv
│   ├── testing_model_predictions_corrected.csv
│   ├── benchmark_metrics_revised_corrected.csv
│   └── T1-T6 verification reports
├── api.py
├── run_benchmarks_corrected.py
├── create_final_dataset_corrected.py
├── align_historical_news.py
├── align_testing_news_corrected.py
└── requirements.txt
```

## Dataset

- Stock: Reliance Industries Limited
- Exchange: NSE
- Series: EQ
- Price field: Close Price
- Currency: INR
- Historical period: January 2025 – June 2026
- Testing period: July 2026 – September 2026

The corrected forecasting dataset contains 433 rows:
- 369 historical records
- 64 testing forecast origins

News features:
- Daily article count
- Log-transformed article count using `log1p`
- Mean GDELT V2Tone

News features are aligned to NSE trading-day forecast origins using the 18:00 Asia/Kolkata cutoff.

## Model Configuration

- Model: `amazon/chronos-2`
- Revision: `29ec3766d36d6f73f0696f85560a422f50e8498c`
- Prediction length: 1 trading day
- Quantile level: 0.5
- Evaluation: Expanding historical context
- Fine-tuning: None

## Benchmark Results

| Model | MAE | RMSE | Directional Accuracy |
|---|---:|---:|---:|
| Naive | 12.4062 | 15.4797 | N/A |
| C0 – Price Only | 12.4710 | 15.9118 | 50.00% |
| C1 – Price + News | 12.7798 | 15.9510 | 50.00% |

Adding news increased MAE by approximately 2.48% compared with the price-only Chronos-2 model.

The Naive baseline achieved the lowest MAE and RMSE in this evaluation.

## Local Setup

### 1. Create a Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start the FastAPI backend

```powershell
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Backend address:

`http://127.0.0.1:8000`

### 4. Start the dashboard

Open another terminal:

```powershell
cd dashboard
npm install
npm run dev
```

Open the local Vite address displayed in the terminal.

## Important API Endpoints

- `/health` – Backend health check
- `/metrics` – Benchmark metrics
- `/predictions` – Forecast predictions
- `/execution-status` – Benchmark execution status
- `/run-benchmark` – Start benchmark execution
- `/ask` – Benchmark question-answer endpoint

## Verification

Verification reports are maintained in the `results/` folder:

- T1 – NSE stock data verification
- T2 – News inventory, coverage and leakage verification
- T3 – Dataset integrity verification
- T4 – Chronos benchmark verification
- T5 – Backend API verification
- T6 – Frontend verification

## Known Limitations

- Historical news coverage contains documented gaps.
- Reliance-specific organization matching against the original GDELT organization fields has not been independently verified.
- The current backend uses FastAPI.
- Supabase and Windmill integrations are not yet implemented.
- Public HTTPS deployment and 72-hour pilot retention are not verified.
- The dashboard question-answer feature uses predefined benchmark responses rather than a generative AI model.

## Disclaimer

This project is intended for research and educational evaluation only. Forecasts are not financial advice and should not be used as the sole basis for investment decisions.
