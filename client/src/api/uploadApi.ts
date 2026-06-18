import { baseApi } from './baseApi';
import type { PipelineRun } from '../types/pipeline';

export async function uploadDocument(file: File): Promise<PipelineRun> {
    const formData = new FormData();
    formData.append('file', file);
    return baseApi.post<PipelineRun>('/upload', formData, true);
}
