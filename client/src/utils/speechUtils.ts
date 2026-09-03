export interface SupportedLanguageInfo {
  code: string;
  name: string;
  nativeName: string;
  bcp47: string;
  speechAliases: string[];
}


export const SUPPORTED_LANGUAGES: Record<string, SupportedLanguageInfo> = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    bcp47: 'en-IN',
    speechAliases: ['en-IN', 'en_IN', 'en-GB', 'en-US', 'en', 'english', 'rishi', 'heera', 'neerja']
  },
  hi: {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    bcp47: 'hi-IN',
    speechAliases: ['hi-IN', 'hi_IN', 'hi', 'hindi', 'हिन्दी', 'madhur', 'swara', 'kalpana', 'hemant']
  },
  ta: {
    code: 'ta',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    bcp47: 'ta-IN',
    speechAliases: ['ta-IN', 'ta_IN', 'ta-LK', 'ta', 'tamil', 'தமிழ்', 'valluvar', 'iniya']
  },
  te: {
    code: 'te',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    bcp47: 'te-IN',
    speechAliases: ['te-IN', 'te_IN', 'te', 'telugu', 'తెలుగు', 'mohan', 'shruti', 'chitra']
  },
  ml: {
    code: 'ml',
    name: 'Malayalam',
    nativeName: 'മലയാളം',
    bcp47: 'ml-IN',
    speechAliases: ['ml-IN', 'ml_IN', 'ml', 'malayalam', 'മലയാളം', 'midhun', 'sobhana']
  },
  bn: {
    code: 'bn',
    name: 'Bengali',
    nativeName: 'বাংলা',
    bcp47: 'bn-IN',
    speechAliases: ['bn-IN', 'bn_IN', 'bn-BD', 'bn', 'bengali', 'bangla', 'বাংলা', 'bashkar', 'tanishaa']
  },
  gu: {
    code: 'gu',
    name: 'Gujarati',
    nativeName: 'ગુજરાતી',
    bcp47: 'gu-IN',
    speechAliases: ['gu-IN', 'gu_IN', 'gu', 'gujarati', 'ગુજરાતી', 'dhwani', 'niranjan']
  },
  mr: {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
    bcp47: 'mr-IN',
    speechAliases: ['mr-IN', 'mr_IN', 'mr', 'marathi', 'मराठी', 'aarohi', 'manohar']
  },
  kn: {
    code: 'kn',
    name: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    bcp47: 'kn-IN',
    speechAliases: ['kn-IN', 'kn_IN', 'kn', 'kannada', 'ಕನ್ನಡ', 'gagan', 'yash']
  },
  kok: {
    code: 'kok',
    name: 'Konkani',
    nativeName: 'कोंकणी',
    bcp47: 'kok-IN',
    speechAliases: ['kok-IN', 'kok_IN', 'kok', 'konkani', 'कोंकणी']
  },
  or: {
    code: 'or',
    name: 'Odia',
    nativeName: 'ଓଡ଼ିଆ',
    bcp47: 'or-IN',
    speechAliases: ['or-IN', 'or_IN', 'or', 'odia', 'oriya', 'ଓଡ଼ିଆ']
  },
  tcy: {
    code: 'tcy',
    name: 'Tulu',
    nativeName: 'ತುಳು',
    bcp47: 'tcy-IN',
    speechAliases: ['tcy-IN', 'tcy_IN', 'tcy', 'tulu', 'ತುಳು']
  },
  kfr: {
    code: 'kfr',
    name: 'Kutchi',
    nativeName: 'કચ્છી',
    bcp47: 'kfr-IN',
    speechAliases: ['kfr-IN', 'kfr_IN', 'kfr', 'kutchi', 'kachchi', 'કચ્છી']
  }
};


// Active audio elements and speech synthesis trackers
let activeUtterance: SpeechSynthesisUtterance | null = null;
let activeAudio: HTMLAudioElement | null = null;
let audioQueue: string[] = [];
let isAudioPlaying = false;
let cachedVoices: SpeechSynthesisVoice[] = [];


// Preload voices immediately on load
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  cachedVoices = window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => {
    cachedVoices = window.speechSynthesis.getVoices();
  };
}


/**
 * Resolves BCP-47 tag from language code
 */
