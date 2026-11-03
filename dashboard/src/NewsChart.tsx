
import React from 'react'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

type NewsData = {
  forecast_date: string
  trading_date: string
  article_count: number
  log_article_count: number
  mean_tone: number | null
  coverage_status: string
}

type NewsApiResponse = {
  status: string
  count: number
  data: NewsData[]
}

function NewsChart() {
  const [data, setData] = React.useState<NewsData[]>([])
  const [startDate, setStartDate] = React.useState('2026-07-01')
  const [endDate, setEndDate] = React.useState('2026-09-29')
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    fetch('http://127.0.0.1:8002/supabase-news-features')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Unable to load news data from Supabase')
        }
        return response.json()
      })
      .then((result: NewsApiResponse) => {
        if (result.status !== 'success') {
          throw new Error('News API returned an unsuccessful response')
        }

        const parsed = result.data
  .map((item) => ({
    ...item,
    forecast_date: item.forecast_date || item.trading_date,
    article_count: Number(item.article_count),
    mean_tone:
      item.mean_tone === null ? null : Number(item.mean_tone),
  }))
  .filter((item) => Boolean(item.forecast_date))
  .sort((a, b) =>
    a.forecast_date.localeCompare(b.forecast_date)
  )

        setData(parsed)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const filteredData = data.filter(
    (item) =>
      item.forecast_date >= startDate &&
      item.forecast_date <= endDate
  )

  if (loading) {
    return <p className="p-4 text-slate-500">Loading news data...</p>
  }

  if (error) {
    return <p className="p-4 text-red-500">{error}</p>
  }

  const totalArticles = filteredData.reduce(
    (sum, item) => sum + item.article_count,
    0
  )

  const toneRecords = filteredData.filter(
    (item) => item.mean_tone !== null
  )

  const averageTone = toneRecords.length
    ? toneRecords.reduce(
        (sum, item) => sum + (item.mean_tone ?? 0),
        0
      ) / toneRecords.length
    : null

  return (
    <div className="w-full">
      <div className="mb-5 flex flex-wrap gap-4">
        <div>
          <label className="mb-1 block text-sm text-slate-600">
            Start Date
          </label>
          <input
            type="date"
            value={startDate}
            min="2026-07-01"
            max="2026-09-29"
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
            value={endDate}
            min="2026-07-01"
            max="2026-09-29"
            onChange={(e) => setEndDate(e.target.value)}
            className="rounded-lg border border-slate-300 p-2"
          />
        </div>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-4">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-sm text-slate-500">Total Articles</p>
          <p className="text-xl font-bold">
            {totalArticles.toLocaleString()}
          </p>
        </div>

        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-sm text-slate-500">Average News Tone</p>
          <p className="text-xl font-bold">
            {averageTone === null ? 'N/A' : averageTone.toFixed(2)}
          </p>
        </div>
      </div>

      <p className="mb-3 text-sm text-slate-500">
        Showing {filteredData.length} forecast dates
      </p>

      {filteredData.length === 0 ? (
        <p className="rounded-lg bg-slate-50 p-6 text-center text-slate-500">
          No news data available for this date range.
        </p>
      ) : (
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey="forecast_date"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
              />

              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />

              <Tooltip />
              <Legend />

              <Bar
                yAxisId="left"
                dataKey="article_count"
                name="Article Count"
                fill="#2563eb"
              />

              <Line
                yAxisId="right"
                type="monotone"
                dataKey="mean_tone"
                name="Mean News Tone"
                stroke="#16a34a"
                dot={false}
                connectNulls={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default NewsChart
