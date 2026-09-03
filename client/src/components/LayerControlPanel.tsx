import React, { useState } from 'react';
import { 
  Layers, 
  ChevronDown, 
  ChevronUp, 
  Eye, 
  EyeOff, 
  Fish, 
  ShieldAlert, 
  ShieldCheck, 
  Wind, 
  Waves, 
  Navigation, 
  Anchor, 
  Flame,
  Activity,
  Sparkles
} from 'lucide-react';

export interface LayerVisibilityState {
  // Ocean Physical
  showSST: boolean;
  showChl: boolean;
  showWaves: boolean;
  // Satellite EO & Analytics
  showFronts: boolean;
  showPFZ: boolean;
  showRasterContours: boolean;
  // Safety & Geofence
  showEEZ: boolean;
  showIMBL: boolean;
  showMPA: boolean;
  showCyclone: boolean;
  showPorts: boolean;
  // Navigation
  showRoute: boolean;
  showAlternates: boolean;
}

interface LayerControlPanelProps {
  layers: LayerVisibilityState;
  onToggleLayer: (key: keyof LayerVisibilityState) => void;
  currentLang?: string;
  isRasterAvailable?: boolean;
}

export const LayerControlPanel: React.FC<LayerControlPanelProps> = ({
  layers,
  onToggleLayer,
  isRasterAvailable = true
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeGroup, setActiveGroup] = useState<'all' | 'ocean' | 'safety' | 'nav'>('all');

  return (
    <div className="w-64 rounded-2xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-xl text-zinc-900 overflow-hidden font-['Outfit',sans-serif] select-none text-xs transition-all">
      {/* Header */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-3.5 py-2.5 flex items-center justify-between cursor-pointer hover:bg-zinc-50 border-b border-zinc-100"
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setIsExpanded(!isExpanded); }}
      >
        <div className="flex items-center space-x-2 text-xs font-bold text-zinc-900">
          <Layers className="w-4 h-4 text-blue-600" />
          <span>Geospatial Layers</span>
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-[9px] font-mono font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">
            ISRO / INCOIS
          </span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-zinc-400" /> : <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-3 space-y-3">
          {/* Quick Category Filter Pills */}
          <div className="flex items-center space-x-1 p-0.5 rounded-lg bg-zinc-100 text-[10px] font-bold">
            <button
              onClick={() => setActiveGroup('all')}
              className={`flex-1 py-1 rounded-md transition-colors cursor-pointer ${
                activeGroup === 'all' ? 'bg-white shadow-xs text-zinc-900' : 'text-zinc-500 hover:text-zinc-800'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveGroup('ocean')}
              className={`flex-1 py-1 rounded-md transition-colors cursor-pointer ${
                activeGroup === 'ocean' ? 'bg-white shadow-xs text-zinc-900' : 'text-zinc-500 hover:text-zinc-800'
              }`}
            >
              Ocean
            </button>
            <button
              onClick={() => setActiveGroup('safety')}
              className={`flex-1 py-1 rounded-md transition-colors cursor-pointer ${
                activeGroup === 'safety' ? 'bg-white shadow-xs text-zinc-900' : 'text-zinc-500 hover:text-zinc-800'
              }`}
            >
              Safety
            </button>
            <button
              onClick={() => setActiveGroup('nav')}
              className={`flex-1 py-1 rounded-md transition-colors cursor-pointer ${
                activeGroup === 'nav' ? 'bg-white shadow-xs text-zinc-900' : 'text-zinc-500 hover:text-zinc-800'
              }`}
            >
              Route
            </button>
          </div>

          {/* Group 1: Ocean & Satellite Analytics */}
          {(activeGroup === 'all' || activeGroup === 'ocean') && (
            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 pl-1">
                Ocean & Analytics
              </span>

              {/* PFZ Zones */}
              <div 
                onClick={() => onToggleLayer('showPFZ')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showPFZ}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showPFZ ? 'bg-emerald-500 ring-2 ring-emerald-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">PFZ Fishing Zones</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showPFZ ? 'text-emerald-700' : 'text-zinc-400'}`}>
                  {layers.showPFZ ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* Sea Surface Temp (SST) */}
              <div 
                onClick={() => onToggleLayer('showSST')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showSST}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showSST ? 'bg-rose-500 ring-2 ring-rose-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">SST Thermal Field</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showSST ? 'text-rose-700' : 'text-zinc-400'}`}>
                  {layers.showSST ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* Chlorophyll-a Biomass */}
              <div 
                onClick={() => onToggleLayer('showChl')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showChl}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showChl ? 'bg-teal-500 ring-2 ring-teal-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">Chlorophyll-a Biomass</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showChl ? 'text-teal-700' : 'text-zinc-400'}`}>
                  {layers.showChl ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* EO Raster Contours */}
              {isRasterAvailable && (
                <div 
                  onClick={() => onToggleLayer('showRasterContours')}
                  className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                  role="checkbox"
                  aria-checked={layers.showRasterContours}
                  tabIndex={0}
                >
                  <span className="flex items-center space-x-2 text-zinc-700">
                    <span className={`w-2 h-2 rounded-full ${layers.showRasterContours ? 'bg-indigo-500 ring-2 ring-indigo-200' : 'bg-zinc-300'}`} />
                    <span className="text-[11px] font-medium">L3 Raster Contours</span>
                  </span>
                  <span className={`text-[10px] font-mono font-bold ${layers.showRasterContours ? 'text-indigo-700' : 'text-zinc-400'}`}>
                    {layers.showRasterContours ? 'ON' : 'OFF'}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Group 2: Safety & Boundaries */}
          {(activeGroup === 'all' || activeGroup === 'safety') && (
            <div className="space-y-1 pt-1 border-t border-zinc-100">
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 pl-1">
                Safety & Geofences
              </span>

              {/* Cyclone Warning Cone */}
              <div 
                onClick={() => onToggleLayer('showCyclone')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showCyclone}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showCyclone ? 'bg-red-600 ring-2 ring-red-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">Cyclone Alert & Cones</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showCyclone ? 'text-red-700' : 'text-zinc-400'}`}>
                  {layers.showCyclone ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* IMBL Boundary */}
              <div 
                onClick={() => onToggleLayer('showIMBL')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showIMBL}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showIMBL ? 'bg-red-500 ring-2 ring-red-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">IMBL Border Buffer</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showIMBL ? 'text-red-700' : 'text-zinc-400'}`}>
                  {layers.showIMBL ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* Marine Protected Areas */}
              <div 
                onClick={() => onToggleLayer('showMPA')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showMPA}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showMPA ? 'bg-amber-500 ring-2 ring-amber-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">MPA Eco Reserves</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showMPA ? 'text-amber-700' : 'text-zinc-400'}`}>
                  {layers.showMPA ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* 200 NM Indian EEZ */}
              <div 
                onClick={() => onToggleLayer('showEEZ')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showEEZ}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showEEZ ? 'bg-sky-500 ring-2 ring-sky-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">200 NM Indian EEZ</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showEEZ ? 'text-sky-700' : 'text-zinc-400'}`}>
                  {layers.showEEZ ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>
          )}

          {/* Group 3: Navigation & Harbours */}
          {(activeGroup === 'all' || activeGroup === 'nav') && (
            <div className="space-y-1 pt-1 border-t border-zinc-100">
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 pl-1">
                Navigation
              </span>

              {/* Route */}
              <div 
                onClick={() => onToggleLayer('showRoute')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showRoute}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showRoute ? 'bg-blue-600 ring-2 ring-blue-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">A* Safe Nav Route</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showRoute ? 'text-blue-700' : 'text-zinc-400'}`}>
                  {layers.showRoute ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* Alternative Routes */}
              <div 
                onClick={() => onToggleLayer('showAlternates')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showAlternates}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showAlternates ? 'bg-purple-600 ring-2 ring-purple-200' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">Alternative Routes</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showAlternates ? 'text-purple-700' : 'text-zinc-400'}`}>
                  {layers.showAlternates ? 'ON' : 'OFF'}
                </span>
              </div>

              {/* Major Harbours */}
              <div 
                onClick={() => onToggleLayer('showPorts')}
                className="flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-zinc-50 cursor-pointer transition-colors"
                role="checkbox"
                aria-checked={layers.showPorts}
                tabIndex={0}
              >
                <span className="flex items-center space-x-2 text-zinc-700">
                  <span className={`w-2 h-2 rounded-full ${layers.showPorts ? 'bg-zinc-800' : 'bg-zinc-300'}`} />
                  <span className="text-[11px] font-medium">Major Harbours</span>
                </span>
                <span className={`text-[10px] font-mono font-bold ${layers.showPorts ? 'text-zinc-800' : 'text-zinc-400'}`}>
                  {layers.showPorts ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