export function getBcp47LangTag(langCode?: string): string {
  if (!langCode) return 'en-IN';
  const cleanCode = langCode.toLowerCase().trim();
  if (SUPPORTED_LANGUAGES[cleanCode]) {
    return SUPPORTED_LANGUAGES[cleanCode].bcp47;
  }
  for (const lang of Object.values(SUPPORTED_LANGUAGES)) {
    if (
      cleanCode === lang.code || 
      cleanCode === lang.bcp47.toLowerCase() ||
      lang.speechAliases.some(alias => cleanCode === alias.toLowerCase() || cleanCode.includes(alias.toLowerCase()))
    ) {
      return lang.bcp47;
    }
  }
  return 'en-IN';
}


/**
 * Strips markdown symbols, asterisks, headers, emojis, and code formatting
 * so the TTS engine speaks clean, natural vernacular sentences.
 */
export function cleanTextForSpeech(rawText: string): string {
  if (!rawText) return '';
  return rawText
    // Remove markdown headers and bullets
    .replace(/^#+\s+/gm, '')
    .replace(/^\s*[-*•]\s+/gm, '')
    // Remove bold/italics markers
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    // Remove inline code and code blocks
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    // Remove links
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // Remove common symbol abbreviations
    .replace(/\bkts\b/gi, 'knots')
    .replace(/\bnm\b/gi, 'nautical miles')
    // Remove emojis (preserve vernacular unicode characters)
    .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
    // Clean multiple whitespace / newlines
    .replace(/\n+/g, '. ')
    .replace(/\s+/g, ' ')
    .trim();
}


/**
 * Finds the best matching system voice installed on the user's OS/Browser.
 */
export function getBestVoiceForLanguage(langCode: string): SpeechSynthesisVoice | null {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;


  const voices = window.speechSynthesis.getVoices().length > 0 
    ? window.speechSynthesis.getVoices() 
    : cachedVoices;


  if (!voices || voices.length === 0) return null;


  const bcp47 = getBcp47LangTag(langCode).toLowerCase();
  const prefix = bcp47.split('-')[0];
  const langKey = langCode.toLowerCase().trim();
  const langInfo = SUPPORTED_LANGUAGES[langKey] || Object.values(SUPPORTED_LANGUAGES).find(l => l.bcp47.toLowerCase() === bcp47);


  // 1. Direct match on BCP-47
  let match = voices.find(v => v.lang.toLowerCase().replace('_', '-') === bcp47);
  if (match) return match;


  // 2. Exact language prefix match
  match = voices.find(v => {
    const vLang = v.lang.toLowerCase().replace('_', '-');
    return vLang.startsWith(`${prefix}-`) || vLang === prefix;
  });
  if (match) return match;


  // 3. Name alias match
  if (langInfo) {
    for (const alias of langInfo.speechAliases) {
      match = voices.find(v => 
        v.name.toLowerCase().includes(alias.toLowerCase()) || 
        v.lang.toLowerCase().includes(alias.toLowerCase())
      );
      if (match) return match;
    }
  }


  // 4. For English only, match Indian English or default voice
  if (prefix === 'en') {
    match = voices.find(v => v.lang.toLowerCase().includes('en-in') || v.lang.toLowerCase().includes('en_in'));
    return match || voices[0] || null;
  }


  return null;
}


const PROD_API_URL = 'https://orca-backend-0dxj.onrender.com';
const getApiBase = (): string => {
  if (typeof window !== 'undefined' && (window as any).VITE_API_URL) {
    return (window as any).VITE_API_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }
  return PROD_API_URL;
};


const AUDIO_CACHE_NAME = 'blue-orbit-marine-audio-v2';


/**
 * Splits long text into natural sentence chunks for smooth streaming audio
 */
function splitIntoAudioChunks(text: string, maxChunkLen: number = 180): string[] {
  const sentences = text.split(/([।!?.]+|\n+)/).filter(Boolean);
  const chunks: string[] = [];
  let current = '';


  for (let i = 0; i < sentences.length; i++) {
    const part = sentences[i].trim();
    if (!part) continue;
    if ((current + ' ' + part).length <= maxChunkLen) {
      current = current ? `${current} ${part}` : part;
    } else {
      if (current) chunks.push(current);
      if (part.length > maxChunkLen) {
        const words = part.split(/\s+/);
        let sub = '';
        for (const w of words) {
          if ((sub + ' ' + w).length <= maxChunkLen) {
            sub = sub ? `${sub} ${w}` : w;
          } else {
            if (sub) chunks.push(sub);
            sub = w;
          }
        }
        if (sub) current = sub;
      } else {
        current = part;
      }
    }
  }
  if (current) chunks.push(current);
  return chunks.length > 0 ? chunks : [text];
}


/**
 * Resolves or fetches audio blob from local Cache Storage / backend TTS for 100% cross-platform reliability on Windows, Mac, Android, iOS
 */
async function getCachedAudioSrc(langPrefix: string, textChunk: string): Promise<string> {
  const encoded = encodeURIComponent(textChunk);
  const apiBase = getApiBase();
  const serverTtsUrl = `${apiBase}/api/tts?text=${encoded}&lang=${langPrefix}`;


  if (typeof window === 'undefined' || !('caches' in window)) {
    return serverTtsUrl;
  }


  try {
    const cache = await caches.open(AUDIO_CACHE_NAME);
    const cachedResponse = await cache.match(serverTtsUrl);


    if (cachedResponse) {
      const blob = await cachedResponse.blob();
      return URL.createObjectURL(blob);
    }


    // Fetch from backend TTS proxy (CORS and Hotlink Safe)
    const netResponse = await fetch(serverTtsUrl);
    if (netResponse.ok) {
      cache.put(serverTtsUrl, netResponse.clone()).catch(() => {});
      const blob = await netResponse.blob();
      return URL.createObjectURL(blob);
    }
  } catch (err) {
    console.warn('[Cache Storage Read/Fetch Error, fallback to server URL]', err);
  }


  return serverTtsUrl;
}


/**
 * Plays queued audio chunks sequentially with offline cache resolution
 */
async function playNextAudioChunk(
  langPrefix: string,
  onEnd?: () => void,
  onError?: (e: any) => void
) {
  if (audioQueue.length === 0) {
    isAudioPlaying = false;
    activeAudio = null;
    if (onEnd) onEnd();
    return;
  }


  const chunk = audioQueue.shift()!;
  try {
    const audioSrc = await getCachedAudioSrc(langPrefix, chunk);
    const audio = new Audio();
    audio.src = audioSrc;
    audio.crossOrigin = 'anonymous';
    activeAudio = audio;
    isAudioPlaying = true;


    audio.onended = () => {
      playNextAudioChunk(langPrefix, onEnd, onError);
    };


    audio.onerror = (err) => {
      console.warn('[Audio chunk playback error, proceeding to next]', err);
      playNextAudioChunk(langPrefix, onEnd, onError);
    };


    audio.play().catch((err) => {
      console.warn('[Audio play interrupted/blocked]', err);
      playNextAudioChunk(langPrefix, onEnd, onError);
    });
  } catch (err) {
    console.warn('[Chunk resolution error]', err);
    playNextAudioChunk(langPrefix, onEnd, onError);
  }
}


/**
 * Core Essential Marine Phrases for all supported Indian Languages
 */
export const CORE_MARINE_AUDIO_PACK: Record<string, string[]> = {
  en: [
    "Hello! Welcome to Blue Orbit marine intelligence.",
    "Sea State verdict: Safe for Venture.",
    "Exercise caution. Wave swell is moderate.",
    "Hazardous sea condition. Do not venture into the sea.",
    "Emergency Distress SOS Activated. Coast Guard 1554 alerted.",
    "IMBL Border Violation Alert! Turn 180 degrees immediately.",
    "High confidence Potential Fishing Zone detected nearby.",
    "Safe weather-optimized navigation route generated."
  ],
  hi: [
    "नमस्ते! ब्लू ऑर्बिट समुद्री सहायक में आपका स्वागत है।",
    "समुद्र स्थिति: समुद्र में जाना पूरी तरह सुरक्षित है।",
    "सावधानी बरतें। समुद्र में मध्यम लहरें हैं।",
    "खतरनाक समुद्री स्थिति। समुद्र में न जाएं।",
    "आपातकालीन एसओएस संकेत सक्रिय। तटरक्षक 1554 को सूचित किया गया।",
    "अंतर्राष्ट्रीय समुद्री सीमा उल्लंघन चेतावनी! तुरंत 180 डिग्री मुड़ें।",
    "निकटतम उच्च-उत्पादक मछली पकड़ने का क्षेत्र खोजा गया।",
    "सुरक्षित नेविगेशन मार्ग तैयार किया गया है।"
  ],
  ta: [
    "வணக்கம்! புளூ ஆர்பிட் கடல்சார் உதவியாளருக்கு வரவேற்கிறோம்.",
    "கடல் நிலை: கடலுக்குச் செல்ல பாதுகாப்பானது.",
    "எச்சரிக்கையுடன் செயல்படவும். மிதமான அலைகள் உள்ளன.",
    "ஆபத்தான கடல் நிலை. கடலுக்குச் செல்ல வேண்டாம்.",
    "அவசர எஸ்ஓஎஸ் எச்சரிக்கை இயக்கப்பட்டது. கடலோரக் காவல் படைக்கு தெரிவிக்கப்பட்டது.",
    "சர்வதேச எல்லை மீறல் எச்சரிக்கை! உடனடியாக 180 பாகை திரும்பவும்.",
    "அருகிலுள்ள அதிக மீன்வள மண்டலம் கண்டறியப்பட்டது.",
    "பாதுகாப்பான வழித்தட திட்டம் உருவாக்கப்பட்டுள்ளது."
  ],
  te: [
    "నమస్కారం! బ్లూ ఆర్బిట్ సముద్ర సహాయకుడికి స్వాగతం.",
    "సముద్ర స్థితి: సముద్రంలోకి వెళ్లడం సురక్షితం.",
    "జాగ్రత్త వహించండి. మోస్తరు అలలు ఉన్నాయి.",
    "ప్రమాదకరమైన సముద్ర పరిస్థితి. సముద్రంలోకి వెళ్లవద్దు.",
    "అత్యవసర ఎస్ఓఎస్ సంకేతం ప్రారంభించబడింది.",
    "అంతర్జాతీయ సరిహద్దు ఉల్లంఘన హెచ్చరిక! వెంటనే వెనక్కి తిరగండి.",
    "సమీపంలో అధిక చేపల వేట ప్రాంతం కనుగొనబడింది.",
    "సురక్షితమైన నావిగేషన్ మార్గం రూపొందించబడింది."
  ],
  ml: [
    "നമസ്കാരം! ബ്ലൂ ഓർബിറ്റ് സമുദ്ര സഹായിയിലേക്ക് സ്വാഗതം.",
    "കടൽ അവസ്ഥ: കടലിൽ പോകുന്നത് സുരക്ഷിതമാണ്.",
    "ജാഗ്രത പാലിക്കുക. മിതമായ തിരമാലകൾ ഉണ്ട്.",
    "അപകടകരമായ കടൽ അവസ്ഥ. കടലിൽ പോകരുത്.",
    "അടിയന്തര എസ്ഒഎസ് സന്ദേശം സജീവമാക്കി.",
    "അന്താരാഷ്ട്ര അതിർത്തി ലംഘന മുന്നറിയിപ്പ്! ഉടൻ 180 ഡിഗ്രി തിരിയുക.",
    "ഉയർന്ന മത്സ്യസാധ്യതയുള്ള മേഖല കണ്ടെത്തി.",
    "സുരക്ഷിതമായ യാത്രാ മാർഗ്ഗം തയ്യാറാക്കിയിട്ടുണ്ട്."
  ],
  bn: [
    "নমস্কার! ব্লু অরবিট সামুদ্রিক সহকারীতে স্বাগতম।",
    "সমুদ্রের অবস্থা: সমুদ্রে যাওয়া নিরাপদ।",
    "সতর্কতা অবলম্বন করুন। মাঝারি ঢেউ রয়েছে।",
    "বিপজ্জনক সমুদ্র অবস্থা। সমুদ্রে যাবেন না।",
    "জরুরী এসওএস সংকেত সক্রিয় করা হয়েছে।",
    "আন্তর্জাতিক জলসীমা লঙ্ঘন সতর্কতা! অবিলম্বে ১৮০ ডিগ্রি ঘুরুন।",
    "নিকটবর্তী সম্ভাব্য মাছ ধরার অঞ্চল শনাক্ত করা হয়েছে।",
    "নিরাপদ নেভিগেশন রুট তৈরি করা হয়েছে।"
  ],
  gu: [
    "નમસ્તે! બ્લુ ઓર્બિટ દરિયાઈ સહાયકમાં આપનું સ્વાગત છે.",
    "દરિયાઈ સ્થિતિ: દરિયામાં જવું સુરક્ષિત છે.",
    "સાવધાની રાખો. મધ્યમ મોજાં છે.",
    "જોખમી દરિયાઈ સ્થિતિ. દરિયામાં ન જવું.",
    "ઇમરજન્સી એસઓએસ એલર્ટ સક્રિય કરવામાં આવ્યું છે.",
    "આંતરરાષ્ટ્રીય સરહદ ઉલ્લંઘન ચેતવણી! તરત જ ૧૮૦ ડિગ્રી પાછા ફરો.",
    "નજીકનો મચ્છીમારી સંભવિત વિસ્તાર શોધાયો.",
    "સુરક્ષિત નેવિગેશન માર્ગ तैयार કરવામાં આવ્યો છે."
  ],
  mr: [
    "नमस्कार! ब्लू ऑर्बिट सागरी सहाय्यकामध्ये आपले स्वागत आहे.",
    "समुद्राची स्थिती: समुद्रात जाणे सुरक्षित आहे.",
    "सावधगिरी बाळगा. मध्यम लाटा आहेत.",
    "धोकादायक समुद्राची स्थिती. समुद्रात जाऊ नका.",
    "आपत्कालीन एसओएस अलर्ट सक्रिय करण्यात आला आहे.",
    "आंतरराष्ट्रीय सागरी सीमा उल्लंघन इशारा! त्वरित १८० अंश मागे वळा.",
    "जवळचे उच्च उत्पादन मासेमारी क्षेत्र आढळले.",
    "सुरक्षित नेव्हिगेशन मार्ग तयार केला गेला आहे."
  ],
  kn: [
    "ನಮಸ್ಕಾರ! ಬ್ಲೂ ಆರ್ಬಿಟ್ ಸಮುದ್ರ ಸಹಾಯಕಕ್ಕೆ ಸ್ವಾಗತ.",
    "ಸಮುದ್ರ ಸ್ಥಿತಿ: ಸಮುದ್ರಕ್ಕೆ ಹೋಗುವುದು ಸುರಕ್ಷಿತವಾಗಿದೆ.",
    "ಎಚ್ಚರಿಕೆ ವಹಿಸಿ. ಮಧ್ಯಮ ಅಲೆಗಳಿವೆ.",
    "ಅಪಾಯಕಾರಿ ಸಮುದ್ರ ಸ್ಥಿತಿ. ಸಮುದ್ರಕ್ಕೆ ಹೋಗಬೇಡಿ.",
    "ತುರ್ತು ಎಸ್ಒಎಸ್ ಸಂಕೇತ ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ. ಕರಾವಳಿ ರಕ್ಷಣಾ ಪಡೆ 1554 ಗೆ ಎಚ್ಚರಿಕೆ ನೀಡಲಾಗಿದೆ.",
    "ಅಂತರರಾಷ್ಟ್ರೀಯ ಗಡಿ ಉಲ್ಲಂಘನೆ ಎಚ್ಚರಿಕೆ! ಕೂಡಲೇ 180 ಡಿಗ್ರಿ ತಿರುಗಿ.",
    "ಸಮೀಪದಲ್ಲಿ ಉತ್ತಮ ಮೀನುಗಾರಿಕಾ ವಲಯ ಪತ್ತೆಯಾಗಿದೆ.",
    "ಸುರಕ್ಷಿತ ಸಂಚರಣೆ ಮಾರ್ಗವನ್ನು ರೂಪಿಸಲಾಗಿದೆ."
  ],
  kok: [
    "नमस्कार! ब्लू ऑर्बिट सामुद्रिक सहाय्यकांत तुमचें स्वागत.",
    "समुद्राची स्थिती: समुद्रांत वचप सुरक्षित आसा.",
    "सावध रावात. मध्यम लाटो आसात.",
    "धोकादायक समुद्र स्थिती. समुद्रांत जावं नाका.",
    "आपत्कालीन एसओएस सतर्कता सक्रीय केल्या. कोस्ट गार्ड 1554 क कळीत केलां.",
    "आंतरराष्ट्रीय सीमा उल्लंघन इशारा! तुर्त 180 डिग्री बदला.",
    "लागींच उत्तम मासळी वाठार सोदल्लां.",
    "सुरक्षित नेव्हिगेशन मार्ग तयार केला."
  ],
  or: [
    "ନମସ୍କାର! ବ୍ଲୁ ଅର୍ବିଟ୍ ସାମୁଦ୍ରିକ ସହାୟକକୁ ସ୍ୱାଗତ।",
    "ସମୁଦ୍ର ସ୍ଥିତି: ସମୁଦ୍ରକୁ ଯାଇବା ସୁରକ୍ଷିତ ଅଛି।",
    "ସାବଧାନ ରୁହନ୍ତୁ। ମଧ୍ୟମ ଉଚ୍ଚତାର ତରଙ୍ଗ ଅଛି।",
    "ବିପଦଜନକ ସାମୁଦ୍ରିକ ସ୍ଥିତି। ସମୁଦ୍ରକୁ ଯାଅନ୍ତୁ ନାହିଁ।",
    "ଜରୁରୀକାଳୀନ ଏସଓଏସ୍ ସୂଚନା ସକ୍ରିୟ। କୋଷ୍ଟ ଗାର୍ଡ 1554କୁ ସୂଚିତ କରାଯାଇଛି।",
    "ଆନ୍ତର୍ଜାତିକ ସୀମା ଉଲ୍ଲଙ୍ଘନ ଚେତାବନୀ! ତୁରନ୍ତ 180 ଡିଗ୍ରୀ ଘୁରନ୍ତୁ।",
    "ନିକଟରେ ଉଚ୍ଚ ମତ୍ସ୍ୟ ସମ୍ଭାବନା ଅଞ୍ଚଳ ଚିହ୍ନଟ ହୋଇଛି।",
    "ସୁରକ୍ଷିତ ନାଭିଗେସନ୍ ମାର୍ଗ ପ୍ରସ୍ତୁତ କରାଯାଇଛି।"
  ],
  tcy: [
    "ನಮಸ್ಕಾರ! ಬ್ಲೂ ಆರ್ಬಿಟ್ ಸಮುದ್ರ ಸಹಾಯಕ್‌ಗ್ ಸ್ವಾಗತ.",
    "ಸಮುದ್ರದ ಸ್ಥಿತಿ: ಸಮುದ್ರಗ್ ಪೋಪುನ ಸುರಕ್ಷಿತ.",
    "ಎಚ್ಚರಿಕೆಡ್ ಇಪ್ಪುಲೆ. ಮಧ್ಯಮ ಅಲೆಲು ಉಂಡು.",
    "ಅಪಾಯಕಾರಿ ಸಮುದ್ರ ಸ್ಥಿತಿ. ಸಮುದ್ರಗ್ ಪೋವಡ್.",
    "ತುರ್ತು ಎಸ್ಒಎಸ್ ಸಂಕೇತ ಸಕ್ರಿಯ ಮಲ್ತೆರ್.",
    "ಅಂತರರಾಷ್ಟ್ರೀಯ ಗಡಿ ಉಲ್ಲಂಘನೆ ಎಚ್ಚರಿಕೆ! ದ೾ಟ್ ದೀಪುನಂದೆ 180 ಡಿಗ್ರಿ ತಿರುಗಾಲೆ.",
    "ಲಾಗಾಯಿ ಒಳ್ಳೆದ ಮೀನುಗಾರಿಕಾ ವಲಯ ಪತ್ತೆ ಆಂಡ್.",
    "ಸುರಕ್ಷಿತ ಪ್ರಯಾಣ ಮಾರ್ಗ ತಯಾರ್ ಮಲ್ತೆರ್."
  ],
  kfr: [
    "નમસ્તે! બ્લુ ઓર્બિટ દરિયાઈ મદદગારમાં તમારું સ્વાગત.",
    "દરિયાની સ્થિતિ: દરિયામાં વેંજણું સલામત આય.",
    "ધ્યાન રખજા. મધ્યમ મોજાં આય.",
    "ખતરાવારો દરિયાઈ સ્થિતિ. દરિયામાં ન વેંજો.",
    "ઇમરજન્સી એસઓએસ સંકેત સક્રિય કરેલ આય.",
    "આંતરરાષ્ટ્રીય સીમા ઉલ્લંઘન ચેતવણી! તરત જ 180 ડિગ્રી પાછા ફરો.",
    "નેડે સારો મચ્છીમારી વિસ્તાર મળ્યો આય.",
    "સલામત નેવિગેશન રસ્તો તૈયાર કરેલ આય."
  ]
};


/**
 * 1-Click Pre-Caches all Regional Language Audio Packs into browser CacheStorage
 */
export async function preloadAllRegionalAudioPacks(
  onProgress?: (progressPercent: number, currentLangName: string) => void
): Promise<boolean> {
  if (typeof window === 'undefined' || !('caches' in window)) return false;


  try {
    const cache = await caches.open(AUDIO_CACHE_NAME);
    const languages = Object.entries(CORE_MARINE_AUDIO_PACK);
    let totalItems = 0;
    languages.forEach(([_, phrases]) => { totalItems += phrases.length; });


    let completed = 0;
    const apiBase = getApiBase();


    for (const [code, phrases] of languages) {
      const langName = SUPPORTED_LANGUAGES[code]?.name || code;
      for (const phrase of phrases) {
        const encoded = encodeURIComponent(phrase);
        const serverTtsUrl = `${apiBase}/api/tts?text=${encoded}&lang=${code}`;


        try {
          const match = await cache.match(serverTtsUrl);
          if (!match) {
            const res = await fetch(serverTtsUrl);
            if (res.ok) {
              await cache.put(serverTtsUrl, res);
            }
          }
        } catch (e) {
          // Continue caching remaining phrases
        }


        completed++;
        if (onProgress) {
          const pct = Math.round((completed / totalItems) * 100);
          onProgress(pct, langName);
        }
      }
    }


    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('blue_orbit_audio_cached', 'true');
    }
    return true;
  } catch (err) {
    console.warn('[Audio Preload Error]', err);
    return false;
  }
}


