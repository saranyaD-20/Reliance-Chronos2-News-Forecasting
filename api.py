from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
import os
import secrets
import subprocess
import sys
import pandas as pd
from threading import Lock, Thread
from datetime import datetime
from supabase_client import supabase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

METRICS_FILE = RESULTS_DIR / "benchmark_metrics_revised_corrected.csv"
PREDICTIONS_FILE = RESULTS_DIR / "testing_model_predictions_corrected.csv"

BENCHMARK_SCRIPT = BASE_DIR / "run_benchmarks_corrected.py"
app = FastAPI(
    title="Reliance Stock Forecasting API",
    description="Chronos-2 stock forecasting benchmark API",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://reliance-chronos-dashboard.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# EXECUTION STATUS
execution = {
    "status": "idle",
    "message": "Ready to run the benchmark.",
    "started_at": None,
    "completed_at": None,
    "error": None,
    "metrics_synced": None,
    "forecasts_synced": None,
    "news_synced": None,
}




execution_lock = Lock()


def update_execution(**kwargs):
    # Update local execution status
    with execution_lock:
        execution.update(kwargs)

    # Update Supabase benchmark_runs table
    try:
        response = (
            supabase
            .table("benchmark_runs")
            .select("id")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if response.data:
            run_id = response.data[0]["id"]

            supabase.table("benchmark_runs").update(
                kwargs
            ).eq("id", run_id).execute()

    except Exception as error:
        print(f"Supabase execution status update error: {error}")


@app.get("/health")
def health():
    return {"status": "healthy"}

# SUPABASE SYNC FUNCTIONS
def sync_metrics_to_supabase():

    if not METRICS_FILE.exists():
        raise FileNotFoundError("Benchmark metrics file not found.")

    df = pd.read_csv(METRICS_FILE)

    required = ["Model", "MAE", "RMSE", "Directional_Accuracy"]

    if not all(column in df.columns for column in required):
        raise ValueError("Metrics CSV has missing columns.")

    if df.empty:
        raise ValueError("Metrics CSV is empty.")

    records = []

    for _, row in df.iterrows():
        records.append({
            "model_name": str(row["Model"]),
            "mae": float(row["MAE"]),
            "rmse": float(row["RMSE"]),
            "directional_accuracy": (
                float(row["Directional_Accuracy"])
                if pd.notna(row["Directional_Accuracy"])
                else None
            )
        })

    supabase.table("benchmark_metrics").upsert(records).execute()

    return len(records)


def sync_forecasts_to_supabase():

    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError("Forecast predictions file not found.")

    df = pd.read_csv(PREDICTIONS_FILE)

    required = [
        "forecast_date",
        "target_date",
        "previous_close",
        "target_close",
        "naive_prediction",
        "c0_prediction",
        "c1_prediction"
    ]

    if not all(column in df.columns for column in required):
        raise ValueError("Prediction CSV has missing columns.")

    if df.empty:
        raise ValueError("Prediction CSV is empty.")

    records = []

    for _, row in df.iterrows():
        records.append({
            "forecast_date": str(row["forecast_date"]),
            "target_date": str(row["target_date"]),
            "previous_close": float(row["previous_close"]),
            "target_close": float(row["target_close"]),
            "naive_prediction": float(row["naive_prediction"]),
            "c0_prediction": float(row["c0_prediction"]),
            "c1_prediction": float(row["c1_prediction"])
        })

    supabase.table("forecasts").upsert(records).execute()

    return len(records)


def verify_windmill_token(
    authorization: str = Header(default="", alias="Authorization")
):
    expected_token = (WINDMILL_API_TOKEN or "").strip()

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API token is not configured"
        )

    supplied_header = authorization.strip()
    scheme, separator, supplied_token = supplied_header.partition(" ")

    supplied_token = supplied_token.strip()

    if (
        scheme.lower() != "bearer"
        or not separator
        or not secrets.compare_digest(
            supplied_token,
            expected_token
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token"
        )

    return True

@app.get("/auth-check")
def auth_check(token: None = Depends(verify_windmill_token)):
    return {
        "status": "success",
        "message": "API authentication is working."
    }
# MANUAL SUPABASE SYNC ENDPOINTS
@app.get("/supabase-forecasts")
def get_supabase_forecasts():
    try:
        response = (
            supabase
            .table("forecasts")
            .select("*")
            .execute()
        )

        return {
            "status": "success",
            "count": len(response.data),
            "data": response.data
        }

    except Exception as e:
        print(f"Supabase forecasts error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/sync-forecasts")
def sync_forecasts(token: None = Depends(verify_windmill_token)):
    try:
        count = sync_forecasts_to_supabase()

        return {
            "status": "success",
            "message": "Forecasts synchronized with Supabase.",
            "records_synced": count
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail="An internal server error occurred. Please try again.")


# BENCHMARK EXECUTION


# ROOT
@app.get("/")
def home():
    return {
        "message": "Reliance Stock Forecasting API",
        "status": "running",
        "version": "1.1.0"
    }


@app.get("/execution-status")
def execution_status():
    with execution_lock:
        return execution.copy()



# RUN BENCHMARK
@app.post("/run-benchmark")
def start_benchmark(
    x_api_key: str = Header(...)
):
    expected_key = os.getenv("API_SECRET_KEY")

    if not expected_key or not secrets.compare_digest(
        x_api_key,
        expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )

    with execution_lock:

        if execution["status"] == "running":
            raise HTTPException(
                status_code=409,
                detail="Benchmark is already running."
            )

        execution.update({
            "status": "running",
            "message": "Benchmark execution started.",
            "started_at": datetime.now().astimezone().isoformat(),
            "completed_at": None,
            "error": None,
            "metrics_synced": None,
            "forecasts_synced": None,
            "news_synced": None,
        })

    thread = Thread(
        target=run_benchmark,
        daemon=True
    )

    thread.start()

    return {
        "message": "Benchmark started successfully.",
        "status": "running"
    }
def run_benchmark():
    try:
        print("STEP 1: Starting benchmark")

        update_execution(
            status="running",
            message="Running Chronos-2 benchmark..."
        )

        print("STEP 2: Running Python benchmark script")

        result = subprocess.run(
            [sys.executable, str(BENCHMARK_SCRIPT)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )

        print("STEP 3: Benchmark script completed successfully")
        print(result.stdout)

        print("STEP 4: Syncing metrics to Supabase")
        metrics_count = sync_metrics_to_supabase()

        print("STEP 5: Syncing forecasts to Supabase")
        forecasts_count = sync_forecasts_to_supabase()

        print("STEP 6: Syncing news to Supabase")
        news_count = sync_news_to_supabase()

        print("STEP 7: Updating status to COMPLETED")

        update_execution(
            status="running",
            message="Benchmark execution started.",
            started_at=datetime.now().astimezone().isoformat(),
            completed_at=None
        )

        print("STEP 8: Benchmark fully completed")

    except subprocess.CalledProcessError as error:

        print("BENCHMARK SCRIPT ERROR")
        print("STDOUT:", error.stdout)
        print("STDERR:", error.stderr)

        update_execution(
            status="failed",
            message="Benchmark script failed.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=error.stderr or str(error)
        )

    except Exception as error:

        print("BENCHMARK ERROR:", str(error))

        update_execution(
            status="failed",
            message="Benchmark execution or synchronization failed.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=str(error)
        )

def sync_news_to_supabase():
    NEWS_FILE = BASE_DIR / "results" / "testing_news_forecast_features_corrected.csv"

    if not NEWS_FILE.exists():
        raise FileNotFoundError(f"News file not found: {NEWS_FILE}")

    df = pd.read_csv(NEWS_FILE)

    required = [
        "forecast_date",
        "article_count",
        "mean_tone",
        "coverage_status"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing news columns: {missing}")

    df = df[required].copy()
    df["trading_date"] = df["forecast_date"]

    records = (
        df.astype(object)
        .where(pd.notna(df), None)
        .to_dict(orient="records")
    )

    supabase.table("news_features").upsert(records).execute()

    return len(records)
# EXECUTION STATUS

@app.get("/execution-status")
def execution_status():
    with execution_lock:
        return execution.copy()


# METRICS
@app.get("/metrics")
def get_metrics(token: None = Depends(verify_windmill_token)):

    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Benchmark metrics file not found."
        )

    try:
        df = pd.read_csv(METRICS_FILE)

        required = [
            "Model",
            "MAE",
            "RMSE",
            "Directional_Accuracy",
            "Directional_Calls"
        ]

        missing = [column for column in required if column not in df.columns]

        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing columns: {missing}"
            )

        df = df[required]

        return df.astype(object).where(
            pd.notna(df), None
        ).to_dict(orient="records")

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(status_code=500, detail="An internal server error occurred. Please try again.")


# PREDICTIONS
@app.get("/predictions")
def get_predictions(token: None = Depends(verify_windmill_token)):

    if not PREDICTIONS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Testing predictions file not found."
        )

    try:
        df = pd.read_csv(PREDICTIONS_FILE)

        return df.astype(object).where(
            pd.notna(df), None
        ).to_dict(orient="records")

    except Exception as error:
        raise HTTPException(status_code=500, detail="An internal server error occurred. Please try again.")


# QUESTION AND ANSWER

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
        strip_whitespace=True
    )



