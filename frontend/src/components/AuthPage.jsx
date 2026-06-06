import React, { useState } from 'react';
import { Activity, Loader, AlertCircle, Heart, Shield, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [guardianEmail, setGuardianEmail] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register({
          email,
          password,
          full_name: fullName || null,
          guardian_email: guardianEmail || null,
        });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
  };

  return (
    <div className="page-bg min-h-screen flex">
      {/* Left panel — branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center p-12 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-56 h-56 bg-secondary/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />

        <div className="relative z-10 max-w-md animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-glow mb-8">
            <Activity size={32} className="text-white" />
          </div>
          <h1 className="font-display text-4xl font-bold text-lightText mb-4 leading-tight">
            Track your wellness journey
          </h1>
          <p className="text-mutedText text-lg leading-relaxed mb-10">
            AI-powered emotion analysis, therapeutic chat, and guardian alerts — all in one place.
          </p>
          <div className="space-y-4">
            {[
              { icon: Heart, text: 'Real-time stress & anxiety tracking' },
              { icon: Shield, text: 'Secure, private accounts' },
              { icon: Mail, text: 'Automatic guardian notifications' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3 text-mutedText">
                <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
                  <Icon size={15} className="text-primary" />
                </div>
                <span className="text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="glass-card w-full max-w-md p-8 sm:p-10 animate-slide-up">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Activity size={20} className="text-white" />
            </div>
            <span className="font-display text-xl font-bold">Wellness Tracker</span>
          </div>

          <div className="mb-8">
            <h2 className="font-display text-2xl font-bold text-lightText">
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </h2>
            <p className="text-mutedText text-sm mt-1">
              {mode === 'login'
                ? 'Sign in to continue your wellness journey'
                : 'Set up your account to get started'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {mode === 'register' && (
              <div>
                <label htmlFor="fullName" className="block text-xs font-medium text-mutedText mb-1.5 uppercase tracking-wide">Full Name</label>
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your name"
                  className="input-field"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-xs font-medium text-mutedText mb-1.5 uppercase tracking-wide">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-mutedText mb-1.5 uppercase tracking-wide">Password</label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === 'register' ? 'Minimum 8 characters' : 'Your password'}
                className="input-field"
              />
            </div>

            {mode === 'register' && (
              <div>
                <label htmlFor="guardianEmail" className="block text-xs font-medium text-mutedText mb-1.5 uppercase tracking-wide">
                  Guardian Email <span className="normal-case text-mutedText/60">(optional)</span>
                </label>
                <input
                  id="guardianEmail"
                  type="email"
                  value={guardianEmail}
                  onChange={(e) => setGuardianEmail(e.target.value)}
                  placeholder="parent@example.com"
                  className="input-field"
                />
                <p className="text-xs text-mutedText/70 mt-1.5">Receives weekly reports and high-stress alerts.</p>
              </div>
            )}

            {error && (
              <div className="flex items-start gap-2.5 bg-error/10 border border-error/20 text-error text-sm rounded-xl p-3" role="alert">
                <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
                <span>{typeof error === 'string' ? error : 'Something went wrong'}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 mt-1">
              {loading && <Loader size={18} className="animate-spin" />}
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-mutedText mt-8">
            {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={switchMode}
              className="text-primary hover:text-primary/80 font-semibold transition-colors focus:outline-none focus:underline"
            >
              {mode === 'login' ? 'Create one' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
