import React from 'react';
import { ExecutionStageTrace } from '../types';
import { 
  Search, 
  Cpu, 
  FileText, 
  GitBranch, 
  Zap, 
  Award, 
  CheckCircle2, 
  Clock, 
  ArrowDown
} from 'lucide-react';

interface TraceVisualizerProps {
  traces: ExecutionStageTrace[];
  isLoading: boolean;
  decisionSource?: string;
  selectedModel?: string;
  reward?: number;
}

export const TraceVisualizer: React.FC<TraceVisualizerProps> = ({
  traces,
  isLoading,
  decisionSource,
  selectedModel,
  reward
}) => {
  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'Query Analyzer':
        return <Search className="h-4 w-4 text-indigo-400" />;
      case 'Decision Engine':
        return <Cpu className="h-4 w-4 text-amber-400" />;
      case 'Prompt Gateway':
        return <FileText className="h-4 w-4 text-cyan-400" />;
      case 'MCP Gateway':
        return <GitBranch className="h-4 w-4 text-emerald-400" />;
      case 'Model Gateway':
        return <Zap className="h-4 w-4 text-purple-400" />;
      case 'Observability & Feedback':
        return <Award className="h-4 w-4 text-rose-400" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-indigo-400" />;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse" />
          <h3 className="font-bold text-sm tracking-wide text-slate-200 uppercase">
            Live Execution Trace Pipeline
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {decisionSource && (
            <span className="px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-[11px] font-mono">
              Policy: <span className="text-indigo-400 font-semibold uppercase">{decisionSource.replace('_', ' ')}</span>
            </span>
          )}
          {selectedModel && (
            <span className="px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-[11px] font-mono">
              {selectedModel}
            </span>
          )}
          {reward !== undefined && (
            <div className="flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
              <span>Feedback Reward:</span>
              <span className="font-bold text-indigo-400">+{reward.toFixed(3)}</span>
            </div>
          )}
        </div>
      </div>

      {traces.length === 0 && !isLoading ? (
        <div className="py-12 text-center text-slate-500 text-xs font-mono flex flex-col items-center justify-center gap-2">
          <Clock className="h-6 w-6 text-slate-600" />
          <span>Awaiting user query execution to generate live control plane trace...</span>
        </div>
      ) : (
        <div className="space-y-3 relative">
          {traces.map((trace, idx) => (
            <React.Fragment key={idx}>
              <div className="group rounded-xl p-3.5 bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/30 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <div className="p-1.5 rounded-lg bg-slate-800 border border-slate-700">
                      {getStageIcon(trace.stage)}
                    </div>
                    <span className="font-semibold text-xs text-slate-200">
                      {trace.stage}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    {trace.status}
                  </span>
                </div>

                {/* Details Json/KV Badge */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-800/50 text-[11px] font-mono">
                  {Object.entries(trace.details).map(([k, v], dIdx) => (
                    <div key={dIdx} className="bg-slate-950/60 p-1.5 rounded border border-slate-800/60">
                      <span className="text-slate-400 block text-[10px] uppercase">{k.replace('_', ' ')}:</span>
                      <span className="text-slate-200 font-semibold truncate block">
                        {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {idx < traces.length - 1 && (
                <div className="flex justify-center -my-1">
                  <ArrowDown className="h-3.5 w-3.5 text-indigo-500/60 animate-bounce" />
                </div>
              )}
            </React.Fragment>
          ))}

          {isLoading && (
            <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 flex items-center justify-center gap-3 text-indigo-300 text-xs font-mono">
              <div className="h-4 w-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span>Executing AI Fabric Orchestration Stages...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
