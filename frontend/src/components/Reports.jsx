import React, { useState } from 'react';
import { Mail, FileText, Loader, AlertCircle, Sparkles, RotateCcw, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../api';

function getStressLabel(score) {
  if (score >= 7) return { label: 'High', badge: 'badge-warning' };
  if (score >= 4) return { label: 'Moderate', badge: 'badge-primary' };
  return { label: 'Low', badge: 'badge-success' };
}

function MetricRow({ label, score }) {
  const { label: level, badge } = getStressLabel(score);
  return (
    <div className="flex justify-between items-center py-3 border-b border-border/40 last:border-0">
      <span className="text-mutedText text-sm">{label}</span>
      <div className="flex items-center gap-2">
        <span className="font-display font-bold text-lg text-lightText">{score}/10</span>
        <span className={badge}>{level}</span>
      </div>
    </div>
  );
}

export default function Reports() {
  const { token } = useAuth();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [emailSent, setEmailSent] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    setEmailSent(false);

    try {
      const res = await fetch(`${API_BASE}/tracker/reports`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to generate report.');
      const data = await res.json();
      setReport(data);
      if (data.email_sent) setEmailSent(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card-hover w-full max-w-lg p-6 sm:p-8" role="region" aria-label="Weekly Reports">
      <div className="flex items-start gap-4 mb-6">
        <div className="w-11 h-11 rounded-xl bg-warning/15 border border-warning/25 flex items-center justify-center flex-shrink-0">
          <FileText size={22} className="text-warning" />
        </div>
        <div>
          <h2 className="section-title">Weekly Report</h2>
          <p className="section-subtitle">AI summary from your chat & image sessions</p>
        </div>
      </div>

      {!report ? (
        <div className="text-center py-4">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-warning/10 to-primary/10 border border-border/60 flex items-center justify-center mx-auto mb-5">
            <TrendingUp size={36} className="text-warning/70" />
          </div>
          <p className="text-mutedText mb-6 text-sm leading-relaxed max-w-xs mx-auto">
            Generate your weekly wellness summary. The report is automatically emailed to your guardian if one is on file.
          </p>
          {error && (
            <div className="flex items-center justify-center gap-2 bg-error/10 border border-error/20 text-error text-sm rounded-xl p-3 mb-4" role="alert">
              <AlertCircle size={16} /> {error}
            </div>
          )}
          <button
            onClick={generateReport}
            disabled={loading}
            className="btn-primary flex items-center justify-center gap-2 mx-auto"
            aria-busy={loading}
          >
            {loading
              ? <><Loader size={18} className="animate-spin" /> Compiling...</>
              : <><Sparkles size={16} /> Generate Report</>}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-4 animate-fade-in" aria-live="polite">
          <div className="bg-darkBg/50 rounded-xl p-5 border border-border/60">
            <h3 className="text-xs font-semibold text-mutedText uppercase tracking-widest mb-1">Metrics Summary</h3>
            <MetricRow label="Average Stress" score={report.avg_stress} />
            <MetricRow label="Average Anxiety" score={report.avg_anxiety} />
          </div>

          <div className="bg-darkBg/50 rounded-xl p-5 border border-border/60">
            <h3 className="text-xs font-semibold text-mutedText uppercase tracking-widest mb-3">AI Insight</h3>
            <p className="text-sm leading-relaxed text-lightText/90">{report.summary}</p>
          </div>

          {emailSent && (
            <div className="flex items-center gap-3 bg-secondary/8 border border-secondary/20 rounded-xl p-4">
              <div className="w-9 h-9 rounded-lg bg-secondary/15 flex items-center justify-center flex-shrink-0">
                <Mail size={18} className="text-secondary" />
              </div>
              <span className="text-sm text-lightText/90">Weekly report sent to your guardian&apos;s email.</span>
            </div>
          )}

          <button
            onClick={() => { setReport(null); setEmailSent(false); }}
            className="btn-ghost self-start flex items-center gap-1.5 text-primary"
          >
            <RotateCcw size={14} /> Regenerate Report
          </button>
        </div>
      )}
    </div>
  );
}
