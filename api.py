from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import os
import secrets
import subprocess
import sys
import pandas as pd
from threading import Lock
from supabase_client import supabase
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

WINDMILL_API_TOKEN = os.getenv("WINDMILL_API_TOKEN")

RESULTS_DIR = BASE_DIR / "results"
METRICS_FILE = RESULTS_DIR / "benchmark_metrics_revised_corrected.csv"
PREDICTIONS_FILE = RESULTS_DIR / "testing_model_predictions_corrected.csv"
BENCHMARK_SCRIPT = BASE_DIR / "run_benchmarks_corrected.py"
# FASTAPI APPLICATION
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
        "http://127.0.0.1:5174"
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
    "forecasts_synced": None
}

execution_lock = Lock()


def update_execution(**kwargs):
    with execution_lock:
        execution.update(kwargs)


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
    authorization: str = Header(default="")
):
    if not WINDMILL_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="API token is not configured"
        )

    scheme, _, supplied_token = authorization.partition(" ")

    if (
        scheme.lower() != "bearer"
        or not secrets.compare_digest(
            supplied_token,
            WINDMILL_API_TOKEN
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token"
        )

    return True
# MANUAL SUPABASE SYNC ENDPOINTS
@app.post("/sync-supabase")
def sync_supabase(token: None = Depends(verify_windmill_token)):
    try:
        count = sync_metrics_to_supabase()

        return {
            "status": "success",
            "message": "Benchmark metrics synchronized with Supabase.",
            "records_synced": count
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


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
        raise HTTPException(status_code=500, detail=str(error))


# BENCHMARK EXECUTION
@app.post("/run-benchmark")
def start_benchmark(token: None = Depends(verify_windmill_token)):

    try:
        update_execution(
            status="running",
            message="Chronos-2 benchmark is running...",
            started_at=datetime.now().astimezone().isoformat(),
            completed_at=None,
            error=None,
            metrics_synced=None,
            forecasts_synced=None
        )

        if not BENCHMARK_SCRIPT.exists():
            raise FileNotFoundError(
                "run_benchmarks_corrected.py was not found."
            )

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            [sys.executable, str(BENCHMARK_SCRIPT)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            check=True
        )

        metrics_count = sync_metrics_to_supabase()
        forecasts_count = sync_forecasts_to_supabase()

        update_execution(
            status="completed",
            message="Benchmark completed and Supabase synchronization successful.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=None,
            metrics_synced=metrics_count,
            forecasts_synced=forecasts_count
        )

    except subprocess.CalledProcessError as error:

        error_message = (
            error.stderr.strip() if error.stderr else str(error)
        )

        update_execution(
            status="failed",
            message="Benchmark execution failed.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=error_message[-4000:]
        )

    except Exception as error:

        update_execution(
            status="failed",
            message="Benchmark or Supabase synchronization failed.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=str(error)[-4000:]
        )


# ROOT
@app.get("/")
def home():
    return {
        "message": "Reliance Stock Forecasting API",
        "status": "running",
        "version": "1.1.0"
    }


# HEALTH CHECK
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# RUN BENCHMARK
@app.post("/run-benchmark")
def start_benchmark():

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
            "forecasts_synced": None
        })

    thread = Thread(target=run_benchmark, daemon=True)
    thread.start()

    return {
        "message": "Benchmark started. Results will synchronize with Supabase.",
        "status": "running"
    }


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
        raise HTTPException(status_code=500, detail=str(error))


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
        raise HTTPException(status_code=500, detail=str(error))


# QUESTION AND ANSWER
class QuestionRequest(BaseModel):
    question: str


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

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))