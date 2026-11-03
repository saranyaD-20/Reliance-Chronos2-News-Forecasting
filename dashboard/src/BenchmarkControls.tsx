
import { supabase } from './lib/supabase'
import { useState, useEffect, useCallback } from 'react'
const API_URL = 'https://reliance-chronos-api.onrender.com'

interface ExecutionStatus {
  status: 'idle' | 'running' | 'completed' | 'failed'
  message: string
  started_at: string | null
  completed_at: string | null
  error: string | null
}

const initialStatus: ExecutionStatus = {
  status: 'idle',
  message: 'Ready to run the benchmark.',
  started_at: null,
  completed_at: null,
  error: null,
}

function formatDate(value: string | null) {
  if (!value) return 'Not available'

  return new Date(value).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  })
}

export default function BenchmarkControls() {
  const [execution, setExecution] =
    useState<ExecutionStatus>(initialStatus)

  const [loading, setLoading] = useState(false)
  const [requestError, setRequestError] = useState('')

  const checkStatus = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_URL}/execution-status`
      )

      if (!response.ok) {
        throw new Error('Unable to fetch execution status.')
      }

      const data: ExecutionStatus = await response.json()

      setExecution(data)
      setRequestError('')
    } catch {
      setRequestError(
        'Cannot connect to backend. Check whether FastAPI is running.'
      )
    }
  }, [])

  useEffect(() => {
    checkStatus()

    const interval = window.setInterval(
      checkStatus,
      3000
    )

    return () => window.clearInterval(interval)
  }, [checkStatus])

  const runBenchmark = async () => {
  setLoading(true)
  setRequestError('')

  try {
    
    const { data, error } = await supabase.functions.invoke(
      'bright-endpoint',
      {
        body: {},
      }
    )

    if (error) {
      throw new Error(error.message)
    }

    if (data?.error) {
      throw new Error(data.error)
    }

    await checkStatus()
  } catch (error) {
    if (error instanceof Error) {
  setRequestError(error.message)
} else {
  setRequestError(JSON.stringify(error))
}
  } finally {
    setLoading(false)
  }
}
  const isRunning = execution.status === 'running'

  const statusColors = {
    idle: '#64748b',
    running: '#2563eb',
    completed: '#15803d',
    failed: '#dc2626',
  }

  return (
    <section className="benchmark-controls">
      <div className="benchmark-controls-header">
        <div>
          <h2>Benchmark Execution</h2>
          <p>
            Run the Chronos-2 stock forecasting benchmark
            and compare the three forecasting models.
          </p>
        </div>

        <button
          className="run-benchmark-button"
          onClick={runBenchmark}
          disabled={isRunning || loading}
        >
          {isRunning || loading
            ? 'Running Benchmark...'
            : 'Run Benchmark'}
        </button>
      </div>

      <div className="execution-status-card">
        <div className="status-heading">
          <span
            className="status-indicator"
            style={{
              backgroundColor: statusColors[execution.status],
            }}
          />

          <strong>
            Status: {execution.status.toUpperCase()}
          </strong>
        </div>

        <p>{execution.message}</p>

        <div className="execution-details">
          <div>
            <span>Started At</span>
            <strong>{formatDate(execution.started_at)}</strong>
          </div>

          <div>
            <span>Completed At</span>
            <strong>{formatDate(execution.completed_at)}</strong>
          </div>
        </div>

        {isRunning && (
          <div className="progress-track">
            <div className="progress-bar" />
          </div>
        )}

        {execution.error && (
          <p className="execution-error">
            {execution.error}
          </p>
        )}

        {requestError && (
          <p className="execution-error">
            {requestError}
          </p>
        )}
      </div>
    </section>
  )
}
