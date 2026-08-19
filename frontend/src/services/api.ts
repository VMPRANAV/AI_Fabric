import axios from 'axios';
import { QueryResponse, MetricsSummary, BenchmarkComparison, LLMModel } from '../types';

const API_BASE = '/api/v1';

export const apiClient = {
  async checkHealth(): Promise<{ status: string; service: string; database: string; mcp_mode: string }> {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  async executeQuery(
    query: string,
    routing_strategy: string = 'rule_based',
    budget: string = 'medium'
  ): Promise<QueryResponse> {
    const res = await axios.post(`${API_BASE}/query`, {
      query,
      routing_strategy,
      budget,
    });
    return res.data;
  },

  async getMetricsSummary(): Promise<MetricsSummary> {
    const res = await axios.get(`${API_BASE}/metrics/summary`);
    return res.data;
  },

  async getBenchmarks(): Promise<BenchmarkComparison[]> {
    const res = await axios.get(`${API_BASE}/metrics/benchmarks`);
    return res.data;
  },

  async getModels(): Promise<LLMModel[]> {
    const res = await axios.get(`${API_BASE}/models`);
    return res.data;
  },
};
