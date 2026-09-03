import React from 'react';
import { Satellite, Activity, Radio, CheckCircle, ShieldCheck, Zap } from 'lucide-react';
import { SatelliteTelemetry } from '../types';
import { t } from '../utils/translations';

interface SatelliteTelemetryBarProps {
  satellites: SatelliteTelemetry[];
  currentLang?: string;
}

export const SatelliteTelemetryBar: React.FC<SatelliteTelemetryBarProps> = ({
  satellites,
  currentLang = 'en'
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
      {satellites.map((sat) => (
        <div 
          key={sat.id}
          className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all space-y-2.5 group"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-blue-50 text-blue-600 border border-blue-100 group-hover:scale-105 transition-transform">
                <Satellite className="w-4 h-4 animate-pulse" />
              </div>
              <div>
                <h4 className="text-sm font-black text-slate-900 tracking-tight">{sat.name}</h4>
                <p className="text-[11px] text-slate-500 font-mono">{sat.orbit}</p>
              </div>
            </div>
            <span className="text-xs font-black px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              {sat.health_score}% {t('health', currentLang)}
            </span>
          </div>

          <div className="text-xs text-slate-700 space-y-1 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5">
              <span className="text-blue-700 font-bold">{t('sensors', currentLang)}</span>
              <span className="text-slate-800 font-medium">{sat.sensors.join(", ")}</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="text-blue-700 font-bold">{t('latency', currentLang)}</span>
              <span className="text-slate-800 font-mono">{sat.data_latency}</span>
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
            <span className="font-mono text-slate-600">{t('last_pass', currentLang)} {sat.last_pass.split("T")[1]?.substring(0, 5) || "Continuous"}</span>
            <span className="flex items-center space-x-1.5 font-bold text-emerald-600">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>{t('ground_synced', currentLang)}</span>
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
