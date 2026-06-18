import React from 'react';
import type { PipelineRun } from '../types/pipeline';
import { RefreshCw, Play } from 'lucide-react';

interface HistoryRegistryProps {
    runs: PipelineRun[];
    loading: boolean;
    onRefresh: () => void;
    onSelectRun: (run: PipelineRun) => void;
}

export const HistoryRegistry: React.FC<HistoryRegistryProps> = ({ runs, loading, onRefresh, onSelectRun }) => {
    const formatDate = (isoString: string) => {
        try {
            const date = new Date(isoString);
            return date.toLocaleString();
        } catch {
            return isoString;
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

    return (
        <div className="bg-[#1E293B]/50 border border-slate-800/80 rounded-xl p-6 shadow-lg backdrop-blur-md text-slate-100 flex flex-col gap-6 w-full animate-fade-in">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="font-outfit text-xl font-bold tracking-tight text-white mb-0.5">Audit Registry Log</h2>
                    <p className="text-xs text-slate-400">Registry list of all shipment audit pipeline runs stored in SQLite.</p>
                </div>
                <button
                    onClick={onRefresh}
                    className="btn px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg flex items-center gap-2 cursor-pointer text-xs font-semibold"
                    disabled={loading}
                >
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                    <span>Refresh Registry</span>
                </button>
            </div>

            <div className="w-full overflow-hidden border border-slate-800 rounded-lg bg-slate-950/20">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr className="bg-slate-950/50 border-b border-slate-800 text-slate-200 font-semibold uppercase tracking-wider">
                                <th className="p-4 w-16 text-center">ID</th>
                                <th className="p-4">Filename</th>
                                <th className="p-4">Upload Date</th>
                                <th className="p-4">AI Decision</th>
                                <th className="p-4">Status</th>
                                <th className="p-4 w-24 text-center">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60">
                            {loading && runs.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-slate-400 italic">
                                        Loading registry database records...
                                    </td>
                                </tr>
                            ) : runs.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-slate-400 italic">
                                        No audit runs logged in the database yet.
                                    </td>
                                </tr>
                            ) : (
                                runs.map(run => (
                                    <tr key={run.id} className="hover:bg-slate-800/20 transition-all duration-150">
                                        <td className="p-4 font-mono font-bold text-center text-slate-300">{run.id}</td>
                                        <td className="p-4 font-semibold text-white">{run.filename}</td>
                                        <td className="p-4 text-slate-400">{formatDate(run.upload_time)}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${getDecisionBadgeClass(run.decision)}`}>
                                                {run.decision.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${getStatusBadgeClass(run.status)}`}>
                                                {run.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td className="p-4 text-center">
                                            <button
                                                onClick={() => onSelectRun(run)}
                                                className="px-2.5 py-1.5 bg-indigo-500/10 hover:bg-indigo-500 text-indigo-400 hover:text-white rounded transition-all duration-200 cursor-pointer flex items-center gap-1 mx-auto font-semibold text-[10px]"
                                            >
                                                <Play size={10} fill="currentColor" />
                                                <span>Audit</span>
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
