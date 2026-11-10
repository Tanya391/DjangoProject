import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Bot, Send, Sparkles, User, RefreshCw, Layers, ArrowUpRight } from 'lucide-react';
import { useChatStore } from '../store/useChatStore';
import { api } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';

export function ChatPage() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const location = useLocation();

  const { messages, addMessage, clearMessages } = useChatStore();
  const queryClient = useQueryClient();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (location.state?.autoQuery) {
      const query = location.state.autoQuery;
      // Clear the router state so it doesn't re-run if the user refreshes
      window.history.replaceState({}, document.title);
      handleSend(query);
    }
  }, [location.state]);

  const handleSend = async (questionText) => {
    const text = questionText || input;
    if (!text.trim() || loading) return;

    // Add user message
    addMessage({
      sender: 'user',
      text,
      timestamp: new Date().toISOString(),
    });

    if (!questionText) setInput('');
    setLoading(true);

    try {
      const res = await api.askQuestion(text);
      addMessage({
        sender: 'assistant',
        text: res.answer || 'No explicit answer returned.',
        sources: res.sources || [],
        timestamp: new Date().toISOString(),
      });
      // Invalidate history query so HistoryPage is updated
      queryClient.invalidateQueries({ queryKey: ['queryHistory'] });
    } catch (err) {
      addMessage({
        sender: 'assistant',
        text: `Sorry, I encountered an error: ${err.message || 'Unable to connect to AI engine.'}`,
        sources: [],
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    'What was my highest expense last month?',
    'How much did I spend on Food Delivery?',
    'List my active subscriptions and monthly costs',
    'Summarize my total income vs total expense',
  ];

  return (
    <div className="h-[calc(100vh-7rem)] flex flex-col glass-card rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      {/* Header Bar */}
      <div className="p-4 px-6 border-b border-slate-200 dark:border-slate-800/80 bg-slate-100/80 dark:bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Bot className="w-5 h-5 text-cyan-200" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              FinAgent Financial Assistant
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/20 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5 text-cyan-500 dark:text-cyan-400" />
                Gemini AI
              </span>
            </h3>
            <p className="text-[11px] text-slate-600 dark:text-slate-400">Query financial transactions and insights</p>
          </div>
        </div>

        <button
          onClick={clearMessages}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition text-xs flex items-center gap-1.5 border border-slate-200 dark:border-slate-800"
          title="Reset Conversation"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Clear Chat</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3.5 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-md'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Bubble Container */}
            <div className={`max-w-2xl space-y-3 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none font-medium'
                    : 'bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none shadow-xl'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>

              {/* RAG Retrieved Sources Card */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400 font-semibold text-[11px] uppercase tracking-wider">
                    <Layers className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                    Retrieved Source Records ({msg.sources.length} matches)
                  </div>
                  <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                    {msg.sources.map((s, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-900/80 text-[11px] border border-slate-200 dark:border-slate-800"
                      >
                        <span className="text-slate-700 dark:text-slate-300 font-medium">
                          {s.date} • {s.receiver} ({s.category})
                        </span>
                        <span
                          className={`font-mono-num font-bold ${
                            s.transaction_type === 'credit' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-slate-200'
                          }`}
                        >
                          ₹{s.amount?.toLocaleString('en-IN')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white flex items-center justify-center font-bold text-xs shrink-0">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 text-xs flex items-center gap-2">
              <span className="animate-spin w-3.5 h-3.5 border-2 border-indigo-600 dark:border-indigo-400 border-t-transparent rounded-full" />
              Synthesizing answer...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions Chips */}
      <div className="p-3 px-6 bg-slate-100/60 dark:bg-slate-950/40 border-t border-slate-200 dark:border-slate-800/60 overflow-x-auto flex items-center gap-2 no-scrollbar">
        <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider shrink-0 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-cyan-600 dark:text-cyan-400" />
          Suggestions:
        </span>
        {suggestedQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 text-slate-700 dark:text-slate-300 transition whitespace-nowrap flex items-center gap-1.5 shrink-0"
          >
            {q}
            <ArrowUpRight className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 bg-slate-100/90 dark:bg-slate-950/80 border-t border-slate-200 dark:border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a financial question..."
            className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-5 py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-40 text-white font-bold text-sm rounded-xl shadow-lg transition flex items-center gap-2 shrink-0"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Ask AI</span>
          </button>
        </form>
      </div>
    </div>
  );
}