/**
 * Check if the offline audio cache has already been preloaded
 */
export function isAudioCachePreloaded(): boolean {
  if (typeof localStorage === 'undefined') return false;
  return localStorage.getItem('blue_orbit_audio_cached') === 'true';
}


/**
 * Fallback to streaming high-fidelity audio chunks
 */
function fallbackToAudioStream(
  cleaned: string,
  prefix: string,
  onStart?: () => void,
  onEnd?: () => void,
  onError?: (e: any) => void
): HTMLAudioElement | null {
  try {
    const chunks = splitIntoAudioChunks(cleaned, 180);
    audioQueue = [...chunks];


    if (onStart) onStart();
    playNextAudioChunk(prefix, onEnd, onError);
    return activeAudio;
  } catch (err) {
    console.warn('[TTS Streaming Init Error]', err);
    if (onError) onError(err);
    if (onEnd) onEnd();
    return null;
  }
}


/**
 * Speaks text in the specified language.
 * Uses local SpeechSynthesis if a genuine native regional voice is present on the OS,
 * or immediately streams crystal clear native vernacular audio through the backend TTS engine.
 */
export function speakText(
  text: string,
  langCode: string = 'en',
  onStart?: () => void,
  onEnd?: () => void,
  onError?: (e: any) => void
): SpeechSynthesisUtterance | HTMLAudioElement | null {
  stopSpeech();
  const cleaned = cleanTextForSpeech(text);
  if (!cleaned) {
    if (onEnd) onEnd();
    return null;
  }


  const bcp47 = getBcp47LangTag(langCode);
  const prefix = langCode.toLowerCase().trim().split('-')[0];
  const bestVoice = getBestVoiceForLanguage(langCode);


  // 1. If English or if a genuine matching native voice is installed in OS
  if (bestVoice && (prefix === 'en' || bestVoice.lang.toLowerCase().replace('_', '-').startsWith(prefix))) {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }


        const utterance = new SpeechSynthesisUtterance(cleaned);
        utterance.lang = bcp47;
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.voice = bestVoice;
        activeUtterance = utterance;


        if (onStart) utterance.onstart = onStart;
        utterance.onend = () => {
          activeUtterance = null;
          if (onEnd) onEnd();
        };
        utterance.onerror = (e) => {
          console.warn('[SpeechSynthesis Error, fallback to high-fidelity stream]', e);
          activeUtterance = null;
          fallbackToAudioStream(cleaned, prefix, onStart, onEnd, onError);
        };


        window.speechSynthesis.speak(utterance);
        return utterance;
      } catch (e) {
        console.warn('[SpeechSynthesis speak error]', e);
      }
    }
  }


  // 2. High-Fidelity Audio Streaming for Vernacular Languages
  return fallbackToAudioStream(cleaned, prefix, onStart, onEnd, onError);
}


/**
 * Stops any active speech synthesis or streaming audio
 */
export function stopSpeech() {
  audioQueue = [];
  isAudioPlaying = false;
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
    activeAudio = null;
  }
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    activeUtterance = null;
  }
}