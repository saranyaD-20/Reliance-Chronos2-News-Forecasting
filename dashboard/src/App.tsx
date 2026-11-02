
import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'
import type { Session } from '@supabase/supabase-js'
import Login from './components/ui/Login'
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
  const [session, setSession] = useState<Session | null>(null)
  const [checkingAuth, setCheckingAuth] = useState(true)

  const [metrics, setMetrics] = useState<Metrics[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Check Supabase authentication
  useEffect(() => {
    let mounted = true

    const checkSession = async () => {
      const { data, error } = await supabase.auth.getSession()

      if (!mounted) return

      if (error) {
        setError(error.message)
      }

      setSession(data.session)
      setCheckingAuth(false)
    }

    checkSession()

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession)
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  // Fetch benchmark metrics only after login
  useEffect(() => {
    if (!session) {
      setMetrics([])
      setLoading(true)
      return
    }

    const fetchMetrics = async () => {
      try {
        setLoading(true)

        const { data, error } = await supabase
          .from('benchmark_metrics')
          .select('*')

        if (error) throw error

        const formattedMetrics: Metrics[] = (data ?? []).map(
          (item) => ({
            Model: item.model_name,
            MAE: Number(item.mae),
            RMSE: Number(item.rmse),
            Directional_Accuracy:
              item.directional_accuracy === null
                ? null
                : Number(item.directional_accuracy),
            Directional_Calls: 0,
          })
        )

        setMetrics(formattedMetrics)
        setError('')
      } catch (err) {
        console.error('Failed to fetch Supabase metrics:', err)
        setError('Unable to load metrics from Supabase.')
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [session])

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut()

    if (error) {
      setError('Unable to log out: ' + error.message)
    }
  }

  // Authentication loading screen
  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Checking login...
      </div>
    )
  }

  // Show login page when user is not authenticated
  if (!session) {
    return <Login onLogin={() => {}} />
  }

  // Identify model metrics
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

        <button
          onClick={handleLogout}
          className="logout-button"
        >
          Logout
        </button>
      </header>

      <main className="dashboard-content">

        <BenchmarkControls />

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
                <h3>{naive?.MAE.toFixed(2) ?? 'N/A'}</h3>
              </div>

              <div className="kpi-card">
                <span>C0 Chronos-2 MAE</span>
                <h3>{c0?.MAE.toFixed(2) ?? 'N/A'}</h3>
              </div>

              <div className="kpi-card">
                <span>C1 Chronos-2 + News MAE</span>
                <h3>{c1?.MAE.toFixed(2) ?? 'N/A'}</h3>
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

        <section className="dashboard-section">
          <h2>Model Performance Comparison</h2>

          <p className="section-description">
            Compare forecasting accuracy and directional
            performance across all three models.
          </p>

          <ModelComparison />
        </section>

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
