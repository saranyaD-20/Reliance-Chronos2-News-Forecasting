
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from threading import Thread, Lock
import subprocess
import sys
import pandas as pd


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

RESULTS_DIR = BASE_DIR / "results"
METRICS_FILE = RESULTS_DIR / "benchmark_metrics_revised_corrected.csv"

PREDICTIONS_FILE = RESULTS_DIR / "testing_model_predictions_corrected.csv"

BENCHMARK_SCRIPT = BASE_DIR / "run_benchmarks_corrected.py"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Reliance Stock Forecasting API",
    description="Chronos-2 stock forecasting benchmark API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

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
    allow_headers=["*"],
)


# --------------------------------------------------
# EXECUTION STATUS
# --------------------------------------------------

execution = {
    "status": "idle",
    "message": "Ready to run the benchmark.",
    "started_at": None,
    "completed_at": None,
    "error": None
}

execution_lock = Lock()


# --------------------------------------------------
# HELPER: UPDATE EXECUTION STATUS
# --------------------------------------------------

def update_execution(**kwargs):

    with execution_lock:
        execution.update(kwargs)


# --------------------------------------------------
# BENCHMARK EXECUTION
# --------------------------------------------------

def run_benchmark():

    try:

        update_execution(
            status="running",
            message="Chronos-2 benchmark is running...",
            started_at=datetime.now().astimezone().isoformat(),
            completed_at=None,
            error=None
        )

        if not BENCHMARK_SCRIPT.exists():
            raise FileNotFoundError(
        "run_benchmarks_corrected.py was not found."
    )

        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        result = subprocess.run(
            [
                sys.executable,
                str(BENCHMARK_SCRIPT)
            ],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            check=True
        )

        update_execution(
            status="completed",
            message="Benchmark completed successfully.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=None
        )

    except subprocess.CalledProcessError as error:

        error_message = (
            error.stderr.strip()
            if error.stderr
            else str(error)
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
            message="An error occurred during benchmark execution.",
            completed_at=datetime.now().astimezone().isoformat(),
            error=str(error)
        )


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Reliance Stock Forecasting API",
        "status": "running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# RUN BENCHMARK
# --------------------------------------------------

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
            "error": None
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


# --------------------------------------------------
# EXECUTION STATUS
# --------------------------------------------------

@app.get("/execution-status")
def get_execution_status():

    with execution_lock:
        return execution.copy()


# --------------------------------------------------
# MODEL METRICS
# --------------------------------------------------

@app.get("/metrics")
def get_metrics():

    if not METRICS_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail="Benchmark metrics file not found."
        )

    try:

        df = pd.read_csv(METRICS_FILE)

        required_columns = [
            "Model",
            "MAE",
            "RMSE",
            "Directional_Accuracy",
            "Directional_Calls"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Metrics file has an unexpected format. "
                    f"Missing columns: {missing_columns}"
                )
            )

        df = df[required_columns]

        records = df.astype(object).where(
            pd.notna(df),
            None
        ).to_dict(orient="records")

        return records

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# --------------------------------------------------
# TESTING PREDICTIONS
# --------------------------------------------------

@app.get("/predictions")
def get_predictions():

    if not PREDICTIONS_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail="Testing predictions file not found."
        )

    try:

        df = pd.read_csv(PREDICTIONS_FILE)

        records = df.astype(object).where(
            pd.notna(df),
            None
        ).to_dict(orient="records")

        return records

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.lower()

    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Benchmark metrics are unavailable."
        )

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
        change = (
            (c0["MAE"] - c1["MAE"]) / c0["MAE"]
        ) * 100

        answer = (
            f"Adding news changed MAE by {change:.2f}% "
            "relative to C0. "
            "A negative improvement means MAE increased. "
            "In this experiment, news did not improve MAE."
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
            f"C0 directional accuracy: "
            f"{c0['Directional_Accuracy']}%. "
            f"C1 directional accuracy: "
            f"{c1['Directional_Accuracy']}%. "
            "Naive has no directional calls."
        )

    else:
        answer = (
            "I can answer questions about the best model, "
            "MAE, RMSE, directional accuracy and the impact "
            "of adding news. Please ask one of these questions."
        )

    return {
        "question": request.question,
        "answer": answer,
        "source": "Stored benchmark_metrics.csv"
    }