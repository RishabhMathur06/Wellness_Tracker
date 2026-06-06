import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, Bot, User, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../api';

export default function ChatInterface() {
  const { token } = useAuth();
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I\'m your therapeutic assistant. How are you feeling today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [piiNotice, setPiiNotice] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setMessages((prev) => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setLoading(true);
    setError(null);
    setPiiNotice(null);

    try {
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userText }),
      });

      if (!res.ok) throw new Error('Failed to get a response from the server.');

      const data = await res.json();

      if (data.pii_detected && data.user_message_display) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'user',
            text: data.user_message_display,
            piiFlagged: true,
          };
          return updated;
        });
        if (data.pii_notice) setPiiNotice(data.pii_notice);
      }

      setMessages((prev) => [...prev, { role: 'bot', text: data.reply }]);
    } catch {
      setError('Connection error. Please ensure the backend is running.');
      setMessages((prev) => [...prev, { role: 'bot', text: "I'm having trouble connecting right now. Please try again in a moment." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="glass-card-hover w-full max-w-lg flex flex-col h-[560px] overflow-hidden"
      role="region"
      aria-label="Therapeutic Chat Interface"
    >
      <div className="px-5 py-4 border-b border-border/60 bg-gradient-to-r from-primary/5 to-accent/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-secondary to-primary flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <h2 className="font-display font-bold text-lightText">Therapeutic Chat</h2>
            <p className="text-xs text-mutedText">Stress & anxiety tracked automatically</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3" aria-live="polite">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-2.5 max-w-[88%] ${msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start'}`}
          >
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${
              msg.role === 'user' ? 'bg-primary/20' : 'bg-secondary/20'
            }`}>
              {msg.role === 'user'
                ? <User size={13} className="text-primary" />
                : <Bot size={13} className="text-secondary" />}
            </div>
            <div className={`px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role === 'user'
                ? msg.piiFlagged
                  ? 'bg-warning/15 border border-warning/30 text-lightText rounded-tr-sm'
                  : 'bg-gradient-to-br from-primary to-primaryDark text-white rounded-tr-sm'
                : 'bg-darkBg/60 border border-border/60 text-lightText/90 rounded-tl-sm'
            }`}>
              {msg.text}
              {msg.piiFlagged && (
                <span className="mt-1.5 flex items-center gap-1 text-[10px] text-warning font-medium">
                  <ShieldAlert size={11} /> Sensitive info redacted
                </span>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5 self-start max-w-[88%]">
            <div className="w-7 h-7 rounded-lg bg-secondary/20 flex items-center justify-center flex-shrink-0">
              <Bot size={13} className="text-secondary" />
            </div>
            <div className="bg-darkBg/60 border border-border/60 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
              <span className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <span key={i} className="w-1.5 h-1.5 bg-mutedText rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </span>
            </div>
          </div>
        )}

        {piiNotice && (
          <div className="flex items-start gap-2 bg-warning/10 border border-warning/25 text-warning text-xs rounded-xl p-3 mx-1" role="alert">
            <ShieldAlert size={14} className="flex-shrink-0 mt-0.5" />
            <span>{piiNotice}</span>
          </div>
        )}

        {error && (
          <p className="text-error text-xs text-center" role="alert">{error}</p>
        )}

        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} className="p-4 border-t border-border/60 bg-darkBg/20 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Share how you're feeling..."
          disabled={loading}
          className="input-field flex-1 py-2.5"
          aria-label="Chat input"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary px-3.5 py-2.5 flex items-center justify-center"
          aria-label="Send message"
        >
          {loading ? <Loader size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
}
