import React, { useState } from 'react';
import {
  Activity, Upload, MessageSquare, FileBarChart, LayoutDashboard,
  LogOut, Loader, Sparkles, User
} from 'lucide-react';
import { useAuth } from './context/AuthContext';
import AuthPage from './components/AuthPage';
import ImageUploader from './components/ImageUploader';
import ChatInterface from './components/ChatInterface';
import MetricsDashboard from './components/MetricsDashboard';
import Reports from './components/Reports';

const TABS = [
  { id: 'upload', label: 'Analysis', icon: Upload },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'dashboard', label: 'Metrics', icon: LayoutDashboard },
  { id: 'reports', label: 'Reports', icon: FileBarChart },
];

function App() {
  const { user, loading, logout, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');

  if (loading) {
    return (
      <div className="page-bg min-h-screen flex flex-col items-center justify-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
          <Loader size={22} className="animate-spin text-primary" />
        </div>
        <p className="text-mutedText text-sm">Loading your session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  const displayName = user.full_name || user.email.split('@')[0];

  return (
    <div className="page-bg min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border/50 bg-darkBg/70 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/30">
              <Activity size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-display text-lg font-bold text-lightText leading-tight">Wellness Tracker</h1>
              <p className="text-xs text-mutedText hidden sm:block">AI-powered emotional well-being</p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden sm:flex items-center gap-2 bg-cardBg/60 border border-border/60 rounded-xl px-3 py-1.5">
              <div className="w-6 h-6 rounded-lg bg-primary/20 flex items-center justify-center">
                <User size={13} className="text-primary" />
              </div>
              <span className="text-sm text-lightText font-medium max-w-[140px] truncate">{displayName}</span>
            </div>
            <button onClick={logout} className="btn-ghost flex items-center gap-1.5" aria-label="Sign out">
              <LogOut size={15} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 pt-6 pb-2">
        <nav
          className="glass-card p-1.5 flex gap-1 overflow-x-auto"
          role="tablist"
          aria-label="Main Navigation"
        >
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              role="tab"
              aria-selected={activeTab === id}
              onClick={() => setActiveTab(id)}
              className={`tab-pill flex-1 justify-center whitespace-nowrap ${activeTab === id ? 'tab-pill-active' : ''}`}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-6">
        <div key={activeTab} className="animate-slide-up flex justify-center">
          {activeTab === 'upload' && <ImageUploader />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'dashboard' && <div className="w-full"><MetricsDashboard /></div>}
          {activeTab === 'reports' && <Reports />}
        </div>
      </main>

      {/* Footer hint */}
      <footer className="py-4 text-center">
        <p className="text-xs text-mutedText/60 flex items-center justify-center gap-1.5">
          <Sparkles size={12} />
          Powered by Gemini AI
        </p>
      </footer>
    </div>
  );
}

export default App;
