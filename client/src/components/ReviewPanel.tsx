import React, { useState, useEffect } from 'react';
import { ClipboardCheck, Info, Database, Mail, Save, CheckCircle, Send } from 'lucide-react';
import type { PipelineRun, TradeDocumentExtraction } from '../types/pipeline';
import { updateStatus } from '../api/statusApi';

interface ReviewPanelProps {
    run: PipelineRun | null;
    onRunUpdated: () => void;
}

export const ReviewPanel: React.FC<ReviewPanelProps> = ({ run, onRunUpdated }) => {
    const runId = run ? (run.id || (run as any).run_id) : 0;
    const status = run ? (run.status || 'pending_review') : 'pending_review';
    const [fields, setFields] = useState<Record<string, string>>({});
    const [emailBody, setEmailBody] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        if (run) {
            const initialFields: Record<string, string> = {};
            const activeData = run.edited_data || run.extracted_data;

            Object.entries(activeData).forEach(([key, info]) => {
                if (key !== 'extraction_warnings' && info && typeof info === 'object' && 'value' in info) {
                    initialFields[key] = info.value !== null && info.value !== undefined ? String(info.value) : '';
                }
            });

            setFields(initialFields);
            setEmailBody(run.amendment_draft || '');
            setMessage(null);
        }
    }, [run]);

    if (!run) {
        return (
            <div className="bg-[#1E293B]/50 border border-slate-800/80 rounded-xl p-6 shadow-lg backdrop-blur-md h-[480px] flex flex-col items-center justify-center text-center text-slate-400 gap-4">
                <ClipboardCheck size={64} className="stroke-1 text-slate-500" />
                <h3 className="font-outfit text-lg font-semibold text-white">Audit Output Desk</h3>
                <p className="text-xs max-w-sm">
                    Upload a trade document or select an audit run from the Registry logs to inspect discrepancies.
                </p>
            </div>
        );
    }

    const handleFieldChange = (key: string, value: string) => {
        setFields(prev => ({ ...prev, [key]: value }));
    };

    const buildEditedDataPayload = (): Partial<TradeDocumentExtraction> => {
        const payload: Record<string, any> = {};
        const activeData = run.edited_data || run.extracted_data;

        Object.keys(fields).forEach(key => {
            const originalField = (activeData as any)[key];
            payload[key] = {
                value: fields[key],
                confidence: originalField?.confidence ?? 1.0,
                source_snippet: originalField?.source_snippet ?? null
            };
        });

        return payload as Partial<TradeDocumentExtraction>;
    };

    const handleSaveEdits = async () => {
        setSubmitting(true);
        setMessage(null);
        try {
            const editedPayload = buildEditedDataPayload();
            await updateStatus(runId, {
                status: status,
                edited_data: editedPayload,
                amendment_draft: emailBody || null
            });
            setMessage({ type: 'success', text: 'Revisions saved successfully.' });
            onRunUpdated();
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message || 'Failed to save changes.' });
        } finally {
            setSubmitting(false);
        }
    };

    const handleApproveRun = async () => {
        setSubmitting(true);
        setMessage(null);
        try {
            const editedPayload = buildEditedDataPayload();
            await updateStatus(runId, {
                status: 'approved',
                edited_data: editedPayload,
                amendment_draft: emailBody || null
            });
            setMessage({ type: 'success', text: 'Document successfully approved and verified.' });
            onRunUpdated();
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message || 'Failed to approve run.' });
        } finally {
            setSubmitting(false);
        }
    };

    const handleSendAmendment = async () => {
        setSubmitting(true);
        setMessage(null);
        try {
            const editedPayload = buildEditedDataPayload();
            await updateStatus(runId, {
                status: 'amended',
                edited_data: editedPayload,
                amendment_draft: emailBody
            });
            setMessage({ type: 'success', text: 'Amendment status updated. Email request dispatched (mocked).' });
            onRunUpdated();
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message || 'Failed to send amendment.' });
        } finally {
            setSubmitting(false);
        }
    };

    const getDecisionBadgeClass = (decision: string) => {
        switch (decision) {
            case 'auto_approve':
                return 'bg-emerald-500/10 text-emerald-450 border border-emerald-500/20';
            case 'flag_review':
                return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
            case 'amendment_request':
                return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
            default:
                return 'bg-slate-800 text-slate-400';
        }
    };

    const getStatusBadgeClass = (status: string) => {
        switch (status) {
            case 'approved':
                return 'bg-emerald-500/10 text-emerald-450 border border-emerald-500/20';
            case 'pending_review':
                return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
            case 'amended':
                return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
            default:
                return 'bg-slate-800 text-slate-400';
        }
    };

    const getValidationPillClass = (result: string) => {
        switch (result) {
            case 'match':
                return 'bg-emerald-500/10 text-emerald-450';
            case 'mismatch':
                return 'bg-rose-500/10 text-rose-450';
            case 'uncertain':
                return 'bg-amber-500/10 text-amber-400';
            default:
                return 'bg-slate-800 text-slate-400';
        }
    };

    const getConfidenceDotClass = (score: number) => {
        if (score >= 0.9) return 'bg-emerald-500 shadow-[0_0_6px_#10B981]';
        if (score >= 0.7) return 'bg-amber-500 shadow-[0_0_6px_#F59E0B]';
        return 'bg-rose-500 shadow-[0_0_6px_#EF4444]';
    };

    const formatLabel = (key: string) => {
        return key.replace(/_/g, ' ');
    };

    return (
        <div className="bg-[#1E293B]/50 border border-slate-800/80 rounded-xl p-6 shadow-lg backdrop-blur-md text-slate-100 flex flex-col gap-6">
            <div className="flex justify-between items-start border-b border-slate-800 pb-5">
                <div>
                    <h2 className="font-outfit text-xl font-bold tracking-tight text-white mb-0.5" id="review-filename">
                        {run.filename}
                    </h2>
                    <span className="text-xs text-slate-400 font-mono" id="review-run-id">Run ID: #{runId}</span>
                </div>
                <div className="flex gap-2">
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${getDecisionBadgeClass(run.decision)}`}>
                        {run.decision.replace(/_/g, ' ')}
                    </span>
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusBadgeClass(status)}`}>
                        {status.replace(/_/g, ' ')}
                    </span>
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded-lg text-sm font-medium border ${message.type === 'success'
                        ? 'bg-emerald-500/5 text-emerald-400 border-emerald-500/20'
                        : 'bg-rose-500/5 text-rose-450 border-rose-500/20'
                    }`}>
                    {message.text}
                </div>
            )}

            {/* Explanation card */}
            <div className="bg-indigo-500/3 border border-indigo-500/10 rounded-lg p-4 leading-relaxed text-sm text-slate-300 flex flex-col gap-2">
                <h4 className="font-semibold text-white flex items-center gap-1.5 text-xs uppercase tracking-wider text-indigo-400">
                    <Info size={14} />
                    <span>Decision Logic Explanation</span>
                </h4>
                <p className="whitespace-pre-line text-xs">{run.decision_reason}</p>
            </div>

            {/* Form grid */}
            <div>
                <h3 className="font-outfit text-md font-semibold text-white flex items-center gap-2 mb-4">
                    <Database size={16} className="text-slate-400" />
                    <span>Extraction & Rule Audit</span>
                </h3>

                <div className="flex flex-col gap-3">
                    {Object.entries(fields).map(([key, val]) => {
                        const originalField = (run.edited_data || run.extracted_data as any)[key];
                        const valResult = run.validation_results[key];
                        const confidence = originalField?.confidence ?? 1.0;

                        return (
                            <div key={key} className="bg-slate-900/20 border border-slate-800/60 rounded-lg p-3 grid grid-cols-[150px_1fr_120px_100px] items-center gap-6">
                                <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wide capitalize">
                                    {formatLabel(key)}
                                </label>
                                <div className="w-full">
                                    <input
                                        type="text"
                                        value={val}
                                        onChange={(e) => handleFieldChange(key, e.target.value)}
                                        className="bg-[#1E293B]/40 border border-slate-800 rounded px-2 py-1 text-sm text-white focus:border-indigo-500 focus:outline-none w-full"
                                        disabled={submitting}
                                    />
                                </div>
                                <div className="flex items-center gap-2 justify-end">
                                    <span className={`w-1.5 h-1.5 rounded-full ${getConfidenceDotClass(confidence)}`}></span>
                                    <span className="text-[11px] text-slate-400 font-semibold font-mono">
                                        {(confidence * 100).toFixed(0)}% conf
                                    </span>
                                </div>
                                <div className="flex justify-end">
                                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${getValidationPillClass(valResult?.result || 'match')}`}>
                                        {valResult?.result || 'match'}
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Email amendment request */}
            {run.decision === 'amendment_request' && (
                <div className="border-t border-slate-850 pt-5 flex flex-col gap-3">
                    <h3 className="font-outfit text-md font-semibold text-white flex items-center gap-2">
                        <Mail size={16} className="text-slate-400" />
                        <span>Supplier Amendment Request</span>
                    </h3>
                    <p className="text-[11px] text-slate-400">
                        Customize the AI-generated email notification flagging errors directly to the supplier:
                    </p>
                    <textarea
                        value={emailBody}
                        onChange={(e) => setEmailBody(e.target.value)}
                        className="bg-[#080A10] border border-slate-800 rounded-lg p-4 font-mono text-xs text-slate-300 h-48 focus:border-indigo-500 focus:outline-none leading-relaxed resize-none"
                        disabled={submitting}
                    />
                </div>
            )}

            {/* Actions panel */}
            <div className="flex justify-end gap-3 border-t border-slate-850 pt-5">
                <button
                    onClick={handleSaveEdits}
                    className="btn px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg flex items-center gap-2 cursor-pointer text-xs font-semibold"
                    disabled={submitting}
                >
                    <Save size={14} />
                    <span>Save Edits Only</span>
                </button>

                <button
                    onClick={handleApproveRun}
                    className="btn px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg flex items-center gap-2 cursor-pointer text-xs font-semibold"
                    disabled={submitting}
                >
                    <CheckCircle size={14} />
                    <span>Approve & Close</span>
                </button>

                {run.decision === 'amendment_request' && (
                    <button
                        onClick={handleSendAmendment}
                        className="btn px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white rounded-lg flex items-center gap-2 cursor-pointer text-xs font-semibold"
                        disabled={submitting}
                    >
                        <Send size={14} />
                        <span>Send Amendment Request</span>
                    </button>
                )}
            </div>
        </div>
    );
};
