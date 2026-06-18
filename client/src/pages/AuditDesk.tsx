import React, { useState } from 'react';
import { UploadZone } from '../components/UploadZone';
import { PipelineTracker } from '../components/PipelineTracker';
import { ReviewPanel } from '../components/ReviewPanel';
import type { PipelineRun } from '../types/pipeline';
import { uploadDocument } from '../api/uploadApi';

interface AuditDeskProps {
    activeRun: PipelineRun | null;
    setActiveRun: (run: PipelineRun | null) => void;
    onRunCompleted: () => void;
}

export const AuditDesk: React.FC<AuditDeskProps> = ({ activeRun, setActiveRun, onRunCompleted }) => {
    const [step, setStep] = useState<'idle' | 'uploading' | 'extracting' | 'validating' | 'routing' | 'done'>('idle');
    const [logs, setLogs] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);

    const handleUploadStart = async (file: File) => {
        setLoading(true);
        setActiveRun(null);
        setStep('uploading');
        setLogs(['Client Node: Connecting to audit endpoint...', `Client Node: Uploading ${file.name} (size: ${(file.size / 1024).toFixed(1)} KB)`]);

        // Simulating progressive pipeline step updates based on expected latency
        const simulateStep = (nextStep: typeof step, logMsg: string, delay: number) => {
            return new Promise<void>(resolve => {
                setTimeout(() => {
                    setStep(nextStep);
                    setLogs(prev => [...prev, logMsg]);
                    resolve();
                }, delay);
            });
        };

        try {
            // Start upload API request in parallel with visual animations
            const uploadPromise = uploadDocument(file);

            await simulateStep('extracting', 'Extractor Agent: Loading vision parameters and extracting data points...', 1500);
            await simulateStep('validating', 'Validator Agent: Loading rules.json and conducting compliance verification...', 2000);
            await simulateStep('routing', 'Router Agent: Conducting lane classification and email drafting...', 2000);

            const result = await uploadPromise;

            setStep('done');
            // Merge actual agent logs from the backend database payload
            if (result.logs) {
                setLogs(prev => [...prev, ...result.logs!]);
            } else {
                setLogs(prev => [...prev, 'Storage Node: Run saved successfully. DB ID: ' + result.id]);
            }
            setActiveRun(result);
            onRunCompleted();
        } catch (err: any) {
            setStep('idle');
            setLogs(prev => [...prev, `Pipeline Error: ${err.message || 'Audit execution failed.'}`]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-6 items-start w-full">
            <div className="flex flex-col gap-6 w-full">
                <UploadZone onUploadStart={handleUploadStart} disabled={loading} />
                {(step !== 'idle' || logs.length > 0) && (
                    <PipelineTracker step={step} logs={logs} />
                )}
            </div>
            <div className="w-full">
                <ReviewPanel run={activeRun} onRunUpdated={onRunCompleted} />
            </div>
        </div>
    );
};
