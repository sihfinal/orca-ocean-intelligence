import React, { useState, useEffect } from 'react';
import { 
  X, 
  Volume2, 
  VolumeX, 
  Download, 
  CheckCircle2, 
  HardDrive, 
  Zap,
  ShieldCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  SUPPORTED_LANGUAGES, 
  speakText, 
  stopSpeech, 
  preloadAllRegionalAudioPacks,
  isAudioCachePreloaded
} from '../utils/speechUtils';

interface VoicePacksModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCacheComplete?: () => void;
}

const SAMPLE_GREETINGS: Record<string, string> = {
  en: "Hello! Welcome to Blue Orbit marine intelligence.",
  hi: "नमस्ते! ब्लू ऑर्बिट समुद्री सहायक में आपका स्वागत है।",
  ta: "வணக்கம்! புளூ ஆர்பிட் கடல்சார் உதவியாளருக்கு வரவேற்கிறோம்.",
  te: "నమస్కారం! బ్లూ ఆర్బిట్ సముద్ర సహాయకుడికి స్వాగతం.",
  ml: "നമസ്കാരം! ബ്ലൂ ഓർബിറ്റ് സമുദ്ര സഹായിയിലേക്ക് സ്വാഗതം.",
  bn: "নমস্কার! ব্লু অরবিট সামুদ্রিক সহকারীতে স্বাগতম।",
  gu: "નમસ્તે! બ્લુ ઓર્બિટ દરિયાઈ સહાયકમાં આપનું સ્વાગત છે.",
  mr: "नमस्कार! ब्लू ऑर्बिट सागरी सहाय्यकामध्ये आपले स्वागत आहे."
};

