import React, { useState, useRef, useEffect } from 'react';
import { 
  Cpu, 
  Sparkles, 
  Send, 
  Mic, 
  Volume2, 
  VolumeX, 
  Activity, 
  ShieldCheck, 
  Compass, 
  Layers, 
  Fish, 
  Waves, 
  Radio, 
  CheckCircle2, 
  Zap, 
  Clock, 
  ArrowRight,
  RefreshCw,
  GitBranch,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import HolographicBeams from './ui/beams-background';
import DotMatrixText from './ui/dot-text';
import { SatelliteTelemetry, ChatResponsePayload } from '../types';
import { speakText, stopSpeech } from '../utils/speechUtils';
import { FormattedMarkdown } from './FormattedMarkdown';
import { t } from '../utils/translations';

interface AgentDAGStudioProps {
  satellites: SatelliteTelemetry[];
  latestResponse: ChatResponsePayload | null;
  isLoading: boolean;
  onSendMessage: (query: string, lang?: string) => void;
  currentLang: string;
}

const PRESET_QUERIES = [
  { label: "🐟 Nearest Tuna PFZ (Kochi)", query: "Where is the nearest Potential Fishing Zone for Tuna from Kochi today?" },
  { label: "🛡️ Sea Venture Safety (Chennai)", query: "Is it safe to venture into the sea tomorrow morning from Chennai?" },
  { label: "🛑 IMBL Border Check (Rameswaram)", query: "What is the closest distance to Sri Lanka IMBL from Rameswaram?" },
  { label: "🌪️ Cyclone Warnings (Bay of Bengal)", query: "Are there any cyclone or lightning alerts in Bay of Bengal?" }
];

const DOMAIN_AGENTS = [
  {
    id: "planner",
    name: "Master Supervisor DAG Planner",
    role: "Intent Decomposition & Graph Orchestration",
    model: "NVIDIA NIM (LLaMA-3.1-8B)",
    status: "Active",
    color: "from-blue-600 to-cyan-500"
  },
  {
    id: "marine_data",
    name: "Marine EO Data Agent",
    role: "Oceansat-3 OCM-3 & INSAT-3DR TIR Ingestion",
    model: "ISRO NRSC Telemetry API",
    status: "Live Sync",
    color: "from-teal-500 to-emerald-500"
  },
  {
    id: "weather_hazard",
    name: "Weather & Marine Hazard Agent",
    role: "Wave, Wind, Squall & Cyclone Analytics",
    model: "IMD / INCOIS Hydrodynamics",
    status: "Operational",
    color: "from-amber-500 to-orange-500"
  },
  {
    id: "ocean_analytics",
    name: "Ocean Analytics & PFZ Engine",
    role: "Thermal-Chlorophyll Front Coincidence & HSI",
    model: "Coincidence Matrix Engine",
    status: "Active",
    color: "from-indigo-600 to-purple-500"
  },
  {
    id: "geospatial",
    name: "Geospatial & Geofencing Agent",
    role: "IMBL Boundary Clearance & A* Safe Routing",
    model: "Geodesic Haversine & A* Grid",
    status: "Enforcing",
    color: "from-rose-500 to-red-600"
  },
  {
    id: "synthesis",
    name: "Neural Synthesis & Multilingual Agent",
    role: "Indic Vernacular Grounding & Provenance PDF",
    model: "8-Language NMT & TTS",
    status: "Ready",
    color: "from-cyan-500 to-blue-600"
  }
];

export const AgentDAGStudio: React.FC<AgentDAGStudioProps> = ({
  satellites,
  latestResponse,
  isLoading,
  onSendMessage,
  currentLang
}) => {
  const [inputText, setInputText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showFullTrace, setShowFullTrace] = useState(true);
  const responseSectionRef = useRef<HTMLDivElement>(null);

  // Smoothly scroll to response when newly generated
  useEffect(() => {
    if (latestResponse && responseSectionRef.current) {
      responseSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [latestResponse]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleSpeak = (text: string, voiceCode?: string) => {
    if (isSpeaking) {
      stopSpeech();
      setIsSpeaking(false);
      return;
    }
    const effectiveLang = voiceCode || latestResponse?.language?.voice_code || currentLang || 'en';
    speakText(
      text,
      effectiveLang,
      () => setIsSpeaking(true),
      () => setIsSpeaking(false),
      () => setIsSpeaking(false)
    );
  };



  return (
    <div className="relative w-full min-h-screen font-['Outfit',sans-serif] bg-[#fcfbf8] text-slate-900 scroll-smooth flex flex-col justify-between select-none">
      
      {/* Holographic Beams with Rich Crimson, Indigo, Cyan Chromatic Colors on Bright Background */}
      <HolographicBeams 
        theme="light"
        density={20}
        speed={1.4}
        aberration={3.5}
        opacity={95}
      />

      {/* Main Content Area */}
      <div className="relative z-30 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-20 space-y-8 w-full">
        
        {/* Ultra-Modern Dot Matrix Hero Stage */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-center space-y-3 max-w-4xl mx-auto flex flex-col items-center"
        >
          {/* Dynamic Dot Matrix Typography Stage */}
          <div className="w-full h-32 sm:h-40 md:h-48 flex items-center justify-center">
            <DotMatrixText
              text={[
                "Multi-Agent DAG",
                "ISRO Ocean AI",
                "Autonomous Reasoning",
                "PFZ & IMBL Geo-DAG"
              ]}
              transition="fade"
              cycleInterval={3200}
              dotSize={4}
              gap={2}
              activeColor="#090d16"
              inactiveColor="rgba(15, 23, 42, 0.08)"
              showInactive={true}
              fontFamily="'Outfit', sans-serif"
              className="w-full h-full drop-shadow-[0_0_20px_rgba(0,0,0,0.08)]"
            />
          </div>

          {/* Refined High-Contrast Subtitle */}
          <p className="text-slate-800 text-xs sm:text-sm md:text-base max-w-xl mx-auto font-semibold leading-relaxed">
            {t('dag_subtitle', currentLang)}
          </p>
        </motion.div>

        {/* Ultra-Clean Borderless Interactive Query Launcher */}
        <div className="max-w-2xl mx-auto space-y-3.5">
          <form onSubmit={handleSend} className="relative flex items-center">
            <div className="absolute left-4 text-blue-600 pointer-events-none">
              <Sparkles className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={t('dag_placeholder', currentLang)}
              className="w-full pl-11 pr-28 py-4 rounded-full bg-white text-slate-950 placeholder-slate-400 font-medium border-0 outline-none focus:outline-none focus:ring-0 shadow-lg shadow-slate-900/5 transition-all text-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              className="absolute right-1.5 px-5 py-2.5 rounded-full bg-slate-950 text-white font-bold text-xs hover:bg-slate-800 transition-all flex items-center space-x-1.5 shadow-md active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-white" />
              ) : (
                <>
                  <span>{t('run_dag', currentLang)}</span>
                  <Send className="w-3 h-3 text-white" />
                </>
              )}
            </button>
          </form>

          {/* Borderless Preset Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            {PRESET_QUERIES.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => onSendMessage(preset.query)}
                disabled={isLoading}
                className="px-3.5 py-1.5 rounded-full text-xs font-bold bg-white text-slate-800 hover:text-blue-700 transition-all shadow-xs hover:shadow-sm cursor-pointer active:scale-95 whitespace-nowrap border-0"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Loading Spinner / Thinking State right under the input */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-5 rounded-3xl bg-white/95 border border-blue-200 shadow-xl backdrop-blur-xl space-y-3"
            >
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-blue-50 text-blue-600 animate-spin">
                  <RefreshCw className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    {t('executing_dag', currentLang)}
                  </h4>
                  <p className="text-xs text-slate-500 font-medium">
                    Coordinating 6 domain agents across Oceansat-3, INSAT-3DR, and IMD/INCOIS hydrodynamics.
                  </p>
                </div>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 via-cyan-500 to-rose-500 h-full w-2/3 animate-pulse rounded-full" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* AI Answer & Execution Inspector: PLACED DIRECTLY UNDER THE QUERY LAUNCHER */}
        {latestResponse && (
          <motion.div 
            ref={responseSectionRef}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="p-6 md:p-8 rounded-3xl bg-white/95 border border-slate-200 shadow-2xl backdrop-blur-2xl space-y-6 text-slate-900"
          >
            {/* Primary Synthesized Marine Advisory Box */}
            <div className="p-5 rounded-2xl bg-blue-50/70 border border-blue-200/90 space-y-3 text-slate-800 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-blue-800 uppercase tracking-wider flex items-center space-x-1.5">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span>Synthesized Marine Advisory ({latestResponse.language.name})</span>
                </span>
                
                <div className="flex items-center space-x-3">
                  <span className="text-[11px] font-mono text-slate-600">
                    Confidence: <strong className="text-emerald-700">{latestResponse.evidence_and_provenance.overall_confidence_percent}%</strong>
                  </span>
                  <button
                    onClick={() => handleSpeak(latestResponse.response.tts_speech_text, latestResponse.language.voice_code)}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-white hover:bg-blue-100 text-blue-700 font-bold text-xs border border-blue-200 transition-all cursor-pointer shadow-xs"
                  >
                    {isSpeaking ? <VolumeX className="w-3.5 h-3.5 text-blue-700" /> : <Volume2 className="w-3.5 h-3.5 text-blue-700" />}
                    <span>{isSpeaking ? 'Stop' : `Listen (${latestResponse.language.native})`}</span>
                  </button>
                </div>
              </div>

              <FormattedMarkdown 
                content={latestResponse.response.markdown} 
                className="text-sm text-slate-800 leading-relaxed font-normal pt-1" 
                strongClassName="font-bold text-slate-900"
                bulletClassName="text-blue-600"
              />
            </div>

            {/* Collapsible DAG Execution Trace & Step-by-Step Chain */}
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-widest font-mono">
                    DAG Provenance Chain
                  </span>
                  <span className="text-xs font-mono text-slate-500">
                    Latency: <strong className="text-slate-900">{latestResponse.execution_metadata.total_latency_ms} ms</strong>
                  </span>
                </div>

                <button
                  onClick={() => setShowFullTrace(!showFullTrace)}
                  className="flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
                >
                  <span>{showFullTrace ? 'Hide Step Traces' : 'Show 6 Agent Step Traces'}</span>
                  {showFullTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              </div>

              <AnimatePresence>
                {showFullTrace && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-3 overflow-hidden"
                  >
                    {latestResponse.evidence_and_provenance.execution_trace.map((step, idx) => (
                      <div 
                        key={idx} 
                        className="p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-blue-300 transition-all space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-bold text-blue-700 flex items-center space-x-2">
                            <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold font-mono">
                              {idx + 1}
                            </span>
                            <span>{step.agent}</span>
                          </span>
                          <span className="text-xs font-mono font-bold text-slate-600 bg-white px-2.5 py-0.5 rounded-md border border-slate-200">
                            {step.duration_ms} ms
                          </span>
                        </div>

                        <p className="text-xs text-slate-700 font-medium pl-8">
                          {step.thought}
                        </p>

                        <div className="ml-8 p-2.5 rounded-xl bg-white border border-slate-200 text-xs font-mono text-emerald-700">
                          ➔ {step.output_summary}
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* 6 Domain Agent Graph Constellation (Overview Section) */}
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <h3 className="text-sm font-black text-slate-950 flex items-center space-x-2 tracking-wide">
              <GitBranch className="w-4 h-4 text-blue-600" />
              <span>{t('agent_architecture', currentLang)}</span>
            </h3>
            <span className="text-xs font-mono text-blue-800 font-black bg-blue-100 px-3.5 py-1 rounded-full border border-blue-300 shadow-xs">
              6 Active Domain Agents
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {DOMAIN_AGENTS.map((agent, idx) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm hover:shadow-md hover:border-blue-400 backdrop-blur-xl transition-all space-y-3 group"
              >
                <div className="flex items-center justify-between">
                  <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center text-white font-black text-xs shadow-xs group-hover:scale-105 transition-transform`}>
                    0{idx + 1}
                  </div>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                    {agent.status}
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-950 group-hover:text-blue-600 transition-colors">
                    {agent.name}
                  </h4>
                  <p className="text-xs text-slate-600 font-medium mt-0.5">
                    {agent.role}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>{t('engine', currentLang)}:</span>
                  <span className="text-slate-950 font-bold">{agent.model}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
export default AgentDAGStudio;
