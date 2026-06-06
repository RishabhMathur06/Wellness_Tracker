import React, { useState, useEffect } from 'react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart
} from 'recharts';
import { Loader, AlertCircle, RefreshCw, TrendingUp, Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../api';

function StatCard({ label, value, color, icon: Icon }) {
  return (
    <div className="bg-darkBg/50 rounded-xl p-4 border border-border/60 flex items-center gap-3">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={18} />
      </div>
      <div>
        <p className="text-xs text-mutedText uppercase tracking-wide">{label}</p>
        <p className="text-xl font-display font-bold text-lightText">{value}<span className="text-sm text-mutedText font-normal">/10</span></p>
      </div>
    </div>
  );
}

export default function MetricsDashboard() {
  const { token } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/tracker/metrics`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch metrics.');
      setData(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchMetrics();
  }, [token]);

  const avgStress = data.length ? (data.reduce((s, d) => s + d.stress, 0) / data.length).toFixed(1) : '—';
  const avgAnxiety = data.length ? (data.reduce((s, d) => s + d.anxiety, 0) / data.length).toFixed(1) : '—';

  return (
    <div className="glass-card-hover w-full max-w-3xl p-6 sm:p-8" role="region" aria-label="Metrics Dashboard">
      <div className="flex items-start justify-between mb-6 gap-4">
        <div className="flex items-start gap-4">
          <div className="w-11 h-11 rounded-xl bg-error/15 border border-error/25 flex items-center justify-center flex-shrink-0">
            <TrendingUp size={22} className="text-error" />
          </div>
          <div>
            <h2 className="section-title">Weekly Metrics</h2>
            <p className="section-subtitle">7-day stress & anxiety trends</p>
          </div>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="btn-ghost p-2 rounded-xl border border-border/60"
          aria-label="Refresh metrics"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin text-primary' : ''} />
        </button>
      </div>

      {loading ? (
        <div className="h-72 flex flex-col items-center justify-center text-mutedText gap-3">
          <Loader size={24} className="animate-spin text-primary" />
          <span className="text-sm">Loading your metrics...</span>
        </div>
      ) : error ? (
        <div className="h-72 flex flex-col items-center justify-center text-error gap-2" role="alert">
          <AlertCircle size={24} />
          <span className="text-sm">{error}</span>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-2 gap-3 mb-6">
            <StatCard
              label="Avg Stress"
              value={avgStress}
              color="bg-error/15 text-error"
              icon={Activity}
            />
            <StatCard
              label="Avg Anxiety"
              value={avgAnxiety}
              color="bg-warning/15 text-warning"
              icon={TrendingUp}
            />
          </div>

          <div className="h-72 w-full bg-darkBg/30 rounded-xl p-2 border border-border/40" aria-hidden="true">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="stressGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="anxietyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3650" vertical={false} />
                <XAxis dataKey="day" stroke="#64748B" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis stroke="#64748B" domain={[0, 10]} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#151E32',
                    border: '1px solid #2A3650',
                    borderRadius: '12px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                  }}
                  labelStyle={{ color: '#94A3B8', marginBottom: 4 }}
                  itemStyle={{ fontSize: 13 }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                <Area type="monotone" dataKey="stress" stroke="#EF4444" strokeWidth={2.5} fill="url(#stressGrad)" dot={{ r: 3, fill: '#EF4444', strokeWidth: 0 }} name="Stress" />
                <Area type="monotone" dataKey="anxiety" stroke="#F59E0B" strokeWidth={2.5} fill="url(#anxietyGrad)" dot={{ r: 3, fill: '#F59E0B', strokeWidth: 0 }} name="Anxiety" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="sr-only">
            <p>Stress and Anxiety levels over the past 7 days, scale 0 to 10.</p>
            <ul>
              {data.map((d) => (
                <li key={d.day}>{d.day}: Stress {d.stress}, Anxiety {d.anxiety}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
