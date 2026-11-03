
import pandas as pd
from supabase_client import supabase
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

NEWS_FILE = (
    BASE_DIR
    / "results"
    / "testing_news_forecast_features_corrected.csv"
)

def sync_news():
    if not NEWS_FILE.exists():
        raise FileNotFoundError(f"News file not found: {NEWS_FILE}")

    df = pd.read_csv(NEWS_FILE)

    required_columns = [
        "forecast_date",
        "article_count",
        "mean_tone",
        "coverage_status"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required_columns].copy()
    df["trading_date"] = df["forecast_date"]
    df = df.astype(object).where(pd.notna(df), None)
    records = df.to_dict(orient="records")

    response = (
        supabase
        .table("news_features")
        .upsert(records)
        .execute()
    )

    print("News records synchronized:", len(response.data))

def sync_news_to_supabase():
    NEWS_FILE = (
        BASE_DIR
        / "results"
        / "testing_news_forecast_features_corrected.csv"
    )

    if not NEWS_FILE.exists():
        raise FileNotFoundError("News features file not found.")

    df = pd.read_csv(NEWS_FILE)

    required = [
        "forecast_date",
        "article_count",
        "mean_tone",
        "coverage_status"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"News CSV is missing columns: {missing}")

    df = df[required].copy()
    df["trading_date"] = df["forecast_date"]

    records = (
        df.astype(object)
        .where(pd.notna(df), None)
        .to_dict(orient="records")
    )

    supabase.table("news_features").upsert(records).execute()

    return len(records)


if __name__ == "__main__":
    sync_news()
