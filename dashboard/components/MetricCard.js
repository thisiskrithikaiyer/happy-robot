export default function MetricCard({ label, value, highlight = false }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{label}</p>
      <p className={`text-3xl font-bold tracking-tight ${highlight ? 'text-indigo-600' : 'text-gray-900'}`}>
        {value}
      </p>
    </div>
  )
}
