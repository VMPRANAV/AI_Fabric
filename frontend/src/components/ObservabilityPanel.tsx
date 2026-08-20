import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
import { ExecutionTrace } from '../types';
import { RefreshCw } from 'lucide-react';

/**
 * ObservabilityPanel displays recent execution traces with latency breakdowns and per‑model latency chart.
 * Design follows the existing glass‑panel aesthetic and uses subtle hover animations.
 */
const ObservabilityPanel: React.FC = () => {
  const [traces, setTraces] = useState<ExecutionTrace[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTraces = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getTraces();
      setTraces(data);
    } catch (err) {
      console.error('Failed to load observability traces', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTraces();
  }, []);

  // Helper to compute per‑model latency for the chart – simple aggregation
  const modelLatencyMap: Record<string, number[]> = {};
  traces.forEach((t) => {
    const model = t.selected_model ?? 'unknown';
    const latency = t.total_latency_ms ?? 0;
    if (!modelLatencyMap[model]) modelLatencyMap[model] = [];
    modelLatencyMap[model].push(latency);
  });
  const modelAvgLatency = Object.entries(modelLatencyMap).map(([model, latencies]) => ({
    model,
    avgLatency: latencies.reduce((a, b) => a + b, 0) / latencies.length,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <RefreshCw className="h-5 w-5 text-indigo-400" /> Observability
        </h2>
        <button
          onClick={fetchTraces}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white text-xs font-mono transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Traces Table */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="pb-3 px-3">Request ID</th>
              <th className="pb-3 px-3">Strategy</th>
              <th className="pb-3 px-3">Model</th>
              <th className="pb-3 px-3">Total Latency</th>
              <th className="pb-3 px-3">Cost (USD)</th>
              <th className="pb-3 px-3">Reward</th>
              <th className="pb-3 px-3">Started</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {traces.map((t) => (
              <tr key={t.request_id} className="hover:bg-slate-900/40 transition-all">
                <td className="py-2 px-3 font-mono text-slate-300 break-all">{t.request_id}</td>
                <td className="py-2 px-3 text-indigo-300">{t.strategy ?? '—'}</td>
                <td className="py-2 px-3 text-cyan-300">{t.selected_model ?? '—'}</td>
                <td className="py-2 px-3 text-amber-300">{t.total_latency_ms ? `${t.total_latency_ms.toFixed(1)}ms` : '—'}</td>
                <td className="py-2 px-3 text-emerald-300">{t.cost_usd ? `$${t.cost_usd.toFixed(6)}` : '—'}</td>
                <td className="py-2 px-3 text-purple-300">{t.reward !== undefined ? t.reward.toFixed(3) : '—'}</td>
                <td className="py-2 px-3 text-slate-500">{new Date(t.start_timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Per‑Model Latency Chart */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 mb-2">Average Latency per Model (ms)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {modelAvgLatency.map((m) => (
            <div key={m.model} className="bg-slate-900/30 p-3 rounded-md">
              <div className="flex justify-between items-center text-sm text-slate-300">
                <span>{m.model}</span>
                <span className="font-mono text-amber-300">{m.avgLatency.toFixed(1)}ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ObservabilityPanel;
