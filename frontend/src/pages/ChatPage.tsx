import React, { useState } from 'react';
import { ChatInterface } from '../components/ChatInterface';
import { TraceVisualizer } from '../components/TraceVisualizer';
import { QueryResponse } from '../types';
import { apiClient } from '../services/api';

export const ChatPage: React.FC = () => {
  const [lastResponse, setLastResponse] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExecute = async (query: string, strategy: string, budget: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.executeQuery(query, strategy, budget);
      setLastResponse(res);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'Execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* Left: Chat Input & Response (7 cols) */}
      <div className="lg:col-span-7 space-y-4">
        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
            ⚠️ {error}
          </div>
        )}
        <ChatInterface
          onExecute={handleExecute}
          isLoading={isLoading}
          lastResponse={lastResponse}
        />
      </div>

      {/* Right: Live Execution Trace Visualizer (5 cols) */}
      <div className="lg:col-span-5">
        <TraceVisualizer
          traces={lastResponse?.trace || []}
          isLoading={isLoading}
          decisionSource={lastResponse?.decision_source}
          selectedModel={lastResponse?.selected_model}
          reward={lastResponse?.reward}
        />
      </div>
    </div>
  );
};