export const VoicePacksModal: React.FC<VoicePacksModalProps> = ({
  isOpen,
  onClose,
  onCacheComplete
}) => {
  const [testingLang, setTestingLang] = useState<string | null>(null);
  const [isPreloading, setIsPreloading] = useState<boolean>(false);
  const [preloadProgress, setPreloadProgress] = useState<number>(0);
  const [currentCachingLang, setCurrentCachingLang] = useState<string>('');
  const [isPreloaded, setIsPreloaded] = useState<boolean>(() => isAudioCachePreloaded());

  useEffect(() => {
    if (isOpen) {
      setIsPreloaded(isAudioCachePreloaded());
    }
    return () => {
      stopSpeech();
      setTestingLang(null);
    };
  }, [isOpen]);

  const handleTestVoice = (code: string) => {
    if (testingLang === code) {
      stopSpeech();
      setTestingLang(null);
      return;
    }

    setTestingLang(code);
    const sample = SAMPLE_GREETINGS[code] || "Blue Orbit voice test.";
    speakText(
      sample,
      code,
      () => setTestingLang(code),
      () => setTestingLang(null),
      () => setTestingLang(null)
    );
  };

  // Preload essential marine phrases for offline deep sea navigation
  const handlePreloadOfflineCache = async () => {
    setIsPreloading(true);
    setPreloadProgress(5);
    setCurrentCachingLang('Starting...');

    const success = await preloadAllRegionalAudioPacks((pct, langName) => {
      setPreloadProgress(pct);
      setCurrentCachingLang(langName);
    });

    if (success) {
      setIsPreloaded(true);
      if (onCacheComplete) onCacheComplete();
    }
    setIsPreloading(false);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[1200] flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md font-['Outfit',sans-serif]">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          className="w-full max-w-2xl bg-zinc-950 text-white rounded-3xl border border-zinc-800 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        >
          {/* Header */}
          <div className="p-5 sm:p-6 border-b border-zinc-800/80 flex items-center justify-between bg-zinc-900/60">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-black tracking-wide text-white flex items-center space-x-2">
                  <span>Offline Marine Audio Cache Manager</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-500/40 text-emerald-300 font-bold">
                    13 Languages
                  </span>
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Store marine speech audio packages in local device memory for 100% offline sea navigation.
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Scrollable Content Body */}
          <div className="p-5 sm:p-6 space-y-6 overflow-y-auto custom-scrollbar flex-1">
            
            {/* Main 1-Click Preload Hero Box */}
            <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-950/50 via-zinc-900/90 to-zinc-900 border border-emerald-500/30 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs sm:text-sm font-bold text-emerald-200">1-Click Regional Voice Pack Preloader</span>
                </div>
                {isPreloaded ? (
                  <span className="text-[11px] font-bold text-emerald-400 flex items-center space-x-1 bg-emerald-950/80 px-2.5 py-1 rounded-full border border-emerald-500/40">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Cache Storage Ready</span>
                  </span>
                ) : (
                  <span className="text-[11px] font-mono text-zinc-400">Deep-Sea Offline Cache</span>
                )}
              </div>

              <p className="text-xs text-zinc-300 leading-relaxed">
                Preload all 13 regional Indian language audio packs into your device's persistent cache. Once loaded, speech synthesis works instantly with <strong>zero latency and zero cellular network required</strong>.
              </p>

              {isPreloading ? (
                <div className="space-y-2 pt-1">
                  <div className="flex justify-between text-xs font-mono text-emerald-300">
                    <span>Caching: {currentCachingLang}</span>
                    <span>{preloadProgress}%</span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-2.5 overflow-hidden">
                    <div 
                      className="bg-emerald-500 h-full transition-all duration-300"
                      style={{ width: `${preloadProgress}%` }}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-3 pt-1">
                  <button
                    onClick={handlePreloadOfflineCache}
                    className={`px-5 py-2.5 rounded-2xl font-bold text-xs flex items-center space-x-2 transition-all cursor-pointer ${
                      isPreloaded 
                        ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/50 hover:bg-emerald-600/30' 
                        : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/40 active:scale-95'
                    }`}
                  >
                    <Download className="w-4 h-4" />
                    <span>{isPreloaded ? "Update / Re-Cache Audio Packs" : "Load All Audio Packs into Cache Now"}</span>
                  </button>

                  {isPreloaded && (
                    <span className="text-xs text-zinc-400">
                      ✓ 64 Marine Voice Phrases Cached
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Language Status & Audio Tester Grid */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-zinc-300">
                <span>Supported Regional Languages (Test Speech)</span>
                <span className="text-[11px] text-zinc-500 font-normal">Click play to test pronunciation</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {Object.values(SUPPORTED_LANGUAGES).map((lang) => {
                  const isTesting = testingLang === lang.code;

                  return (
                    <div
                      key={lang.code}
                      className="p-3 rounded-2xl bg-zinc-900/80 border border-zinc-800 flex items-center justify-between hover:border-zinc-700 transition-colors"
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <div className="w-8 h-8 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center font-bold text-xs text-zinc-200 shrink-0">
                          {lang.code.toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                            <span className="truncate">{lang.nativeName}</span>
                            <span className="text-zinc-500 font-normal text-[11px]">({lang.name})</span>
                          </div>
                          <div className="flex items-center space-x-1.5 text-[10px] mt-0.5 text-emerald-400 font-medium">
                            <CheckCircle2 className="w-2.5 h-2.5" />
                            <span>{isPreloaded ? "Offline Cache Ready" : "High-Fidelity Audio Ready"}</span>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => handleTestVoice(lang.code)}
                        className={`p-2 rounded-xl transition-all cursor-pointer ${
                          isTesting 
                            ? 'bg-emerald-600 text-white animate-pulse' 
                            : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300'
                        }`}
                        title={isTesting ? "Stop Audio" : `Test ${lang.name} Audio`}
                      >
                        {isTesting ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Offline Deep Sea Navigation Assurance Banner */}
            <div className="p-3.5 rounded-2xl bg-zinc-900/60 border border-zinc-800 text-[11px] text-zinc-400 flex items-start space-x-2.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div className="leading-relaxed">
                <strong className="text-zinc-200 block">Fishermen Sea-Venture Audio Resilience:</strong>
                All audio packages are stored using W3C Cache Storage API. When fishing vessels venture beyond 12 nautical miles where mobile signals drop, critical IMBL alarms, weather warnings, and navigational coordinates will speak in the chosen regional dialect without internet.
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-zinc-800 bg-zinc-900/40 flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-bold text-xs transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
