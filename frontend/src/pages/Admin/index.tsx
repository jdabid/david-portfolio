import { useApi } from "../../hooks/useApi";
import { getDashboard } from "../../services/api";

export default function Admin() {
  const { data: dashboard, loading, error } = useApi(getDashboard, []);

  if (loading) return <div className="max-w-6xl mx-auto px-4 py-24 text-gray-500">Loading dashboard...</div>;
  if (error) return <div className="max-w-6xl mx-auto px-4 py-24 text-red-400">Error: {error}</div>;
  if (!dashboard) return null;

  return (
    <section className="max-w-6xl mx-auto px-4 py-12">
      <h2 className="text-2xl font-bold text-white mb-8">Admin Dashboard</h2>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Visits" value={dashboard.total_visits} />
        <StatCard label="Unique Visitors" value={dashboard.unique_visitors} />
        <StatCard label="Messages" value={dashboard.total_messages} />
        <StatCard label="Chat Sessions" value={dashboard.total_chats} />
      </div>

      {/* Top Pages */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="border border-white/10 rounded-lg p-6">
          <h3 className="text-white font-semibold mb-4">Top Pages</h3>
          {dashboard.top_pages.length === 0 ? (
            <p className="text-gray-500 text-sm">No data yet</p>
          ) : (
            <div className="space-y-2">
              {dashboard.top_pages.map((page, i) => (
                <div key={page.path} className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">
                    <span className="text-gray-600 mr-2">{i + 1}.</span>
                    {page.path}
                  </span>
                  <span className="text-primary-500 font-mono text-sm">{page.count}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Daily Stats */}
        <div className="border border-white/10 rounded-lg p-6">
          <h3 className="text-white font-semibold mb-4">Daily Activity</h3>
          {dashboard.daily_stats.length === 0 ? (
            <p className="text-gray-500 text-sm">No data yet</p>
          ) : (
            <div className="space-y-2">
              {dashboard.daily_stats.slice(0, 7).map((day) => (
                <div key={day.date} className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm font-mono">{day.date}</span>
                  <div className="flex gap-4 text-sm">
                    <span className="text-gray-400">
                      {day.total_visits} <span className="text-gray-600">visits</span>
                    </span>
                    <span className="text-gray-400">
                      {day.unique_visitors} <span className="text-gray-600">unique</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-white/10 rounded-lg p-4">
      <p className="text-gray-500 text-xs font-mono uppercase">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value.toLocaleString()}</p>
    </div>
  );
}
