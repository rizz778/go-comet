import { baseApi } from './baseApi';
import type { TradeDocumentExtraction } from '../types/pipeline';

export interface UpdateStatusPayload {
    status: 'pending_review' | 'approved' | 'amended';
    edited_data?: Partial<TradeDocumentExtraction> | null;
    amendment_draft?: string | null;
}

export async function updateStatus(
    runId: number,
    payload: UpdateStatusPayload
): Promise<{ status: string; message: string }> {
    return baseApi.post<{ status: string; message: string }>(`/update-status/${runId}`, payload);
}
