import React, { useState } from 'react';
import { 
  Info, 
  ChevronRight, 
  ChevronDown, 
  ShieldCheck, 
  AlertTriangle, 
  ShieldAlert, 
  XCircle, 
  HelpCircle,
  Database
} from 'lucide-react';
import { WeatherObservation } from '../types';

interface DataLegendBarProps {
  weather?: WeatherObservation | null;
  currentLang?: string;
}

export const DataLegendBar: React.FC<DataLegendBarProps> = ({ weather }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative font-['Outfit',sans-serif] text-xs">
      {/* Floating Pill Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-zinc-200/80 shadow-md text-zinc-800 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer font-bold"
        aria-expanded={isOpen}
        aria-label="Toggle Data Legends and Scientific Scales"
      >
        <Database className="w-3.5 h-3.5 text-blue-600" />
        <span>Scientific Legends</span>
        {isOpen ? <ChevronDown className="w-3 h-3 text-zinc-400" /> : <ChevronRight className="w-3 h-3 text-zinc-400" />}
      </button>

      {/* Popout Legend Modal / Card */}
      {isOpen && (
        <div className="absolute bottom-10 left-0 w-80 p-4 rounded-2xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-2xl text-zinc-900 space-y-3 z-[500] animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-2">
            <span className="font-bold text-zinc-900 flex items-center space-x-1.5">
              <span>Scientific Data Scales & Provenance</span>
            </span>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-zinc-400 hover:text-zinc-600 cursor-pointer"
            >
              ✕
            </button>
          </div>

          <div className="space-y-3 text-[11px]">
            {/* 1. Sea Surface Temperature */}
            <div className="space-y-1">
              <div className="flex justify-between font-bold text-zinc-800">
                <span>Sea Surface Temperature (SST)</span>
                <span className="font-mono text-rose-700">24 – 32 °C</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-blue-500 via-emerald-400 via-amber-400 to-rose-600" />
              <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                <span>Cool Upwelling (24°C)</span>
                <span>Warm Basin (32°C)</span>
              </div>
              <div className="text-[9px] text-zinc-500">Source: ISRO INSAT-3DR Geostationary TIR Imager</div>
            </div>

            {/* 2. Chlorophyll-a Biomass */}
            <div className="space-y-1 pt-1 border-t border-zinc-100">
              <div className="flex justify-between font-bold text-zinc-800">
                <span>Chlorophyll-a Concentration</span>
                <span className="font-mono text-teal-700">0.1 – 5.0 mg/m³</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-cyan-200 via-teal-400 via-emerald-500 to-green-800" />
              <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                <span>Oligotrophic (0.1)</span>
                <span>Eutrophic Bloom (5.0+)</span>
              </div>
              <div className="text-[9px] text-zinc-500">Source: ISRO Oceansat-3 (EOS-06) OCM-3 360m LAC</div>
            </div>

            {/* 3. Operational Risk Classification (Accessible Non-Color Encoding) */}
            <div className="space-y-1.5 pt-1 border-t border-zinc-100">
              <div className="font-bold text-zinc-800 flex items-center justify-between">
                <span>Marine Operational Risk</span>
                <span className="text-[9px] text-zinc-400 font-normal">Multi-factor score</span>
              </div>

              <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                <div className="flex items-center space-x-1.5 p-1.5 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-800 font-bold">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>LOW (Safe)</span>
                </div>
                <div className="flex items-center space-x-1.5 p-1.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-800 font-bold">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>MODERATE</span>
                </div>
                <div className="flex items-center space-x-1.5 p-1.5 rounded-lg bg-rose-50 border border-rose-300 text-rose-800 font-bold">
                  <ShieldAlert className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                  <span>HIGH (Danger)</span>
                </div>
                <div className="flex items-center space-x-1.5 p-1.5 rounded-lg bg-red-100 border-2 border-dashed border-red-500 text-red-900 font-black">
                  <XCircle className="w-3.5 h-3.5 text-red-700 shrink-0" />
                  <span>SEVERE / NO-GO</span>
                </div>
              </div>
            </div>

            {/* 4. Current Conditions Snapshot */}
            {weather && (
              <div className="pt-2 border-t border-zinc-100 flex items-center justify-between text-[10px] font-mono text-zinc-600">
                <span>Observed Waves: <strong>{weather.significant_wave_height_m}m</strong></span>
                <span>Winds: <strong>{weather.wind_speed_knots} kts</strong></span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
