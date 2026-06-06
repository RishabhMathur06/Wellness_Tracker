import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Loader, ScanFace, RotateCcw, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../api';

function scoreClass(score) {
  if (score >= 7) return 'score-high';
  if (score >= 4) return 'score-mid';
  return 'score-low';
}

function ScoreCard({ label, score }) {
  const pct = Math.min(100, (score / 10) * 100);
  return (
    <div className="bg-darkBg/50 rounded-xl p-4 border border-border/60">
      <p className="text-xs font-medium text-mutedText uppercase tracking-wide mb-2">{label}</p>
      <p className={`text-3xl font-display font-bold ${scoreClass(score)}`}>
        {score}<span className="text-base text-mutedText font-normal">/10</span>
      </p>
      <div className="mt-3 h-1.5 bg-border/60 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${score >= 7 ? 'bg-error' : score >= 4 ? 'bg-warning' : 'bg-secondary'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function ImageUploader() {
  const { token } = useAuth();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setResult(null);
    setError(null);
    setPreview(URL.createObjectURL(selected));
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/tracker/analyze-emotion`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis failed.');
      }

      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="glass-card-hover w-full max-w-lg p-6 sm:p-8" id="uploader-title">
      <div className="flex items-start gap-4 mb-6">
        <div className="w-11 h-11 rounded-xl bg-primary/15 border border-primary/25 flex items-center justify-center flex-shrink-0">
          <ScanFace size={22} className="text-primary" />
        </div>
        <div>
          <h2 className="section-title">Emotion Analysis</h2>
          <p className="section-subtitle">Upload a photo for AI-powered stress & emotion detection</p>
        </div>
      </div>

      {!result ? (
        <div className="flex flex-col gap-5">
          <label
            htmlFor="file-upload"
            className="group cursor-pointer flex flex-col items-center justify-center w-full rounded-2xl overflow-hidden border-2 border-dashed border-border hover:border-primary/50 transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/40 bg-darkBg/30"
            aria-labelledby="uploader-title"
          >
            {preview ? (
              <div className="relative w-full">
                <img src={preview} alt="Selected preview" className="w-full h-52 object-cover" />
                <div className="absolute inset-0 bg-darkBg/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="text-sm font-medium text-white bg-darkBg/80 px-3 py-1.5 rounded-lg">Change image</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-44 w-full gap-3 py-6">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:scale-105 transition-transform">
                  <UploadCloud size={28} className="text-primary" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-lightText">Drop an image or click to browse</p>
                  <p className="text-xs text-mutedText mt-1">JPG, PNG, WEBP supported</p>
                </div>
              </div>
            )}
            <input
              id="file-upload"
              ref={inputRef}
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={handleFileChange}
              aria-label="Upload an image for emotion analysis"
            />
          </label>

          {error && (
            <div className="flex items-center gap-2 bg-error/10 border border-error/20 text-error text-sm rounded-xl p-3" role="alert">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
            aria-busy={loading}
          >
            {loading ? <><Loader size={18} className="animate-spin" /> Analyzing...</> : <><Sparkles size={16} /> Analyze Image</>}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-4 animate-fade-in" role="region" aria-live="polite">
          <div className="flex items-center gap-2 text-secondary">
            <CheckCircle2 size={20} />
            <span className="font-semibold">Analysis Complete</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <ScoreCard label="Stress" score={result.stress_score} />
            <ScoreCard label="Anxiety" score={result.anxiety_score} />
          </div>

          {result.detected_emotions?.length > 0 && (
            <div className="bg-darkBg/50 rounded-xl p-4 border border-border/60">
              <p className="text-xs font-medium text-mutedText uppercase tracking-wide mb-2">Detected Emotions</p>
              <div className="flex flex-wrap gap-2">
                {result.detected_emotions.map((e) => (
                  <span key={e} className="badge-primary">{e}</span>
                ))}
              </div>
            </div>
          )}

          <div className="bg-darkBg/50 rounded-xl p-4 border border-border/60">
            <p className="text-xs font-medium text-mutedText uppercase tracking-wide mb-2">Analysis</p>
            <p className="text-sm leading-relaxed text-lightText/90">{result.analysis}</p>
          </div>

          <div className="bg-secondary/8 border border-secondary/20 rounded-xl p-4">
            <p className="text-xs font-medium text-secondary uppercase tracking-wide mb-2">Recommendation</p>
            <p className="text-sm leading-relaxed text-lightText/90">{result.recommendation}</p>
          </div>

          <button onClick={reset} className="btn-ghost self-start flex items-center gap-1.5 text-primary hover:text-primary">
            <RotateCcw size={14} /> Analyze another image
          </button>
        </div>
      )}
    </div>
  );
}
