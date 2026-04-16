import axios from 'axios';
import type { TripPlan, TripPlanRequest } from './types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const travelApi = {
  createPlan: async (request: TripPlanRequest): Promise<TripPlan> => {
    const response = await api.post<TripPlan>('/plan', request);
    return response.data;
  },
};
