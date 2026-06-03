import type { AnalyzeRequest, ApiResponse } from '../types';

const API_BASE = '/api';

export async function analyzeBazi(data: AnalyzeRequest): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
}
