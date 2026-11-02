
import { useEffect, useState } from 'react'

import BenchmarkControls from './BenchmarkControls'
import StockChart from './StockChart'
import NewsChart from './NewsChart'
import ModelComparison from './ModelComparison'
import BenchmarkQA from './BenchmarkQA'
import './App.css'

interface Metrics {
  Model: string
  MAE: number
  RMSE: number
  Directional_Accuracy: number | null
  Directional_Calls: number
}

export default function App() {
  const [metrics, setMetrics] = useState<Metrics[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(
          'http://127.0.0.1:8000/metrics'
        )

        if (!response.ok) {
          throw new Error('Unable to load benchmark metrics.')
        }

        const data: Metrics[] = await response.json()

        setMetrics(data)
        setError('')
      } catch {
        setError(
          'Unable to load metrics. Please check FastAPI.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  const naive = metrics.find(
    (item) => item.Model === 'Naive'
  )

  const c0 = metrics.find(
    (item) => item.Model === 'C0 Chronos-2 Price Only'
  )

  const c1 = metrics.find(
    (item) => item.Model === 'C1 Chronos-2 Price + News'
  )

  return (
    <div className="dashboard">

      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            FORECAST-001 | CHRONOS-2
          </p>

          <h1>
            Reliance Stock Forecasting Dashboard
          </h1>

          <p>
            News-Augmented Next-Trading-Day Stock Price
            Forecasting Benchmark
          </p>
        </div>
      </header>

      <main className="dashboard-content">

        {/* Benchmark execution */}

        <BenchmarkControls />

        {/* KPI summary */}

        <section className="dashboard-section">
          <h2>Benchmark Summary</h2>

          {loading ? (
            <p>Loading benchmark metrics...</p>
          ) : error ? (
            <p className="execution-error">{error}</p>
          ) : (
            <div className="kpi-grid">

              <div className="kpi-card">
                <span>Naive MAE</span>
                <h3>
                  {naive?.MAE.toFixed(2) ?? 'N/A'}
                </h3>
              </div>

              <div className="kpi-card">
                <span>C0 Chronos-2 MAE</span>
                <h3>
                  {c0?.MAE.toFixed(2) ?? 'N/A'}
                </h3>
              </div>

              <div className="kpi-card">
                <span>C1 Chronos-2 + News MAE</span>
                <h3>
                  {c1?.MAE.toFixed(2) ?? 'N/A'}
                </h3>
              </div>

              <div className="kpi-card">
                <span>C1 Directional Accuracy</span>
                <h3>
                  {c1?.Directional_Accuracy != null
                    ? `${c1.Directional_Accuracy.toFixed(2)}%`
                    : 'N/A'}
                </h3>
              </div>

            </div>
          )}
        </section>

        {/* Stock price chart */}

        <section className="dashboard-section">
          <h2>Actual vs Predicted Stock Prices</h2>

          <p className="section-description">
            Comparison of actual Reliance closing prices
            against Naive, C0 and C1 forecasts.
          </p>

          <div className="chart-card">
            <StockChart />
          </div>
        </section>

        {/* News analysis */}

        <section className="dashboard-section">
          <h2>News Analysis</h2>

          <p className="section-description">
            Daily news article coverage and average
            sentiment tone during the testing period.
          </p>

          <div className="chart-card">
            <NewsChart />
          </div>
        </section>

        {/* Model comparison */}

        <section className="dashboard-section">
          <h2>Model Performance Comparison</h2>

          <p className="section-description">
            Compare forecasting accuracy and directional
            performance across all three models.
          </p>

          <ModelComparison />
        </section>

        {/* Project information */}

        <section className="dashboard-section about-section">
          <h2>About This Project</h2>

          <p>
            This project evaluates whether historical
            Reliance Industries news improves next-trading-day
            stock price forecasting using Amazon Chronos-2.
          </p>

          <div className="about-grid">
            <div>
              <strong>Stock</strong>
              <span>Reliance Industries (NSE: RELIANCE)</span>
            </div>

            <div>
              <strong>Forecast Model</strong>
              <span>Amazon Chronos-2</span>
            </div>

            <div>
              <strong>Baseline</strong>
              <span>Previous Trading Session Close</span>
            </div>

            <div>
              <strong>Evaluation Metrics</strong>
              <span>MAE, RMSE, Directional Accuracy</span>
            </div>
          </div>
        </section>
        <BenchmarkQA />

      </main>

      <footer className="dashboard-footer">
        Reliance Stock Forecasting | Chronos-2 Benchmark
      </footer>

    </div>
  )
}
