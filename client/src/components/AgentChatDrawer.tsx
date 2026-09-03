import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Cpu, 
  Sparkles, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  Compass, 
  ShieldCheck, 
  Satellite,
  Layers,
  ArrowRight
} from 'lucide-react';
import { ChatResponsePayload, AgentExecutionStep } from '../types';
import { speakText, stopSpeech, getBcp47LangTag } from '../utils/speechUtils';
import { FormattedMarkdown } from './FormattedMarkdown';
import { t } from '../utils/translations';

interface AgentChatDrawerProps {
  onSendMessage: (query: string) => void;
  isLoading: boolean;
  latestResponse: ChatResponsePayload | null;
  currentLang: string;
}

export const AgentChatDrawer: React.FC<AgentChatDrawerProps> = ({
  onSendMessage,
  isLoading,
  latestResponse,
  currentLang
}) => {
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [expandedTrace, setExpandedTrace] = useState(true);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Quick preset chips
  const PRESET_QUERIES = [
    { label: "🐟 Nearest Tuna PFZ (Kochi)", query: "Where is the nearest Potential Fishing Zone for Tuna from Kochi today?" },
    { label: "🛡️ Sea Venture Safety", query: "Is it safe to venture into the sea tomorrow morning from Chennai?" },
    { label: "🛑 IMBL Border Check", query: "What is the closest distance to Sri Lanka IMBL from Rameswaram?" },
    { label: "🌪️ Cyclone Warnings", query: "Are there any cyclone or lightning alerts in Bay of Bengal?" }
  ];

  // Speech Recognition (STT)
  const handleToggleMic = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser. Please type your query.");
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = getBcp47LangTag(currentLang);

    if (!isListening) {
      setIsListening(true);
      recognition.start();

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
        onSendMessage(transcript);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };
    } else {
      recognition.stop();
      setIsListening(false);
    }
  };

  // Text to Speech (TTS)
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

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-3xl border border-slate-200 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shadow-sm">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-900 flex items-center space-x-2">
              <span>{t('agentic_assistant', currentLang)}</span>
              <span className="text-[10px] font-black px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                Multi-Agent DAG
              </span>
            </h2>
            <p className="text-[11px] text-slate-500 font-medium">
              {t('autonomous_reasoning', currentLang)}
            </p>
          </div>
        </div>

        {latestResponse && (
          <button
            onClick={() => handleSpeak(latestResponse.response.tts_speech_text, latestResponse.language.voice_code)}
            className={`p-2 rounded-xl border transition-all cursor-pointer ${
              isSpeaking 
                ? 'bg-blue-600 text-white border-blue-600 shadow-md animate-pulse' 
                : 'bg-white text-slate-700 hover:text-blue-600 hover:bg-blue-50 border-slate-200'
            }`}
            title="Read aloud in regional language"
          >
            {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
        )}
      </div>

      {/* Preset Query Chips */}
      <div className="px-4 py-2.5 border-b border-slate-100 bg-slate-50/50 flex items-center space-x-2 overflow-x-auto no-scrollbar">
        {PRESET_QUERIES.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => onSendMessage(preset.query)}
            disabled={isLoading}
            className="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-semibold bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 hover:border-blue-300 transition-all shadow-xs cursor-pointer"
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Main Conversation & Reasoning Area */}
      <div className="flex-1 p-4 md:p-5 overflow-y-auto space-y-4 bg-slate-50/30">
        {isLoading && (
          <div className="p-5 rounded-2xl bg-white border border-blue-200 space-y-3.5 animate-pulse shadow-md">
            <div className="flex items-center space-x-2 text-blue-700 text-xs font-extrabold">
              <Sparkles className="w-4 h-4 animate-spin text-blue-600" />
              <span>Blue Orbit Multi-Agent Network Collaborating...</span>
            </div>
            <div className="space-y-2 text-xs text-slate-700">
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
                <span>Decomposing spatial intent & querying Oceansat-3 OCM-3 products...</span>
              </div>
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>Computing SST Thermal Front × Chlorophyll-a Coincidence Gradient...</span>
              </div>
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>Evaluating IMBL geofence buffer & A* weather routing clearance...</span>
              </div>
            </div>
          </div>
        )}

        {latestResponse && !isLoading && (
          <div className="space-y-4">
            {/* User Query Echo */}
            <div className="flex justify-end">
              <div className="max-w-[85%] px-4 py-2.5 rounded-2xl rounded-tr-sm bg-blue-600 text-white font-medium text-xs shadow-md">
                {latestResponse.query}
              </div>
            </div>

            {/* Agent Primary Synthesized Response Card */}
            <div className="bg-white p-5 rounded-3xl border border-blue-200 space-y-3.5 shadow-md">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-black flex items-center justify-center text-[10px]">
                    ISRO
                  </div>
                  <span className="text-xs font-black text-slate-900">
                    Verified Advisory · {latestResponse.reference_port.name}
                  </span>
                </div>
                <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                  {latestResponse.language.native} ({latestResponse.language.name})
                </span>
              </div>

              {/* Formatted Markdown Content */}
              <FormattedMarkdown 
                content={latestResponse.response.markdown} 
                className="text-xs leading-relaxed text-slate-800 font-medium"
                strongClassName="font-bold text-slate-900"
                bulletClassName="text-blue-600"
              />

              {/* Quick Insight Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2.5 border-t border-slate-100">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="text-[10px] text-slate-500 font-semibold">Sea Venture Verdict</div>
                  <div className={`text-xs font-black mt-0.5 ${
                    latestResponse.weather_and_safety.safety_status === 'SAFE_FOR_VENTURE' ? 'text-emerald-700' : 'text-amber-700'
                  }`}>
                    {latestResponse.weather_and_safety.safety_status.replace(/_/g, ' ')}
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="text-[10px] text-slate-500 font-semibold">Dominant Species</div>
                  <div className="text-xs font-black text-blue-700 mt-0.5">
                    {latestResponse.top_pfz.dominant_species}
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 col-span-2 sm:col-span-1">
                  <div className="text-[10px] text-slate-500 font-semibold">Nearest IMBL Distance</div>
                  <div className="text-xs font-black text-slate-900 mt-0.5 font-mono">
                    {latestResponse.geofence_status.nearest_imbl.distance_nautical_miles} NM
                  </div>
                </div>
              </div>
            </div>

            {/* Collapsible Multi-Agent Reasoning DAG Trace */}
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden text-xs shadow-sm">
              <button
                onClick={() => setExpandedTrace(!expandedTrace)}
                className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100 flex items-center justify-between font-extrabold text-slate-800 transition-colors cursor-pointer"
              >
                <span className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-blue-600" />
                  <span>Agent Execution Chain ({latestResponse.evidence_and_provenance.execution_steps_count} Specialized Agents)</span>
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-blue-700 font-mono font-bold">
                    {latestResponse.execution_metadata.total_latency_ms}ms
                  </span>
                  {expandedTrace ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </button>

              {expandedTrace && (
                <div className="p-3.5 space-y-3 bg-white border-t border-slate-200">
                  {latestResponse.evidence_and_provenance.execution_trace.map((step, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-extrabold text-blue-700 flex items-center space-x-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{step.agent}</span>
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">{step.duration_ms}ms</span>
                      </div>
                      <p className="text-xs text-slate-700 leading-snug font-medium">
                        {step.thought}
                      </p>
                      <div className="text-[11px] text-emerald-800 font-mono bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                        ➔ {step.output_summary}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Box & Voice Trigger */}
      <form onSubmit={handleFormSubmit} className="p-3.5 border-t border-slate-200 bg-white">
        <div className="relative flex items-center bg-slate-50 border border-slate-300 rounded-2xl p-1.5 shadow-inner focus-within:border-blue-500 focus-within:bg-white transition-all">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={t('drawer_placeholder', currentLang)}

            className="flex-1 bg-transparent px-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none font-medium"
            disabled={isLoading}
          />

          <button
            type="button"
            onClick={handleToggleMic}
            className={`p-2.5 rounded-xl transition-all cursor-pointer ${
              isListening 
                ? 'bg-red-600 text-white animate-ping' 
                : 'text-slate-500 hover:text-blue-600 hover:bg-slate-200'
            }`}
            title="Speak query (Web Speech STT)"
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="ml-1 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-xs transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-blue-600/30 cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
