import axios from 'axios';
import type { TripPlan, TripPlanRequest } from './types';

// 在生产环境下，通过 Nginx 转发，地址应为相对路径 /api
// 如果是本地调试 npm run dev，可以保留 localhost:8000
const API_BASE_URL = import.meta.env.MODE === 'production' 
  ? '/api' 
  : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const travelApi = {
  createPlan: async (request: TripPlanRequest): Promise<TripPlan> => {
    const response = await api.post<TripPlan>('/plan', request);
    return response.data;
  },

  // SSE-F1: 使用原生 fetch 处理流式响应
  createStreamPlan: async (
    request: TripPlanRequest,
    onStatus: (msg: string) => void,
    onFinal: (plan: TripPlan) => void,
    onError: (err: string) => void
  ) => {
    try {
      const streamUrl = `${API_BASE_URL}/plan/stream`;
      const response = await fetch(streamUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.body) throw new Error('ReadableStream not supported');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // 按照 SSE 格式分割数据 (data: ...)
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // 最后一个可能不完整，留到下一轮

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.replace('data: ', '');
            try {
              const data = JSON.parse(jsonStr);
              if (data.type === 'status') onStatus(data.content);
              else if (data.type === 'final') onFinal(data.content);
              else if (data.type === 'error') onError(data.content);
            } catch (e) {
              console.error('JSON parse error', e);
            }
          }
        }
      }
    } catch (err: any) {
      onError(err.message || '网络请求失败');
    }
  }
};
