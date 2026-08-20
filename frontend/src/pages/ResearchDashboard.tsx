import React, { useEffect, useState } from 'react';
import { MetricsSummary, BenchmarkComparison } from '../types';
import { apiClient } from '../services/api';
import { 
  Activity, 
  DollarSign, 
  Clock, 
  Award, 
  BarChart2, 
  PieChart, 
  CheckCircle2,
  RefreshCw 
} from 'lucide-react';
import PpoDashboard from '../components/PpoDashboard';

export const ResearchDashboard: React.FC = () => {
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [benchmarks, setBenchmarks] = useState<BenchmarkComparison[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const [sumData, benchData] = await Promise.all([
        apiClient.getMetricsSummary(),
        apiClient.getBenchmarks()
      ]);
      setSummary(sumData);
      setBenchmarks(benchData);
    } catch (err) {
      console.error('Failed to load metrics', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart2 className="h-5 w-5 text-indigo-400" />
            Research Analytics & Policy Evaluation
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Empirical evaluation across Static Baseline, Rule-Based, PPO, and Federated Learning policies.
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white text-xs font-mono transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Total Requests</span>
            <Activity className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {summary?.total_requests ?? 0}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" />
            {summary?.success_rate ?? 100}% Success Rate
          </div>
        </div>

        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Avg Latency</span>
            <Clock className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-300 font-mono">
            {summary?.avg_latency_ms.toFixed(1) ?? '0.0'}ms
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">
            Across active models
          </div>
        </div>

        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Avg Cost / Req</span>
            <DollarSign className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 font-mono">
            ${summary?.avg_cost.toFixed(6) ?? '0.000000'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">
            ~{summary?.avg_tokens.toFixed(0) ?? '0'} avg tokens
          </div>
        </div>

        <div className="glass-panel p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Avg Feedback Reward</span>
            <Award className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300 font-mono">
            {summary?.avg_reward.toFixed(3) ?? '0.000'}
          </div>
          <div className="text-[11px] text-indigo-400 mt-1 font-mono">
            PPO Objective Score
          </div>
        </div>
      </div>

      {/* Comparative Research Policy Table */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800">
        <h3 className="font-bold text-sm text-slate-200 mb-3 uppercase tracking-wide flex items-center gap-2">
          <span>Comparative Policy Performance Table</span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono">
            Research Evaluation
          </span>
        </h3>
        {/* PPO Dashboard inserted below policy table */}
        <PpoDashboard />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 px-3">Routing Strategy</th>
                <th className="pb-3 px-3">Avg Latency</th>
                <th className="pb-3 px-3">Avg Cost ($)</th>
                <th className="pb-3 px-3">Quality Score</th>
                <th className="pb-3 px-3">Success Rate</th>
                <th className="pb-3 px-3">PPO Reward (R)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {benchmarks.map((b, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-all">
                  <td className="py-3 px-3 font-semibold text-slate-200 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-indigo-400" />
                    {b.policy}
                  </td>
                  <td className="py-3 px-3 text-cyan-300">{b.avg_latency_ms > 0 ? `${b.avg_latency_ms.toFixed(1)}ms` : '—'}</td>
                  <td className="py-3 px-3 text-emerald-300">{b.avg_cost > 0 ? `$${b.avg_cost.toFixed(6)}` : '—'}</td>
                  <td className="py-3 px-3 text-purple-300">{b.avg_quality > 0 ? b.avg_quality.toFixed(2) : '—'}</td>
                  <td className="py-3 px-3 text-slate-300">{b.success_rate > 0 ? `${b.success_rate.toFixed(1)}%` : '—'}</td>
                  <td className="py-3 px-3 text-amber-300 font-bold">{b.avg_reward !== 0 ? `+${b.avg_reward.toFixed(3)}` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model and Strategy Distributions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-3 flex items-center gap-2">
            <PieChart className="h-4 w-4 text-purple-400" />
            Model Selection Distribution
          </h4>
          {summary?.model_distribution && Object.keys(summary.model_distribution).length > 0 ? (
            <div className="space-y-2 font-mono text-xs">
              {Object.entries(summary.model_distribution).map(([model, count], i) => (
                <div key={i} className="flex justify-between items-center bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                  <span className="text-slate-300">{model}</span>
                  <span className="text-indigo-400 font-bold">{count} executions</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs font-mono text-slate-500 py-4 text-center">No model executions recorded yet.</p>
          )}
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-400" />
            Policy Decision Distribution
          </h4>
          {summary?.routing_distribution && Object.keys(summary.routing_distribution).length > 0 ? (
            <div className="space-y-2 font-mono text-xs">
              {Object.entries(summary.routing_distribution).map(([strategy, count], i) => (
                <div key={i} className="flex justify-between items-center bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                  <span className="text-slate-300 uppercase">{strategy.replace('_', ' ')}</span>
                  <span className="text-indigo-400 font-bold">{count} decisions</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs font-mono text-slate-500 py-4 text-center">No routing decisions recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};
