import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Volume2, 
  VolumeX, 
  Navigation, 
  AlertOctagon, 
  Radio, 
  Compass,
  X,
  Play
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  evaluateOfflineGeofence, 
  geofenceAudioSiren, 
  GeofenceProximityResult 
} from '../utils/offlineGeofence';
import { speakText } from '../utils/speechUtils';
import { Geolocation } from '@capacitor/geolocation';

interface GeofenceAlarmHUDProps {
  userCoords: { lat: number; lon: number } | null;
  onSelectCoord?: (lat: number, lon: number) => void;
}

// Temporary disable flag for Geofence Alarm & HUD feature
const IS_ALERT_FEATURE_ENABLED = false;

export const GeofenceAlarmHUD: React.FC<GeofenceAlarmHUDProps> = ({
  userCoords,
  onSelectCoord
}) => {
  if (!IS_ALERT_FEATURE_ENABLED) {
    return null;
  }

  const [currentCoords, setCurrentCoords] = useState<{ lat: number; lon: number }>(
    userCoords || { lat: 9.9416, lon: 76.2575 }
  );
  const [geofenceState, setGeofenceState] = useState<GeofenceProximityResult>(() =>
    evaluateOfflineGeofence(currentCoords.lat, currentCoords.lon)
  );
  const [isSirenMuted, setIsSirenMuted] = useState<boolean>(true);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isMinimized, setIsMinimized] = useState<boolean>(true);
  const [isSimulatingBreach, setIsSimulatingBreach] = useState<boolean>(false);
  const lastSpokenThreatRef = useRef<string | null>(null);

  // Sync coords from parent or GPS
  useEffect(() => {
    if (userCoords && !isSimulatingBreach) {
      setCurrentCoords(userCoords);
      const res = evaluateOfflineGeofence(userCoords.lat, userCoords.lon);
      setGeofenceState(res);
    }
  }, [userCoords, isSimulatingBreach]);

  // If danger breach or caution occurs, auto-expand/un-minimize for safety and speak voice alert
  useEffect(() => {
    if (geofenceState.isBreach || geofenceState.isCaution) {
      setIsMinimized(false);

      if (!isSirenMuted && lastSpokenThreatRef.current !== geofenceState.threatLevel) {
        lastSpokenThreatRef.current = geofenceState.threatLevel;
        speakText(geofenceState.alertMessage, 'en');
      }
    } else {
      lastSpokenThreatRef.current = null;
    }
  }, [geofenceState.isBreach, geofenceState.isCaution, isSirenMuted, geofenceState.alertMessage, geofenceState.threatLevel]);

  // Continuous background GPS Watcher for on-device tracking
  useEffect(() => {
    let watchId: number | null = null;
    let capWatchId: string | null = null;

    const startWatcher = async () => {
      try {
        if (typeof window !== 'undefined') {
          // 1. Capacitor native watcher
          try {
            capWatchId = await Geolocation.watchPosition(
              { enableHighAccuracy: true, timeout: 10000 },
              (position, err) => {
                if (position && !isSimulatingBreach) {
                  const lat = position.coords.latitude;
                  const lon = position.coords.longitude;
                  setCurrentCoords({ lat, lon });
                  const res = evaluateOfflineGeofence(lat, lon);
                  setGeofenceState(res);
                }
              }
            );
          } catch {
            // 2. HTML5 fallback
            if ('geolocation' in navigator) {
              watchId = navigator.geolocation.watchPosition(
                (pos) => {
                  if (!isSimulatingBreach) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    setCurrentCoords({ lat, lon });
                    const res = evaluateOfflineGeofence(lat, lon);
                    setGeofenceState(res);
                  }
                },
                (err) => console.warn('GPS Watcher warning:', err),
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
              );
            }
          }
        }
      } catch (err) {
        console.warn('Geofence watcher error:', err);
      }
    };

    startWatcher();

    return () => {
      if (watchId !== null && typeof navigator !== 'undefined' && navigator.geolocation) {
        navigator.geolocation.clearWatch(watchId);
      }
      if (capWatchId !== null) {
        Geolocation.clearWatch({ id: capWatchId });
      }
    };
  }, [isSimulatingBreach]);

  // Siren Audio Management
  useEffect(() => {
    if (geofenceState.isBreach && !isSirenMuted) {
      geofenceAudioSiren.startSiren(true);
    } else if (geofenceState.isCaution && !isSirenMuted) {
      geofenceAudioSiren.startSiren(false);
    } else {
      geofenceAudioSiren.stopSiren();
    }

    return () => {
      geofenceAudioSiren.stopSiren();
    };
  }, [geofenceState.isBreach, geofenceState.isCaution, isSirenMuted]);

  const toggleMute = () => {
    setIsSirenMuted((prev) => {
      const next = !prev;
      geofenceAudioSiren.isSirenDisabled = next;
      if (next) geofenceAudioSiren.stopSiren();
      return next;
    });
  };

  // Demo Breach Simulation (Palk Strait danger zone)
  const handleSimulateBreach = () => {
    setIsSimulatingBreach(true);
    const breachCoord = { lat: 9.35, lon: 79.48 }; // Critical Palk Strait IMBL proximity
    setCurrentCoords(breachCoord);
    const res = evaluateOfflineGeofence(breachCoord.lat, breachCoord.lon);
    setGeofenceState(res);
    setIsMinimized(false);
    if (onSelectCoord) {
      onSelectCoord(breachCoord.lat, breachCoord.lon);
    }
  };

  const handleSimulateSafe = () => {
    setIsSimulatingBreach(false);
    const safeCoord = userCoords || { lat: 9.9416, lon: 76.2575 };
    setCurrentCoords(safeCoord);
    const res = evaluateOfflineGeofence(safeCoord.lat, safeCoord.lon);
    setGeofenceState(res);
    if (onSelectCoord) {
      onSelectCoord(safeCoord.lat, safeCoord.lon);
    }
  };

  const isBreach = geofenceState.isBreach;
  const isCaution = geofenceState.isCaution;

  return (
    <>
      {/* 1. Full-Screen Red Flashing Emergency Strobe, Perimeter Border & Top Banner */}
      <AnimatePresence>
        {isBreach && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[1000] pointer-events-none flex flex-col justify-between"
          >
            {/* Screen Perimeter Pulsing Red Border & Glow */}
            <div className="absolute inset-0 border-[8px] sm:border-[16px] border-red-600/90 shadow-[inset_0_0_120px_rgba(239,68,68,0.75)] animate-pulse" />

            {/* Top Red Strobe Emergency Header Bar */}
            <div className="relative z-10 w-full bg-gradient-to-r from-red-700 via-red-600 to-red-700 text-white px-4 py-2.5 shadow-2xl flex items-center justify-between pointer-events-auto border-b-2 border-red-400">
              <div className="flex items-center space-x-2.5 min-w-0">
                <div className="w-8 h-8 rounded-full bg-white text-red-600 flex items-center justify-center animate-bounce font-black shrink-0 shadow-md">
                  <AlertOctagon className="w-5 h-5 stroke-[2.5]" />
                </div>
                <div className="min-w-0">
                  <div className="text-xs sm:text-sm font-black uppercase tracking-widest flex items-center space-x-2">
                    <span className="truncate">🚨 CRITICAL IMBL BORDER VIOLATION!</span>
                    <span className="hidden md:inline text-[10px] font-mono px-2 py-0.5 rounded bg-black/40 border border-white/30 text-yellow-300">
                      FOREIGN WATERS BREACH
                    </span>
                  </div>
                  <div className="text-[11px] font-bold text-red-100 truncate mt-0.5">
                    {geofenceState.alertMessage}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2 shrink-0 ml-3">
                <button
                  onClick={toggleMute}
                  className="px-3 py-1.5 rounded-full bg-black/40 hover:bg-black/60 text-white text-xs font-bold border border-white/20 transition-all cursor-pointer flex items-center space-x-1"
                >
                  {isSirenMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 animate-pulse text-yellow-300" />}
                  <span className="hidden sm:inline">{isSirenMuted ? "Unmute" : "Mute Siren"}</span>
                </button>

                <button
                  onClick={handleSimulateSafe}
                  className="px-3.5 py-1.5 rounded-full bg-white hover:bg-zinc-100 text-red-700 text-xs font-black shadow-lg active:scale-95 transition-all cursor-pointer whitespace-nowrap"
                  title="Simulate 180 degree return into safe Indian waters"
                >
                  ↩️ Return Course (180°)
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="fixed bottom-5 left-4 sm:bottom-6 sm:left-6 z-[60] max-w-[calc(100vw-2rem)] sm:max-w-sm w-auto font-['Outfit',sans-serif] pointer-events-auto">

      {/* Minimized Pill Badge */}
      {isMinimized ? (
        <motion.button
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={() => setIsMinimized(false)}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-full border backdrop-blur-xl shadow-2xl cursor-pointer transition-all hover:scale-105 ${
            isBreach 
              ? 'bg-red-950/95 border-red-500 text-red-200 animate-pulse' 
              : (isCaution 
                  ? 'bg-amber-950/95 border-amber-500 text-amber-200' 
                  : 'bg-zinc-900/95 hover:bg-zinc-800 border-zinc-700/80 text-white')
          }`}
          title="Click to show Offline GPS IMBL Guard"
        >
          <span className={`w-2.5 h-2.5 rounded-full ${isBreach ? 'bg-red-500 animate-ping' : (isCaution ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500 animate-pulse')}`} />
          {isBreach ? <AlertOctagon className="w-4 h-4 text-red-400" /> : <ShieldCheck className="w-4 h-4 text-emerald-400" />}
          <span className="text-[11px] font-mono font-bold">
            {isBreach ? "OUT OF BORDER (0.0 NM)" : `${geofenceState.distanceNM} NM to Border`}
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-zinc-800 text-zinc-400 font-semibold">Show</span>
        </motion.button>
      ) : (
        /* Floating Compact HUD Pill */
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-3.5 rounded-3xl backdrop-blur-xl border shadow-xl transition-all ${
            isBreach
              ? 'bg-red-950/95 border-red-500 text-white shadow-2xl shadow-red-900/50'
              : (isCaution
                  ? 'bg-amber-950/90 border-amber-500 text-white'
                  : 'bg-zinc-900/90 border-zinc-700/80 text-white')
          }`}
        >
          <div className="flex items-center justify-between gap-2.5">
            <div className="flex items-center space-x-2.5 min-w-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                isBreach
                  ? 'bg-red-600 text-white animate-bounce'
                  : (isCaution ? 'bg-amber-500 text-white' : 'bg-emerald-600 text-white')
              }`}>
                {isBreach ? <AlertOctagon className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
              </div>

              <div className="min-w-0">
                <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                  <Radio className={`w-3 h-3 ${isBreach ? 'text-red-400 animate-ping' : 'text-emerald-400 animate-pulse'}`} />
                  <span>{isBreach ? "🚨 BORDER BREACH ALERT" : "Offline GPS IMBL Guard"}</span>
                </div>
                <div className={`text-xs font-black truncate font-mono ${isBreach ? 'text-red-300' : 'text-white'}`}>
                  {isBreach ? "OUT OF BORDER / FOREIGN WATERS" : `${geofenceState.distanceNM} NM to Border`}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-1.5 shrink-0">
              <button
                onClick={toggleMute}
                className={`p-2 rounded-xl transition-all cursor-pointer ${
                  isSirenMuted ? 'bg-zinc-800 text-zinc-400' : 'bg-blue-600 text-white hover:bg-blue-500'
                }`}
                title={isSirenMuted ? "Enable Siren" : "Mute Siren"}
              >
                {isSirenMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 animate-pulse" />}
              </button>

              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="px-2.5 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-bold text-[11px] cursor-pointer transition-colors"
              >
                {isExpanded ? "Hide" : "Details"}
              </button>

              <button
                onClick={() => setIsMinimized(true)}
                className="p-1.5 rounded-xl bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 cursor-pointer transition-colors"
                title="Hide / Minimize IMBL Guard"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Expandable Geofence Telemetry & Demo Controls */}
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="pt-3 mt-3 border-t border-zinc-800 space-y-2.5 text-xs text-zinc-300"
            >
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div className="p-2 rounded-xl bg-zinc-950/60 border border-zinc-800">
                  <span className="text-zinc-500 block text-[9px] uppercase">GPS Lat/Lon</span>
                  <strong>{currentCoords.lat.toFixed(4)}°N, {currentCoords.lon.toFixed(4)}°E</strong>
                </div>
                <div className="p-2 rounded-xl bg-zinc-950/60 border border-zinc-800">
                  <span className="text-zinc-500 block text-[9px] uppercase">Threat Level</span>
                  <strong className={isBreach ? 'text-red-400 font-bold' : (isCaution ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold')}>
                    {geofenceState.threatLevel}
                  </strong>
                </div>
              </div>

              <div className="text-[11px] leading-relaxed text-zinc-300">
                Nearest: <strong className="text-white">{geofenceState.nearestBorderName}</strong>
              </div>

              {/* Hackathon Demo Simulation Buttons */}
              <div className="pt-1.5 border-t border-zinc-800/80 flex items-center space-x-2">
                <button
                  onClick={handleSimulateBreach}
                  className="flex-1 py-1.5 rounded-xl bg-red-600/30 hover:bg-red-600/50 border border-red-500/50 text-red-300 text-[10px] font-bold cursor-pointer transition-all flex items-center justify-center space-x-1"
                >
                  <AlertOctagon className="w-3 h-3" />
                  <span>Test 1.29 NM Breach Alarm</span>
                </button>
                <button
                  onClick={handleSimulateSafe}
                  className="flex-1 py-1.5 rounded-xl bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/50 text-emerald-300 text-[10px] font-bold cursor-pointer transition-all flex items-center justify-center space-x-1"
                >
                  <ShieldCheck className="w-3 h-3" />
                  <span>Reset Safe (Kochi)</span>
                </button>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
      </div>
    </>
  );
};
