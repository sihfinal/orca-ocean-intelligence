import React, { useState } from 'react';
import { 
  Clock, 
  Calendar, 
  AlertCircle, 
  Satellite, 
  Compass, 
  Radio,
  ChevronDown
} from 'lucide-react';
import { TemporalSelection } from '../types';

interface TemporalControlBarProps {
  selection: TemporalSelection;
  onSelectTemporal: (sel: TemporalSelection) => void;
  currentLang?: string;
}

export const TemporalControlBar: React.FC<TemporalControlBarProps> = ({
  selection,
  onSelectTemporal
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const presets = [
    {
      label: 'Current Observation',
      mode: 'OBSERVATION' as const,
      timeLabel: 'Now (Real-Time)',
      target: new Date().toISOString()
    },
    {
      label: 'Tomorrow Morning',
      mode: 'FORECAST' as const,
      timeLabel: 'Tomorrow 08:00 IST',
      target: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
      isMismatch: true,
      mismatchMessage: 'Satellite Earth Observation sensors record physical passes and cannot predict future imagery. Weather and wave fields are projected via numerical hydrodynamics.'
    },
    {
      label: 'Tomorrow Evening',
      mode: 'FORECAST' as const,
      timeLabel: 'Tomorrow 18:00 IST',
      target: new Date(Date.now() + 34 * 3600 * 1000).toISOString(),
      isMismatch: true,
      mismatchMessage: 'Forecast mode: Wave and wind fields simulated via Open-Meteo & INCOIS models.'
    }
  ];

  return (
    <div className="relative font-['Outfit',sans-serif] text-xs">
      {/* Trigger Pill */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-zinc-200/80 shadow-md text-zinc-800 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer font-bold"
        aria-expanded={isOpen}
        aria-label="Toggle Temporal Horizon and Forecast Selection"
      >
        <Clock className="w-3.5 h-3.5 text-blue-600" />
        <span className="font-mono text-[11px] text-zinc-600">Time:</span>
        <span className="font-bold text-zinc-900">{selection.time_label}</span>
        <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono font-bold ${
          selection.mode === 'OBSERVATION' 
            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
            : 'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {selection.mode}
        </span>
        <ChevronDown className="w-3 h-3 text-zinc-400" />
      </button>

      {/* Popout Selector */}
      {isOpen && (
        <div className="absolute top-10 left-0 w-80 p-3.5 rounded-2xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-2xl text-zinc-900 space-y-2.5 z-[500] animate-in fade-in duration-150">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-1.5">
            <span className="font-bold text-zinc-800 text-[11px] flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5 text-blue-600" />
              <span>Temporal Horizon Selection</span>
            </span>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-zinc-400 hover:text-zinc-600 cursor-pointer text-xs"
            >
              ✕
            </button>
          </div>

          <div className="space-y-1.5">
            {presets.map((p, idx) => {
              const isSelected = selection.time_label === p.timeLabel;
              return (
                <div
                  key={idx}
                  onClick={() => {
                    onSelectTemporal({
                      mode: p.mode,
                      target_datetime: p.target,
                      time_label: p.timeLabel,
                      is_mismatch: p.isMismatch,
                      mismatch_message: p.mismatchMessage
                    });
                    setIsOpen(false);
                  }}
                  className={`p-2.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected 
                      ? 'bg-blue-50/80 border-blue-300 text-blue-900 font-bold' 
                      : 'bg-white border-zinc-100 hover:border-zinc-200 text-zinc-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span>{p.label}</span>
                    <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono font-bold ${
                      p.mode === 'OBSERVATION' 
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                        : 'bg-blue-100 text-blue-800 border border-blue-200'
                    }`}>
                      {p.mode}
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-400 font-mono mt-0.5">{p.timeLabel}</div>
                </div>
              );
            })}
          </div>

          {/* Temporal Mismatch Notice Box */}
          {selection.is_mismatch && (
            <div className="p-2.5 rounded-xl bg-amber-50/90 border border-amber-200 text-[10px] space-y-1 text-amber-900">
              <div className="flex items-center space-x-1 font-bold">
                <AlertCircle className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                <span>Temporal Notice (Scientific Honesty):</span>
              </div>
              <p className="text-amber-800 leading-snug">
                {selection.mismatch_message}
              </p>
              <div className="pt-1 border-t border-amber-200/60 font-mono text-[9px] text-amber-700 flex justify-between">
                <span>Satellite: <strong>Latest Observation</strong></span>
                <span>Weather/Wave: <strong>Forecast Model</strong></span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
