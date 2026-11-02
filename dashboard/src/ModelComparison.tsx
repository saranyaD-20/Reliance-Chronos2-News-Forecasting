
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

const metrics = [
  {
    model: 'Naive',
    MAE: 12.40625,
    RMSE: 15.479735,
    DirectionalAccuracy: null,
  },
  {
    model: 'Chronos C0',
    MAE: 12.471048,
    RMSE: 15.911770,
    DirectionalAccuracy: 50.0,
  },
  {
    model: 'Chronos C1',
    MAE: 12.779792,
    RMSE: 15.951036,
    DirectionalAccuracy: 50.0,
  },
]
function ModelComparison() {
  return (
    <div className="mt-8 rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold">
        Model Performance Comparison
      </h2>

      <p className="mt-2 text-sm text-slate-500">
        Benchmark evaluation on 64 testing forecast origins.
        Lower MAE and RMSE indicate lower prediction errors.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 font-semibold">MAE Comparison</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="MAE" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <h3 className="mb-3 font-semibold">RMSE Comparison</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="RMSE" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-slate-50">
            <tr>
              <th className="p-3">Model</th>
              <th className="p-3">MAE</th>
              <th className="p-3">RMSE</th>
              <th className="p-3">Directional Accuracy</th>
            </tr>
          </thead>

          <tbody>
            {metrics.map((item) => (
              <tr key={item.model} className="border-b">
                <td className="p-3 font-medium">{item.model}</td>
                <td className="p-3">{item.MAE.toFixed(4)}</td>
                <td className="p-3">{item.RMSE.toFixed(4)}</td>
                <td className="p-3">
                  {item.DirectionalAccuracy === null
                    ? 'N/A'
                    : `${item.DirectionalAccuracy.toFixed(2)}%`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-5 text-sm text-slate-600">
        Result: C1 has a 2.48% higher MAE than C0.
Adding news did not improve forecasting accuracy.
C1 also has slightly higher RMSE than C0.
      </p>
    </div>
  )
}

export default ModelComparison
