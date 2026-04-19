import { useState, useEffect } from 'react'
import ChartsSection from '../components/ChartsSection'

const API_URL = '/api/proxy'

function MetricCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${API_URL}/metrics`)
        if (!res.ok) throw new Error('Failed to fetch metrics')
        const data = await res.json()
        setMetrics(data)
        setLastUpdated(new Date())
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-8 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Acme Logistics — Carrier Sales</h1>
            <p className="text-sm text-gray-400 mt-0.5">Real-time inbound call analytics</p>
          </div>
          {lastUpdated && (
            <span className="text-xs text-gray-400">Updated {lastUpdated.toLocaleTimeString()}</span>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-gray-700"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-700">Unable to load metrics: {error}</p>
          </div>
        ) : metrics ? (
          <>
            {/* KPI Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
              <MetricCard label="Total Calls" value={metrics.total_calls} sub="All inbound carrier calls" />
              <MetricCard label="Booked" value={metrics.outcomes?.agreed || 0} sub="Loads successfully booked" />
              <MetricCard label="Booking Rate" value={`${(metrics.success_rate * 100).toFixed(1)}%`} sub="Calls converted to bookings" />
              <MetricCard label="Unique Carriers" value={metrics.unique_carriers} sub="Distinct carriers reached" />
            </div>

            {/* Price Row */}
            <div className="grid grid-cols-3 gap-5 mb-8">
              <MetricCard label="Avg Negotiated Price" value={`$${metrics.avg_negotiated_price.toFixed(0)}`} sub="Average across all agreed deals" />
              <MetricCard label="Min Price" value={`$${metrics.min_negotiated_price.toFixed(0)}`} sub="Lowest agreed rate" />
              <MetricCard label="Max Price" value={`$${metrics.max_negotiated_price.toFixed(0)}`} sub="Highest agreed rate" />
            </div>

            {/* Charts */}
            <ChartsSection metrics={metrics} />

            {/* Bottom Row */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Sentiment */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Carrier Sentiment</h3>
                {Object.keys(metrics.sentiment || {}).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(metrics.sentiment).map(([sentiment, count]) => {
                      const total = Object.values(metrics.sentiment).reduce((a, b) => a + b, 0)
                      const pct = ((count / total) * 100).toFixed(0)
                      const colors = { positive: 'bg-green-100 text-green-700', neutral: 'bg-gray-100 text-gray-700', negative: 'bg-red-100 text-red-700' }
                      return (
                        <div key={sentiment} className="flex justify-between items-center">
                          <span className={`text-xs font-semibold px-2 py-1 rounded-md capitalize ${colors[sentiment] || 'bg-gray-100 text-gray-700'}`}>
                            {sentiment}
                          </span>
                          <span className="text-sm text-gray-500">{count} calls ({pct}%)</span>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-8">No data yet</p>
                )}
              </div>

              {/* Equipment */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Equipment Type</h3>
                {metrics.equipment?.length > 0 ? (
                  <div className="space-y-3">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>Type</span>
                      <span className="flex gap-6"><span>Calls</span><span>Booked</span></span>
                    </div>
                    {metrics.equipment.map((e) => (
                      <div key={e.type} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700">{e.type}</span>
                        <span className="flex gap-6 text-sm">
                          <span className="text-gray-500">{e.calls}</span>
                          <span className="font-semibold text-gray-900">{e.booked}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-8">No data yet</p>
                )}
              </div>
            </div>

            {/* Popular Lanes */}
            <div className="mt-5 bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Popular Lanes</h3>
              {metrics.lanes?.length > 0 ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Lane</span>
                    <span className="flex gap-10"><span>Calls</span><span>Booked</span></span>
                  </div>
                  {metrics.lanes.map((l) => (
                    <div key={l.lane} className="flex justify-between items-center">
                      <span className="text-sm text-gray-700 font-medium">{l.lane}</span>
                      <span className="flex gap-10 text-sm">
                        <span className="text-gray-500">{l.calls}</span>
                        <span className="font-semibold text-gray-900">{l.booked}</span>
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400 text-center py-8">No data yet</p>
              )}
            </div>
          </>
        ) : null}
      </main>
    </div>
  )
}
