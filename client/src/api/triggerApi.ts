import { baseApi } from './baseApi';
import type { PipelineRun } from '../types/pipeline';

export async function triggerEmail(
    sender: string,
    subject: string,
    body: string,
    files: File[]
): Promise<{ success: boolean; message: string }> {
    const formData = new FormData();
    formData.append('sender', sender);
    formData.append('subject', subject);
    formData.append('email_body', body);
    files.forEach(file => {
        formData.append('file', file);
    });
    return baseApi.post<{ success: boolean; message: string }>('/trigger-email', formData, true);
}

export async function triggerEmailIncoming(
    sender: string,
    subject: string,
    body: string,
    files: File[]
): Promise<{ success: boolean; message: string }> {
    const formData = new FormData();
    formData.append('sender', sender);
    formData.append('subject', subject);
    formData.append('email_body', body);
    files.forEach(file => {
        formData.append('file', file);
    });
    return baseApi.post<{ success: boolean; message: string }>('/incoming', formData, true);
}

export async function fetchIncomingEmails(): Promise<PipelineRun[]> {
    return baseApi.get<PipelineRun[]>('/incoming');
}

export async function fetchProcessedEmails(): Promise<PipelineRun[]> {
    return baseApi.get<PipelineRun[]>('/processed');
}

export async function resolveProcessedEmail(
    runId: number,
    status: string,
    editedData?: any,
    amendmentDraft?: string
): Promise<{ status: string; message: string }> {
    return baseApi.post<{ status: string; message: string }>('/processed', {
        run_id: runId,
        status,
        edited_data: editedData,
        amendment_draft: amendmentDraft
    });
}