@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.lower().strip()

    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Benchmark metrics are unavailable."
        )

    try:
        df = pd.read_csv(METRICS_FILE)

        naive = df[df["Model"] == "Naive"].iloc[0]
        c0 = df[df["Model"] == "C0 Chronos-2 Price Only"].iloc[0]
        c1 = df[df["Model"] == "C1 Chronos-2 Price + News"].iloc[0]

        if "best model" in question or "performed best" in question:
            best = df.loc[df["MAE"].idxmin()]
            answer = (
                f"{best['Model']} performed best based on MAE, "
                f"with an MAE of {best['MAE']:.4f}."
            )

        elif "news" in question or "improve" in question:
            change = ((c0["MAE"] - c1["MAE"]) / c0["MAE"]) * 100

            if change >= 0:
                answer = f"Adding news reduced MAE by {change:.2f}%."
            else:
                answer = (
                    f"Adding news increased MAE by {abs(change):.2f}%. "
                    "News did not improve MAE in this experiment."
                )

        elif "mae" in question:
            answer = (
                f"Naive MAE: {naive['MAE']:.4f}. "
                f"C0 MAE: {c0['MAE']:.4f}. "
                f"C1 MAE: {c1['MAE']:.4f}."
            )

        elif "rmse" in question:
            answer = (
                f"Naive RMSE: {naive['RMSE']:.4f}. "
                f"C0 RMSE: {c0['RMSE']:.4f}. "
                f"C1 RMSE: {c1['RMSE']:.4f}."
            )

        elif "direction" in question or "accuracy" in question:
            answer = (
                f"C0 directional accuracy: {c0['Directional_Accuracy']}%. "
                f"C1 directional accuracy: {c1['Directional_Accuracy']}%. "
                "Naive has no directional calls."
            )

        else:
            answer = (
                "I can answer questions about best model, MAE, RMSE, "
                "directional accuracy, and the impact of adding news."
            )

        return {
            "question": request.question,
            "answer": answer,
            "source": "Stored corrected benchmark metrics",
            "answer_type": "rule_based"
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again."
        )
@app.get("/supabase-metrics")
def get_supabase_metrics():
    try:
        response = (
            supabase
            .table("benchmark_metrics")
            .select("*")
            .execute()
        )

        return {
            "status": "success",
            "count": len(response.data),
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/supabase-news-features")
def get_supabase_news_features():
    try:
        response = supabase.table("news_features").select("*").execute()

        return {
            "status": "success",
            "count": len(response.data),
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
