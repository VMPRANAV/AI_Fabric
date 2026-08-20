export interface ExecutionStageTrace {
  stage: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  details: Record<string, any>;
  timestamp: string;
}

export interface QueryResponse {
  request_id: string;
  query: string;
  task_type: string;
  complexity: number;
  selected_model: string;
  prompt_version: string;
  selected_tool?: string;
  response_text: string;
  latency_ms: number;
  total_tokens: number;
  estimated_cost: number;
  reward: number;
  decision_source: string;
  trace: ExecutionStageTrace[];
}

export interface MetricsSummary {
  total_requests: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_cost: number;
  avg_tokens: number;
  avg_reward: number;
  model_distribution: Record<string, number>;
  routing_distribution: Record<string, number>;
}

export interface BenchmarkComparison {
  policy: string;
  avg_latency_ms: number;
  avg_cost: number;
  avg_quality: number;
  success_rate: number;
  avg_reward: number;
}

export interface ExecutionTrace {
  request_id: string;
  strategy?: string;
  task_type?: string;
  selected_model?: string;
  prompt_version?: string;
  start_timestamp: string;
  end_timestamp?: string;
  total_latency_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  cost_usd?: number;
  tool_success?: boolean;
  model_success?: boolean;
  quality_score?: number;
  reward?: number;
  state_vector?: Record<string, any>;
  error?: string;
  stages: StageSchema[];
}

export interface StageSchema {
  stage: string;
  status: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  tier: string;
  cost_per_1k_prompt_tokens: number;
  cost_per_1k_completion_tokens: number;
  max_context_window: number;
  is_active: boolean;
}
