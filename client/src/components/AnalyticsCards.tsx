import React from 'react';
import { FileText, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { AnalyticsResponse } from '../types/pipeline';

interface AnalyticsCardsProps {
    stats: AnalyticsResponse | null;
}

export const AnalyticsCards: React.FC<AnalyticsCardsProps> = ({ stats }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
            <div className="bg-[#1E293B]/50 border border-slate-800/85 rounded-xl p-5 flex items-center gap-5 shadow-lg backdrop-blur-md">
                <div className="w-12 h-12 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                    <FileText size={22} />
                </div>
                <div>
                    <h3 className="text-2xl font-bold text-white tracking-tight">{stats?.total_runs ?? 0}</h3>
                    <span className="text-xs text-slate-400 font-medium">Total Audits</span>
                </div>
            </div>

            <div className="bg-[#1E293B]/50 border border-slate-800/85 rounded-xl p-5 flex items-center gap-5 shadow-lg backdrop-blur-md">
                <div className="w-12 h-12 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                    <CheckCircle2 size={22} />
                </div>
                <div>
                    <h3 className="text-2xl font-bold text-white tracking-tight">{stats?.decisions.auto_approve ?? 0}</h3>
                    <span className="text-xs text-slate-400 font-medium">Auto-Approved</span>
                </div>
            </div>

            <div className="bg-[#1E293B]/50 border border-slate-800/85 rounded-xl p-5 flex items-center gap-5 shadow-lg backdrop-blur-md">
                <div className="w-12 h-12 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
                    <AlertTriangle size={22} />
                </div>
                <div>
                    <h3 className="text-2xl font-bold text-white tracking-tight">
                        {(stats?.decisions.flag_review ?? 0) + (stats?.decisions.amendment_request ?? 0)}
                    </h3>
                    <span className="text-xs text-slate-400 font-medium">Flagged Mismatches</span>
                </div>
            </div>
        </div>
    );
};
