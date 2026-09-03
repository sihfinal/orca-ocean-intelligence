import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Sparkles, 
  Plus, 
  Copy, 
  Check, 
  ArrowUp,
  Fish,
  ShieldCheck,
  Download,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatResponsePayload } from '../types';
import { speakText, stopSpeech, getBcp47LangTag, isAudioCachePreloaded, preloadAllRegionalAudioPacks } from '../utils/speechUtils';
import { FormattedMarkdown } from './FormattedMarkdown';
import { DecisionEvidencePanel } from './DecisionEvidencePanel';
import { t } from '../utils/translations';

interface Message {
  id: string;
  sender: 'user' | 'blueorbit' | 'orca';
  text: string;
  timestamp: string;
  data?: ChatResponsePayload;
}

interface AIChatStudioProps {
  onSendMessage: (query: string, langOverride?: string) => Promise<any>;
  isLoading: boolean;
  latestResponse: ChatResponsePayload | null;
  currentLang: string;
  setCurrentLang: (lang: string) => void;
  onVoiceSetupClick?: () => void;
  onNavigateToMap?: () => void;
}

export const AIChatStudio: React.FC<AIChatStudioProps> = ({
  onSendMessage,
  isLoading,
  latestResponse,
  currentLang,
  setCurrentLang
}) => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [expandedDecisionId, setExpandedDecisionId] = useState<string | null>(null);
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isAudioCached, setIsAudioCached] = useState(() => isAudioCachePreloaded());
  const [isCaching, setIsCaching] = useState(false);
  const [cacheProgress, setCacheProgress] = useState(0);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDirectCache = async () => {
    if (isCaching) return;
    setIsCaching(true);
    setCacheProgress(5);
    const success = await preloadAllRegionalAudioPacks((pct) => {
      setCacheProgress(pct);
    });
    if (success) {
      setIsAudioCached(true);
    }
    setIsCaching(false);
  };

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // When language is switched from Header dropdown or parent, dynamically sync the last AI response
  useEffect(() => {
    if (latestResponse && latestResponse.response?.markdown) {
      setMessages(prev => {
        if (prev.length === 0) return prev;
        const lastIdx = prev.length - 1;
        if (prev[lastIdx].sender === 'blueorbit' || prev[lastIdx].sender === 'orca') {
          if (prev[lastIdx].text !== latestResponse.response.markdown) {
            const updated = [...prev];
            updated[lastIdx] = {
              ...updated[lastIdx],
              text: latestResponse.response.markdown,
              data: latestResponse
            };
            return updated;
          }
        }
        return prev;
      });
    }
  }, [latestResponse]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputText;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputText('');

    const res = await onSendMessage(textToSend, currentLang);
    if (res && res.response?.markdown) {
      const newMsgId = `msg-${Date.now()}`;
      setMessages(prev => [
        ...prev,
        {
          id: newMsgId,
          sender: 'blueorbit',
          text: res.response.markdown,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          data: res
        }
      ]);
    } else {
      const errorMsgId = `msg-err-${Date.now()}`;
      setMessages(prev => [
        ...prev,
        {
          id: errorMsgId,
          sender: 'blueorbit',
          text: "⚠️ **Service Notice**: Unable to connect to Blue Orbit AI reasoning engine. Please ensure your device has internet access and try again.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  };

  // Speech to Text (STT) - Full 13 Indian Languages Support
  const handleToggleMic = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setSpeechError("Speech recognition is not supported in this browser. Please use keyboard input.");
      setTimeout(() => setSpeechError(null), 4000);
      return;
    }

    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = getBcp47LangTag(currentLang);

      if (!isListening) {
        setIsListening(true);
        setSpeechError(null);
        recognition.start();

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setIsListening(false);
          handleSend(transcript);
        };

        recognition.onerror = (err: any) => {
          console.warn("[Voice] Speech recognition error:", err);
          setIsListening(false);
          if (err.error === 'not-allowed') {
            setSpeechError("Microphone permission denied. Please allow microphone access in browser settings.");
            setTimeout(() => setSpeechError(null), 4500);
          }
        };
        recognition.onend = () => setIsListening(false);
      } else {
        recognition.stop();
        setIsListening(false);
      }
    } catch (e) {
      console.warn("[Voice] Web Speech API initialization error:", e);
      setIsListening(false);
      setSpeechError("Unable to start microphone audio capture.");
      setTimeout(() => setSpeechError(null), 4000);
    }
  };

  // Text to Speech (TTS) - Full 13 Indian Languages Support
  const handleSpeak = (msgId: string, text: string, voiceCode?: string) => {
    if (speakingId === msgId) {
      stopSpeech();
      setSpeakingId(null);
      return;
    }

    const effectiveLang = voiceCode || currentLang || 'en';
    speakText(
      text,
      effectiveLang,
      () => setSpeakingId(msgId),
      () => setSpeakingId(null),
      () => setSpeakingId(null)
    );
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="relative min-h-screen w-full bg-[#fcfbf8] text-[#111113] flex flex-col font-['Outfit',sans-serif] overflow-hidden selection:bg-blue-100 selection:text-blue-950">
      
      {/* 1. EXACT 1:1 LOVABLE VIBRANT BLUE ANNULAR HALO */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center z-0">
        <div 
          className="w-[880px] sm:w-[1020px] h-[640px] sm:h-[720px] rounded-[100%]"
          style={{
            background: 'radial-gradient(ellipse 55% 48% at 50% 50%, rgba(252, 251, 248, 0) 0%, rgba(252, 251, 248, 0) 26%, rgba(96, 165, 250, 0.85) 54%, rgba(37, 99, 235, 0.95) 68%, rgba(96, 165, 250, 0.7) 78%, rgba(252, 251, 248, 0) 95%)',
            filter: 'blur(45px)',
          }}
        />
      </div>

      {/* STATE 1: EXACT 1:1 LOVABLE HERO WITH CENTER CHATBOX */}
      {!hasMessages && (
        <div className="relative z-10 flex-1 flex flex-col items-center justify-center text-center max-w-4xl w-full mx-auto px-4 sm:px-6 my-auto pt-24 pb-16">
          
          {/* Main Headline: Responsive Sizing */}
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-[#111113] tracking-[-0.035em] leading-[1.1] select-none mb-4 sm:mb-6"
          >
            {t('reasoning_by_design', currentLang)}
          </motion.h1>

          {/* 2-Line Subtitle Description */}
          <motion.p 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-[#52525b] text-sm sm:text-base md:text-[17px] max-w-[640px] font-normal leading-[1.6] mb-6 sm:mb-8 text-center px-2"
          >
            {t('chat_subtitle', currentLang)}
          </motion.p>

          {/* Action Buttons (Responsive Wrap) */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-wrap justify-center gap-2 sm:gap-3 mb-6 sm:mb-8 w-full max-w-lg"
          >
            <button
              onClick={() => handleSend("Where is the nearest Potential Fishing Zone for Tuna from Kochi today?")}
              className="px-3.5 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-medium text-white bg-[#111113] hover:bg-zinc-800 shadow-sm transition-all active:scale-98 cursor-pointer"
            >
              🐟 Tuna PFZ Advisory
            </button>

            <button
              onClick={() => handleSend("Is it safe to venture into the sea tomorrow morning?")}
              className="px-3.5 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-medium text-[#18181b] bg-white hover:bg-zinc-50 border border-[#e4e4e7] shadow-sm transition-all active:scale-98 cursor-pointer"
            >
              🛡️ Sea Safety Clearance
            </button>

            <button
              onClick={handleDirectCache}
              disabled={isCaching}
              className="px-3.5 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-medium text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 shadow-sm transition-all active:scale-98 cursor-pointer flex items-center space-x-1.5"
              title="Preload 13 Regional Indian Audio Packs into Local Device Cache"
            >
              {isCaching ? (
                <Loader2 className="w-3.5 h-3.5 text-emerald-600 animate-spin" />
              ) : isAudioCached ? (
                <Check className="w-3.5 h-3.5 text-emerald-600 stroke-[2.5]" />
              ) : (
                <Download className="w-3.5 h-3.5 text-emerald-600" />
              )}
              <span>{isCaching ? `Caching ${cacheProgress}%` : (isAudioCached ? "✓ Audio Cached" : "📥 Cache Audio Packs")}</span>
            </button>
          </motion.div>

          {/* Center Chat Box Capsule */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="w-full max-w-xl px-2 sm:px-0"
          >
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="relative flex items-center bg-white border border-[#e4e4e7] hover:border-zinc-400 focus-within:border-blue-500 rounded-full px-3.5 sm:px-5 py-2.5 sm:py-3 shadow-[0_10px_35px_rgba(0,0,0,0.06)] transition-all"
            >
              {/* Plus icon on left */}
              <button 
                type="button"
                className="p-1 rounded-full text-zinc-400 hover:text-zinc-700 transition-colors mr-2 cursor-pointer"
                title="New Query"
              >
                <Plus className="w-4 h-4" />
              </button>

              {/* Main Input Field */}
              <input
                ref={inputRef}
                type="text"
                autoFocus
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={t('chat_placeholder', currentLang)}
                className="flex-1 bg-transparent text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none font-normal"
                disabled={isLoading}
              />

              {/* Microphone Trigger */}
              <button
                type="button"
                onClick={handleToggleMic}
                className={`p-2 rounded-full transition-all mr-1 cursor-pointer ${
                  isListening 
                    ? 'bg-red-600 text-white animate-ping' 
                    : 'text-zinc-400 hover:text-zinc-700'
                }`}
                title="Speak query"
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Send Arrow Button */}
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-[#111113] hover:bg-zinc-800 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shrink-0 shadow-sm"
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            </form>
          </motion.div>
        </div>
      )}

      {/* STATE 2: Active Chat Conversation Stream */}
      {hasMessages && (
        <div className="relative z-10 flex-1 flex flex-col max-w-3xl w-full mx-auto px-4 pt-24 pb-36 sm:pb-32">
          <div className="space-y-6">
            <AnimatePresence>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'} space-y-1`}
                >
                  {msg.sender === 'user' ? (
                    <div className="max-w-[85%] sm:max-w-[75%] px-5 py-3 rounded-2xl bg-[#111113] text-white font-medium text-sm shadow-sm">
                      {msg.text}
                    </div>
                  ) : (
                    <div className="w-full bg-white/95 backdrop-blur-md p-6 rounded-2xl border border-[#e4e4e7] shadow-sm space-y-3">
                      <div className="flex items-center space-x-2 text-xs font-bold text-blue-600">
                        <Sparkles className="w-4 h-4" />
                        <span>Blue Orbit AI Advisory</span>
                      </div>

                      <FormattedMarkdown 
                        content={msg.text} 
                        className="text-sm leading-relaxed text-zinc-800 font-normal" 
                        strongClassName="font-bold text-zinc-950"
                        bulletClassName="text-blue-600"
                      />

                      {/* Tool actions: Audio speaker + Copy + Decision Badges */}
                      <div className="flex items-center justify-between pt-2 border-t border-zinc-100 flex-wrap gap-2">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleSpeak(
                              msg.id, 
                              msg.data?.response?.tts_speech_text || msg.text, 
                              msg.data?.language?.voice_code || currentLang
                            )}
                            className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                              speakingId === msg.id 
                                ? 'text-blue-600 bg-blue-50 animate-pulse' 
                                : 'text-zinc-400 hover:text-zinc-700 hover:bg-zinc-50'
                            }`}
                            title={speakingId === msg.id ? "Stop voice" : "Read aloud"}
                          >
                            {speakingId === msg.id ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                          </button>
                          <button
                            onClick={() => handleCopy(msg.id, msg.text)}
                            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-700 hover:bg-zinc-50 transition-colors cursor-pointer"
                            title="Copy response"
                          >
                            {copiedId === msg.id ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                          </button>
                        </div>

                        {/* Phase 8 & 9 Decision Chips & Inspect Toggle */}
                        {msg.data?.decision && (
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              msg.data.decision.decision_status === 'RECOMMENDED'
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                                : msg.data.decision.decision_status === 'NO_GO'
                                ? 'bg-rose-50 text-rose-700 border-rose-300'
                                : 'bg-amber-50 text-amber-700 border-amber-300'
                            }`}>
                              {msg.data.decision.decision_status}
                            </span>
                            <span className="font-mono text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100 text-[10px]">
                              {(msg.data.decision.confidence.overall_confidence * 100).toFixed(0)}% Conf
                            </span>
                            <button
                              onClick={() => setExpandedDecisionId(expandedDecisionId === msg.id ? null : msg.id)}
                              className="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 text-[10px] font-bold flex items-center space-x-1 transition-colors cursor-pointer"
                            >
                              <span>{expandedDecisionId === msg.id ? 'Hide Evidence' : 'Inspect Evidence'}</span>
                              {expandedDecisionId === msg.id ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            </button>
                          </div>
                        )}
                      </div>

                      {/* Inline Expanded Decision & Evidence Panel */}
                      {expandedDecisionId === msg.id && msg.data?.decision && (
                        <div className="pt-3 border-t border-zinc-100 animate-in fade-in duration-200">
                          <DecisionEvidencePanel
                            decision={msg.data.decision}
                            evidencePackage={msg.data.evidence_package}
                            claimValidation={msg.data.claim_validation}
                            currentLang={currentLang}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Speech Error Banner */}
            {speechError && (
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center space-x-2 animate-in fade-in duration-200">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>{speechError}</span>
              </div>
            )}

            {isLoading && (
              <div className="flex items-center space-x-2.5 text-zinc-500 text-xs font-medium pl-2 pt-3 animate-pulse">
                <Sparkles className="w-4 h-4 text-blue-600 animate-spin" />
                <span>{t('thinking', currentLang)}</span>
              </div>
            )}

            <div ref={chatBottomRef} />
          </div>

          {/* Docked Bottom Search Box when in Conversation */}
          <div className="fixed bottom-6 left-0 right-0 z-40 max-w-2xl w-full mx-auto px-4">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="relative flex items-center bg-white border border-[#e4e4e7] rounded-full px-5 py-3 shadow-xl focus-within:border-blue-500 transition-all"
            >
              <button 
                type="button"
                onClick={() => setMessages([])}
                className="p-1 rounded-full text-zinc-400 hover:text-zinc-700 transition-colors mr-2 cursor-pointer"
                title="New Chat"
              >
                <Plus className="w-4 h-4" />
              </button>

              <input
                type="text"
                autoFocus
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={t('chat_placeholder', currentLang)}
                className="flex-1 bg-transparent text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none font-normal"
                disabled={isLoading}
              />

              <button
                type="button"
                onClick={handleToggleMic}
                className={`p-2 rounded-full transition-all mr-1 cursor-pointer ${
                  isListening 
                    ? 'bg-red-600 text-white animate-ping' 
                    : 'text-zinc-400 hover:text-zinc-700'
                }`}
                title="Speak query"
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-[#111113] hover:bg-zinc-800 text-white flex items-center justify-center transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shrink-0 shadow-sm"
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
