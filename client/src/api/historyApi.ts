import { baseApi } from './baseApi';
import type { PipelineRun } from '../types/pipeline';

export async function fetchHistory(): Promise<PipelineRun[]> {
    return baseApi.get<PipelineRun[]>('/history');
}
