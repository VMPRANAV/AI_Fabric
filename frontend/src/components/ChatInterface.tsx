import React, { useState } from 'react';
import { Send, Sparkles, Cpu, DollarSign, Clock, Hash, Code2 } from 'lucide-react';
import { QueryResponse } from '../types';

interface ChatInterfaceProps {
  onExecute: (query: string, strategy: string, budget: string) => Promise<void>;
  isLoading: boolean;
  lastResponse: QueryResponse | null;
}

const PRESET_QUERIES = [
  {
    title: "SQL Optimization Demo",
    query: "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement.",
  },
  {
    title: "Repository Architecture Analysis",
    query: "Inspect the repository structure, analyze file dependencies, and identify potential architectural bottlenecks.",
  },
  {
    title: "Fast Lightweight Task",
    query: "Generate an idempotent SQL script to create a user audit log table with indexed timestamps.",
  },
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onExecute,
  isLoading,
  lastResponse,
}) => {
  const [query, setQuery] = useState(PRESET_QUERIES[0].query);
  const [strategy, setStrategy] = useState('rule_based');
  const [budget, setBudget] = useState('medium');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onExecute(query, strategy, budget);
  };

  return (
    <div className="space-y-5">
      {/* Query Form Box */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <h2 className="font-bold text-sm text-slate-200 uppercase tracking-wide">
              AI Request Input
            </h2>
          </div>

          {/* Quick Config Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400">Policy:</span>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-indigo-300 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-indigo-500 font-semibold"
              >
                <option value="rule_based">Rule-Based</option>
                <option value="ppo">PPO Agent</option>
                <option value="federated">Federated Learning</option>
                <option value="static">Static Baseline</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400">Budget:</span>
              <select
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
        </div>

        {/* Preset query chips */}
        <div className="flex flex-wrap gap-2 mb-3">
          {PRESET_QUERIES.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuery(preset.query)}
              className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-indigo-950/40 text-slate-400 hover:text-indigo-300 border border-slate-800 hover:border-indigo-500/40 transition-all text-left"
            >
              💡 {preset.title}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={3}
            placeholder="Enter request for AI Fabric orchestration..."
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-sans resize-none transition-all"
          />

          <div className="flex justify-between items-center mt-2.5">
            <span className="text-[11px] font-mono text-slate-500">
              Closed-loop feedback & adaptive policy enabled
            </span>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold font-mono tracking-wide transition-all ${
                isLoading || !query.trim()
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white hover:shadow-lg hover:shadow-indigo-500/25 active:scale-95'
              }`}
            >
              {isLoading ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Routing & Executing...
                </>
              ) : (
                <>
                  <Send className="h-3.5 w-3.5" />
                  Execute Fabric Pipeline
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Response Card */}
      {lastResponse && (
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4 text-emerald-400" />
              <h3 className="font-bold text-sm text-slate-200">Execution Output</h3>
            </div>

            {/* Metric Badges */}
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-300">
                <Cpu className="h-3 w-3" />
                {lastResponse.selected_model}
              </span>
              <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                <Clock className="h-3 w-3" />
                {lastResponse.latency_ms.toFixed(1)}ms
              </span>
              <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300">
                <Hash className="h-3 w-3" />
                {lastResponse.total_tokens} tokens
              </span>
              <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                <DollarSign className="h-3 w-3" />
                ${lastResponse.estimated_cost.toFixed(6)}
              </span>
            </div>
          </div>

          <div className="prose prose-invert max-w-none text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-mono bg-slate-950/70 p-4 rounded-xl border border-slate-800">
            {lastResponse.response_text}
          </div>
        </div>
      )}
    </div>
  );
};
