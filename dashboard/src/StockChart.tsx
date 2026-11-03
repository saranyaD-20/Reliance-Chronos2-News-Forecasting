
import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

type Prediction = {
  forecast_date: string
  target_date: string
  target_close: number
  naive_prediction: number
  c0_prediction: number
  c1_prediction: number
}

function StockChart() {
  const [data, setData] = React.useState<Prediction[]>([])
  const [startDate, setStartDate] = React.useState('2026-07-02')
  const [endDate, setEndDate] = React.useState('2026-09-30')
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    const fetchForecasts = async () => {
      try {
        const response = await fetch(
          'http://127.0.0.1:8000/supabase-forecasts'
        )

        if (!response.ok) {
          throw new Error('Unable to retrieve forecasts from Supabase.')
        }

        const result = await response.json()

        if (result.status !== 'success' || !Array.isArray(result.data)) {
          throw new Error('Invalid forecast data received.')
        }

        const parsed: Prediction[] = result.data.map((item: Prediction) => ({
          forecast_date: item.forecast_date,
          target_date: item.target_date,
          target_close: Number(item.target_close),
          naive_prediction: Number(item.naive_prediction),
          c0_prediction: Number(item.c0_prediction),
          c1_prediction: Number(item.c1_prediction),
        }))

        setData(parsed)
        setError('')
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Something went wrong while loading forecasts.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchForecasts()
  }, [])

  const filteredData = data.filter(
    (item) =>
      item.target_date >= startDate &&
      item.target_date <= endDate
  )

  if (loading) {
    return <p className="p-4 text-slate-500">Loading forecasts from Supabase...</p>
  }

  if (error) {
    return <p className="p-4 text-red-500">{error}</p>
  }

  return (
    <div className="w-full">
      <div className="mb-5 flex flex-wrap gap-4">
        <div>
          <label className="mb-1 block text-sm text-slate-600">
            Start Date
          </label>
          <input
            type="date"
            min="2026-07-02"
            max="2026-09-30"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="rounded-lg border border-slate-300 p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-slate-600">
            End Date
          </label>
          <input
            type="date"
            min="2026-07-02"
            max="2026-09-30"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="rounded-lg border border-slate-300 p-2"
          />
        </div>
      </div>

      <p className="mb-3 text-sm text-slate-500">
        Showing {filteredData.length} forecast records
      </p>

      {filteredData.length === 0 ? (
        <p className="rounded-lg bg-slate-50 p-6 text-center text-slate-500">
          No predictions available for this date range.
        </p>
      ) : (
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="target_date" tick={{ fontSize: 10 }} />
              <YAxis domain={['auto', 'auto']} />
              <Tooltip />
              <Legend />

              <Line
                type="monotone"
                dataKey="target_close"
                name="Actual"
                stroke="#0f172a"
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="naive_prediction"
                name="Naive"
                stroke="#94a3b8"
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="c0_prediction"
                name="Chronos C0"
                stroke="#2563eb"
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="c1_prediction"
                name="Chronos C1"
                stroke="#16a34a"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default StockChart
