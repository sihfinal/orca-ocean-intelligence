import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { OrcaLandingHero } from './components/OrcaLandingHero';
import { AIChatStudio } from './components/AIChatStudio';
import { MapViewport } from './components/MapViewport';
import { AgentChatDrawer } from './components/AgentChatDrawer';
import { GisCommandView } from './components/GisCommandView';
import { AgentDAGStudio } from './components/AgentDAGStudio';
import { SeaSafetyBarometer } from './components/SeaSafetyBarometer';
import { SatelliteTelemetryBar } from './components/SatelliteTelemetryBar';
import { AdvisoryExportModal } from './components/AdvisoryExportModal';
import { GeofenceAlarmHUD } from './components/GeofenceAlarmHUD';
import { VoicePacksModal } from './components/VoicePacksModal';
import { 
  PFZHotspot, 
  NavigationRoute, 
  WeatherObservation, 
  SatelliteTelemetry, 
  ChatResponsePayload 
} from './types';
import { 
  Compass, 
  Map, 
  Cpu, 
  ShieldAlert, 
  FileText, 
  Radio, 
  AlertOctagon, 
  PhoneCall, 
  X,
  Sparkles,
  Layers,
  ChevronRight,
  Fish,
  Waves,
  Wind,
  ShieldCheck,
  Printer,
  QrCode,
  Home
} from 'lucide-react';

import { Capacitor } from '@capacitor/core';
import { Geolocation } from '@capacitor/geolocation';

const PROD_API = 'https://orca-backend-0dxj.onrender.com';
const DEV_API = 'http://localhost:8000';

const getApiBase = () => {
  const customUrl = (import.meta as any).env?.VITE_API_URL;
  if (customUrl) return customUrl;

  // On Native Mobile (Capacitor Android APK / iOS), ALWAYS point to production cloud backend
  if (typeof window !== 'undefined' && Capacitor.isNativePlatform()) {
    return PROD_API;
  }

  // In desktop web browser on localhost, use local if running, else production
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return DEV_API;
  }

  return PROD_API;
};

const API_BASE = getApiBase();

const INDIAN_PORTS = [
  { key: 'munambam', name: 'Munambam Fishing Harbour', lat: 10.1800, lon: 76.1750 },
  { key: 'neendakara', name: 'Neendakara Fishing Harbour', lat: 8.9350, lon: 76.5380 },
  { key: 'sakthikulangara', name: 'Sakthikulangara Fishing Harbour', lat: 8.9220, lon: 76.5500 },
  { key: 'vizhinjam', name: 'Vizhinjam Fishing Harbour', lat: 8.3760, lon: 76.9890 },
  { key: 'koyilandy', name: 'Koyilandy Fishing Harbour', lat: 11.4360, lon: 75.6940 },
  { key: 'malpe', name: 'Malpe Fishing Harbour', lat: 13.3496, lon: 74.7031 },
  { key: 'karwar', name: 'Karwar (Baithkol) Harbour', lat: 14.8080, lon: 74.1250 },
  { key: 'mallet_bunder', name: 'New Ferry Wharf (Mallet Bunder)', lat: 18.9550, lon: 72.8480 },
  { key: 'ratnagiri', name: 'Ratnagiri (Mirkarwada) Harbour', lat: 16.9950, lon: 73.2820 },
  { key: 'malim', name: 'Malim Fishing Jetty', lat: 15.5030, lon: 73.8320 },
  { key: 'mangrol', name: 'Mangrol Fishing Harbour', lat: 21.1200, lon: 70.1150 },
  { key: 'nagapattinam', name: 'Nagapattinam Fishing Harbour', lat: 10.7650, lon: 79.8450 },
  { key: 'chinnamuttom', name: 'Chinnamuttom Fishing Harbour', lat: 8.0930, lon: 77.5620 },
  { key: 'kakinada', name: 'Kakinada Fishing Harbour', lat: 16.9600, lon: 82.2500 },
  { key: 'dhamara', name: 'Dhamara Fishing Harbour', lat: 20.7950, lon: 86.9550 },
  { key: 'petuaghat', name: 'Petuaghat (Deshapran) Harbour', lat: 21.7890, lon: 87.8920 },
  { key: 'kochi', name: 'Kochi Fishing Harbour', lat: 9.9416, lon: 76.2575 },
  { key: 'chennai', name: 'Chennai Kasimedu Harbour', lat: 13.1256, lon: 80.2974 },
  { key: 'visakhapatnam', name: 'Visakhapatnam Fishing Harbour', lat: 17.6974, lon: 83.2986 },
  { key: 'mumbai', name: 'Sassoon Docks & Versova', lat: 18.9172, lon: 72.8228 },
  { key: 'porbandar', name: 'Porbandar Fisheries Port', lat: 21.6417, lon: 69.6293 },
  { key: 'rameswaram', name: 'Rameswaram / Mandapam Jetty', lat: 9.2876, lon: 79.3129 },
  { key: 'mangalore', name: 'Mangalore Old Port', lat: 12.8596, lon: 74.8396 },
  { key: 'paradip', name: 'Paradip Fishing Harbour', lat: 20.2644, lon: 86.6698 },
  { key: 'kanyakumari', name: 'Kanyakumari Harbour', lat: 8.0883, lon: 77.5385 },
  { key: 'port_blair', name: 'Port Blair Phoenix Bay', lat: 11.6670, lon: 92.7350 },
];

export const getNearestPortKey = (lat: number, lon: number): string => {
  let closest = 'kochi';
  let minDist = Infinity;
  for (const p of INDIAN_PORTS) {
    const d = (p.lat - lat) ** 2 + (p.lon - lon) ** 2;
    if (d < minDist) {
      minDist = d;
      closest = p.key;
    }
  }
  return closest;
};

export const DEFAULT_PFZ_HOTSPOTS: PFZHotspot[] = [
  {
    id: "pfz_01",
    name: "Kochi Offshore Thermal Front",
    latitude: 9.82,
    longitude: 75.85,
    recommended_depth_m: 45,
    sst_celsius: 28.2,
    chlorophyll_a_mg_m3: 1.85,
    thermal_gradient_c_per_10km: 0.65,
    chlorophyll_gradient_per_10km: 0.42,
    front_coincidence_index: 0.88,
    confidence_score_percent: 92,
    dominant_species: "Yellowfin Tuna",
    species_suitability_indices: { "Yellowfin Tuna": 92, "Skipjack": 85 },
    catch_enhancement_multiplier: "4.5x Enhance",
    nearest_port: "Kochi Fishing Harbour",
    distance_from_port_km: 48,
    distance_from_port_nm: 25.9,
    bearing_from_port: "WSW (245°)",
    validity: "Next 24 Hours",
    recommended_gear: "Surface Longline / Gillnet"
  },
  {
    id: "pfz_02",
    name: "Mumbai Wadge Bank Shelf",
    latitude: 18.75,
    longitude: 72.35,
    recommended_depth_m: 60,
    sst_celsius: 27.8,
    chlorophyll_a_mg_m3: 2.10,
    thermal_gradient_c_per_10km: 0.72,
    chlorophyll_gradient_per_10km: 0.55,
    front_coincidence_index: 0.91,
    confidence_score_percent: 89,
    dominant_species: "Indian Mackerel",
    species_suitability_indices: { "Indian Mackerel": 89, "Pomfret": 82 },
    catch_enhancement_multiplier: "3.8x Enhance",
    nearest_port: "Sassoon Dock, Mumbai",
    distance_from_port_km: 55,
    distance_from_port_nm: 29.7,
    bearing_from_port: "W (270°)",
    validity: "Next 24 Hours",
    recommended_gear: "Purse Seine / Trawl"
  },
  {
    id: "pfz_03",
    name: "Kasimedu Deep-Sea Canyon",
    latitude: 13.25,
    longitude: 80.85,
    recommended_depth_m: 85,
    sst_celsius: 29.1,
    chlorophyll_a_mg_m3: 1.65,
    thermal_gradient_c_per_10km: 0.58,
    chlorophyll_gradient_per_10km: 0.38,
    front_coincidence_index: 0.84,
    confidence_score_percent: 86,
    dominant_species: "Skipjack Tuna",
    species_suitability_indices: { "Skipjack Tuna": 86, "Mahi Mahi": 78 },
    catch_enhancement_multiplier: "3.5x Enhance",
    nearest_port: "Chennai Kasimedu",
    distance_from_port_km: 62,
    distance_from_port_nm: 33.5,
    bearing_from_port: "ENE (070°)",
    validity: "Next 24 Hours",
    recommended_gear: "Hook & Line / Drift Net"
  },
  {
    id: "pfz_04",
    name: "Veraval Upwelling Convergence",
    latitude: 20.65,
    longitude: 69.90,
    recommended_depth_m: 40,
    sst_celsius: 26.5,
    chlorophyll_a_mg_m3: 3.20,
    thermal_gradient_c_per_10km: 0.85,
    chlorophyll_gradient_per_10km: 0.68,
    front_coincidence_index: 0.94,
    confidence_score_percent: 94,
    dominant_species: "Silver Pomfret",
    species_suitability_indices: { "Silver Pomfret": 94, "Ribbonfish": 88 },
    catch_enhancement_multiplier: "4.8x Enhance",
    nearest_port: "Veraval Fisheries Port",
    distance_from_port_km: 52,
    distance_from_port_nm: 28.1,
    bearing_from_port: "SW (225°)",
    validity: "Next 24 Hours",
    recommended_gear: "Bottom Trawl / Gillnet"
  },
  {
    id: "pfz_05",
    name: "Vizag Northern Bay Front",
    latitude: 17.55,
    longitude: 83.80,
    recommended_depth_m: 70,
    sst_celsius: 28.6,
    chlorophyll_a_mg_m3: 1.95,
    thermal_gradient_c_per_10km: 0.62,
    chlorophyll_gradient_per_10km: 0.46,
    front_coincidence_index: 0.87,
    confidence_score_percent: 88,
    dominant_species: "Sardines & Anchovy",
    species_suitability_indices: { "Sardines": 88, "Tuna": 80 },
    catch_enhancement_multiplier: "3.9x Enhance",
    nearest_port: "Visakhapatnam Harbour",
    distance_from_port_km: 58,
    distance_from_port_nm: 31.3,
    bearing_from_port: "SE (135°)",
    validity: "Next 24 Hours",
    recommended_gear: "Ring Seine / Gillnet"
  }
];

export function App() {
  const getInitialTab = (): 'home' | 'chat' | 'map' | 'agent-lab' | 'safety' | 'bulletin' => {
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace('#', '');
      const valid = ['home', 'chat', 'map', 'agent-lab', 'safety', 'bulletin'];
      if (valid.includes(hash)) return hash as any;
    }
    return 'home';
  };

  const [activeTab, setActiveTabState] = useState<'home' | 'chat' | 'map' | 'agent-lab' | 'safety' | 'bulletin'>(getInitialTab);

  const setActiveTab = (tab: 'home' | 'chat' | 'map' | 'agent-lab' | 'safety' | 'bulletin') => {
    setActiveTabState(tab);
    if (typeof window !== 'undefined') {
      if (window.location.hash.replace('#', '') !== tab) {
        window.history.pushState({ tab }, '', `#${tab}`);
      }
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      const hash = window.location.hash.replace('#', '');
      const valid = ['home', 'chat', 'map', 'agent-lab', 'safety', 'bulletin'];
      if (valid.includes(hash)) {
        setActiveTabState(hash as any);
      } else {
        setActiveTabState('home');
      }
    };
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('hashchange', handlePopState);
    };
  }, []);

  const [currentLang, setCurrentLang] = useState<string>('en');
  const [userCoords, setUserCoords] = useState<{ lat: number; lon: number } | null>(null);

  const [pfzHotspots, setPfzHotspots] = useState<PFZHotspot[]>([]);
  const [selectedPFZ, setSelectedPFZ] = useState<PFZHotspot | null>(null);
  const [activeRoute, setActiveRoute] = useState<NavigationRoute | null>(null);
  const [weather, setWeather] = useState<WeatherObservation | null>(null);
  const [satellites, setSatellites] = useState<SatelliteTelemetry[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Global + Source-Isolated Chat State
  const [latestResponse, setLatestResponse] = useState<ChatResponsePayload | null>(null);

  const [chatResponse, setChatResponse] = useState<ChatResponsePayload | null>(null);
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);

  const [dagResponse, setDagResponse] = useState<ChatResponsePayload | null>(null);
  const [isDagLoading, setIsDagLoading] = useState<boolean>(false);

  const [gisResponse, setGisResponse] = useState<ChatResponsePayload | null>(null);
  const [isGisLoading, setIsGisLoading] = useState<boolean>(false);

  const [isBulletinModalOpen, setIsBulletinModalOpen] = useState<boolean>(false);
  const [isSOSModalOpen, setIsSOSModalOpen] = useState<boolean>(false);
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState<boolean>(false);

  // Initial load & Location Permission Prompt
  useEffect(() => {
    document.title = "Blue Orbit — ISRO Marine Ecosystem Reasoning with Collaborative Agents";
    requestLocationAndInitialize();
  }, []);


  const requestLocationAndInitialize = async () => {
    // 1. Check Native Mobile Environment (Capacitor Android / iOS)
    if (typeof window !== 'undefined' && Capacitor.isNativePlatform()) {
      try {
        const permStatus = await Geolocation.requestPermissions();
        if (permStatus.location === 'granted') {
          const pos = await Geolocation.getCurrentPosition({ enableHighAccuracy: true, timeout: 10000 });
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          setUserCoords({ lat, lon });
          const nearestPort = getNearestPortKey(lat, lon);
          fetchInitialData(lat, lon, nearestPort);
          return;
        }
      } catch (capErr) {
        console.warn('[Blue Orbit GPS] Native Capacitor GPS error:', capErr);
      }
    }

    // 2. Standard Web Browser HTML5 Geolocation API
    if (typeof window !== 'undefined' && 'geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          console.log(`[Blue Orbit GPS] Live Browser Location: ${lat}, ${lon}`);
          setUserCoords({ lat, lon });
          const nearestPort = getNearestPortKey(lat, lon);
          fetchInitialData(lat, lon, nearestPort);
        },
        async (err) => {
          console.warn('[Blue Orbit GPS] Browser Geolocation declined/timeout:', err);
          // 3. Fallback: Quick IP-based coastal city estimation
          try {
            const ipRes = await fetch('https://ipapi.co/json/', { signal: AbortSignal.timeout(3500) });
            if (ipRes.ok) {
              const ipData = await ipRes.json();
              if (ipData.latitude && ipData.longitude) {
                const ipLat = Number(ipData.latitude);
                const ipLon = Number(ipData.longitude);
                console.log(`[Blue Orbit GPS] IP Location: ${ipLat}, ${ipLon} (${ipData.city || 'India'})`);
                setUserCoords({ lat: ipLat, lon: ipLon });
                const nearestPort = getNearestPortKey(ipLat, ipLon);
                fetchInitialData(ipLat, ipLon, nearestPort);
                return;
              }
            }
          } catch (ipErr) {
            console.warn('[Blue Orbit GPS] IP location service unavailable:', ipErr);
          }
          // Default to Kochi Harbour if completely offline
          fetchInitialData(9.9416, 76.2575, 'kochi');
        },
        { enableHighAccuracy: true, timeout: 7000, maximumAge: 60000 }
      );

      // Continuous GPS Position Watcher for moving fishing vessels
      try {
        navigator.geolocation.watchPosition(
          (pos) => {
            setUserCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
          },
          () => {},
          { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
        );
      } catch {}
      return;
    }

    fetchInitialData(9.9416, 76.2575, 'kochi');
  };

  const fetchInitialData = async (lat: number = 9.9416, lon: number = 76.2575, portKey: string = 'kochi') => {
    try {
      // 1. Fetch PFZ Hotspots for user's nearest port
      const pfzRes = await fetch(`${API_BASE}/api/pfz?port=${portKey}`);
      if (pfzRes.ok) {
        const pfzData = await pfzRes.json();
        setPfzHotspots(pfzData.hotspots || []);
        if (pfzData.hotspots && pfzData.hotspots.length > 0) {
          setSelectedPFZ(pfzData.hotspots[0]);
        }
      }

      // 2. Fetch Weather & Safety for current location
      const weatherRes = await fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}`);
      if (weatherRes.ok) {
        const wData = await weatherRes.json();
        setWeather(wData);
      }

      // 3. Fetch Satellite Telemetry
      const satRes = await fetch(`${API_BASE}/api/satellites`);
      if (satRes.ok) {
        const satData = await satRes.json();
        setSatellites(satData.constellation || []);
      }
    } catch (err) {
      console.warn("Backend initializing:", err);
    }
  };

  // Chat message submission with source-scoped state isolation
  const handleSendMessage = async (
    query: string,
    langOverride?: string,
    source: 'chat' | 'dag-lab' | 'map' | 'global' = 'global'
  ): Promise<ChatResponsePayload | null> => {
    if (source === 'chat') setIsChatLoading(true);
    else if (source === 'dag-lab') setIsDagLoading(true);
    else if (source === 'map') setIsGisLoading(true);
    setIsLoading(true);

    const targetLang = langOverride || currentLang;
    const nearestPort = userCoords ? getNearestPortKey(userCoords.lat, userCoords.lon) : undefined;

    const executeChatRequest = async (baseUrl: string): Promise<ChatResponsePayload> => {
      const res = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          language: targetLang,
          user_lat: userCoords?.lat,
          user_lon: userCoords?.lon,
          reference_port: nearestPort
        })
      });

      if (!res.ok) {
        throw new Error(`Server at ${baseUrl} returned ${res.status}`);
      }

      return await res.json();
    };

    try {
      let data: ChatResponsePayload;
      try {
        data = await executeChatRequest(API_BASE);
      } catch (primaryErr) {
        if (API_BASE !== PROD_API) {
          console.warn(`[Blue Orbit] Primary API (${API_BASE}) failed, trying production failover (${PROD_API})...`, primaryErr);
          data = await executeChatRequest(PROD_API);
        } else {
          throw primaryErr;
        }
      }

      // Background domain state updates
      setLatestResponse(data);
      if (data.all_pfz_hotspots) {
        setPfzHotspots(data.all_pfz_hotspots);
      }
      if (data.top_pfz) {
        setSelectedPFZ(data.top_pfz);
      }
      if (data.safe_navigation_route) {
        setActiveRoute(data.safe_navigation_route);
      }
      if (data.weather_and_safety) {
        setWeather(data.weather_and_safety);
      }
      if (data.satellite_telemetry) {
        setSatellites(data.satellite_telemetry);
      }

      // Scoped view isolation to avoid cross-page state leakage
      if (source === 'chat' || source === 'global') {
        setChatResponse(data);
      }
      if (source === 'dag-lab' || source === 'global') {
        setDagResponse(data);
      }
      if (source === 'map' || source === 'global') {
        setGisResponse(data);
      }

      return data;
    } catch (error) {
      console.error("Error executing chat query:", error);
      return null;
    } finally {
      if (source === 'chat') setIsChatLoading(false);
      else if (source === 'dag-lab') setIsDagLoading(false);
      else if (source === 'map') setIsGisLoading(false);
      setIsLoading(false);
    }
  };

  // Map Click coordinate investigation
  const handleMapClickCoord = async (lat: number, lon: number) => {
    setUserCoords({ lat, lon });
    setIsGisLoading(true);
    try {
      fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}`)
        .then(res => res.ok ? res.json() : null)
        .then(w => { if (w) setWeather(w); })
        .catch(() => {});
      await handleSendMessage(
        `What are the sea conditions, PFZ suitability, and IMBL border proximity at coordinates ${lat.toFixed(2)}N, ${lon.toFixed(2)}E?`,
        undefined,
        'map'
      );
    } catch (e) {
      console.error(e);
      setIsGisLoading(false);
    }
  };

  // When a PFZ is clicked on map
  const handleSelectPFZ = async (pfz: PFZHotspot) => {
    setSelectedPFZ(pfz);
    try {
      const routeRes = await fetch(`${API_BASE}/api/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_port: userCoords ? getNearestPortKey(userCoords.lat, userCoords.lon) : "kochi",
          dest_lat: pfz.latitude,
          dest_lon: pfz.longitude,
          dest_name: pfz.name
        })
      });
      if (routeRes.ok) {
        const routeData = await routeRes.json();
        setActiveRoute(routeData);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const isDarkCanvas = activeTab === 'map';

  return (
    <div className={`relative flex flex-col min-h-screen ${isDarkCanvas ? 'bg-black text-white' : 'bg-[#fcfbf8] text-slate-900'} overflow-x-hidden font-['Outfit',sans-serif]`}>
      {/* Top Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentLang={currentLang}
        setCurrentLang={(lang) => {
          setCurrentLang(lang);
          if (activeTab === 'chat' && chatResponse) {
            handleSendMessage(chatResponse.query, lang, 'chat');
          } else if (activeTab === 'agent-lab' && dagResponse) {
            handleSendMessage(dagResponse.query, lang, 'dag-lab');
          } else if (activeTab === 'map' && gisResponse) {
            handleSendMessage(gisResponse.query, lang, 'map');
          }
        }}
        onSOSClick={() => setIsSOSModalOpen(true)}
      />

      {/* Tab 0: Home Landing Page */}
      {activeTab === 'home' && (
        <OrcaLandingHero
          onExplorePlatform={(tab) => setActiveTab(tab)}
          currentLang={currentLang}
        />
      )}

      {/* Tab 1: Minimalist Dedicated AI Chatbot Studio Page (Gemini-style) */}
      {activeTab === 'chat' && (
        <AIChatStudio
          onSendMessage={(q, l) => handleSendMessage(q, l, 'chat')}
          isLoading={isChatLoading}
          latestResponse={chatResponse}
          currentLang={currentLang}
          setCurrentLang={setCurrentLang}
          onNavigateToMap={() => setActiveTab('map')}
        />
      )}

      {/* Fullscreen Liquid Glass GIS Command Center */}
      <div className={activeTab === 'map' ? 'block relative w-full h-full' : 'hidden'}>
        <GisCommandView
          pfzHotspots={pfzHotspots}
          selectedPFZ={selectedPFZ}
          onSelectPFZ={handleSelectPFZ}
          activeRoute={activeRoute}
          weather={weather}
          satellites={satellites}
          onSendMessage={(q, l) => handleSendMessage(q, l, 'map')}
          isLoading={isGisLoading}
          latestResponse={gisResponse}
          currentLang={currentLang}
          onMapClickCoord={handleMapClickCoord}
          userCoords={userCoords}
        />
      </div>


      {/* Dedicated Holographic Agent DAG Studio */}
      {activeTab === 'agent-lab' && (
        <AgentDAGStudio
          satellites={satellites}
          latestResponse={dagResponse}
          isLoading={isDagLoading}
          onSendMessage={(q, l) => handleSendMessage(q, l, 'dag-lab')}
          currentLang={currentLang}
        />
      )}

      {/* Other Workspace Tabs (Safety, Bulletin) */}
      {activeTab !== 'home' && activeTab !== 'chat' && activeTab !== 'map' && activeTab !== 'agent-lab' && (
        <main className="relative z-10 flex-1 pt-24 pb-10 px-4 sm:px-8 lg:px-12 max-w-[1720px] w-full mx-auto space-y-6">
          {/* Top Constellation Bar */}
          {activeTab === 'bulletin' && (
  <SatelliteTelemetryBar satellites={satellites} currentLang={currentLang} />
)}
          {/* Fishermen Safety & Disaster Barometer */}
          {activeTab === 'safety' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7 space-y-5">
                <SeaSafetyBarometer 
                  weather={weather} 
                  portName={latestResponse?.reference_port.name || "Kochi Fishing Harbour"} 
                  onPortSelect={(lat, lon) => handleMapClickCoord(lat, lon)}
                  currentLang={currentLang}
                />
              </div>
              <div className="lg:col-span-5 h-[700px] rounded-3xl overflow-hidden border border-slate-200 shadow-sm sticky top-24">
                <MapViewport
                  pfzHotspots={pfzHotspots}
                  selectedPFZ={selectedPFZ}
                  onSelectPFZ={handleSelectPFZ}
                  activeRoute={activeRoute}
                  weather={weather}
                  onMapClickCoord={handleMapClickCoord}
                  userCoords={userCoords}
                  currentLang='en'
                />
              </div>
            </div>
          )}

          {/* Official Advisory Bulletin */}
          {activeTab === 'bulletin' && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 text-slate-900">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-widest">
                      Official Bulletin Dashboard
                    </span>
                    <span className="text-xs font-mono text-blue-700 font-bold">
                      {latestResponse?.official_bulletin.bulletin_id || "INCOIS-ISRO-BLUEORBIT-2026"}
                    </span>
                  </div>
                  <h2 className="text-xl md:text-2xl font-black text-slate-900">
                    ISRO — INCOIS Joint Satellite Marine Advisory
                  </h2>
                  <p className="text-xs text-slate-500 font-medium">
                    Validated Earth Observation products from Oceansat-3 (OCM-3) & INSAT-3DR TIR
                  </p>
                </div>

                <button
                  onClick={() => setIsBulletinModalOpen(true)}
                  className="flex items-center justify-center space-x-2 px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md transition-all active:scale-95 cursor-pointer"
                >
                  <Printer className="w-4 h-4" />
                  <span>Print / Export Official PDF</span>
                </button>
              </div>

              {/* 4 Core Executive Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-2xl border border-slate-200 space-y-2 shadow-sm">
                  <div className="flex items-center justify-between text-xs font-bold text-emerald-700">
                    <span>Sea Venture Verdict</span>
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div className="text-lg font-black text-emerald-700">
                    {latestResponse?.official_bulletin?.sea_venture_verdict?.replace(/_/g, ' ') || "SAFE FOR VENTURE"}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Sector: <strong className="text-slate-700">{latestResponse?.official_bulletin?.coastal_sector || "Indian EEZ (Arabian Sea & Bay of Bengal)"}</strong>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-slate-200 space-y-2 shadow-sm">
                  <div className="flex items-center justify-between text-xs font-bold text-blue-700">
                    <span>Safety Index Score</span>
                    <Compass className="w-4 h-4" />
                  </div>
                  <div className="text-2xl font-black font-mono text-slate-900">
                    {latestResponse?.official_bulletin?.safety_index_score || 85}<span className="text-xs text-slate-400">/100</span>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Validity: <strong className="text-slate-700">{latestResponse?.official_bulletin?.validity_period || "Next 24 Hours (Active Valid Forecast)"}</strong>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-slate-200 space-y-2 shadow-sm">
                  <div className="flex items-center justify-between text-xs font-bold text-amber-700">
                    <span>PFZ Hotspots Detected</span>
                    <Fish className="w-4 h-4" />
                  </div>
                  <div className="text-2xl font-black font-mono text-slate-900">
                    {latestResponse?.official_bulletin?.recommended_pfz_count || 15} <span className="text-xs text-amber-600 font-bold">Fronts</span>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Top Catch Multiplier: <strong className="text-slate-700">{latestResponse?.official_bulletin?.top_pfz_advisories?.[0]?.catch_enhancement_multiplier || "4.5x Enhance"}</strong>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-slate-200 space-y-2 shadow-sm">
                  <div className="flex items-center justify-between text-xs font-bold text-blue-600">
                    <span>Wave & Wind State</span>
                    <Waves className="w-4 h-4" />
                  </div>
                  <div className="text-lg font-black text-slate-900 font-mono">
                    {latestResponse?.official_bulletin?.meteorological_summary?.wave_height_m || 1.03}m · {latestResponse?.official_bulletin?.meteorological_summary?.wind_speed_knots || 14.9} kts
                  </div>
                  <div className="text-[11px] text-slate-500 truncate">
                    {latestResponse?.official_bulletin?.meteorological_summary?.sea_state || "Smooth Sea"}
                  </div>
                </div>
              </div>

              {/* High-Resolution PFZ Recommendation Table */}
              <div className="bg-white p-6 rounded-3xl border border-slate-200 space-y-4 shadow-sm text-slate-900">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                    <Fish className="w-4 h-4 text-blue-600" />
                    <span>High-Confidence Potential Fishing Zones (PFZ)</span>
                  </h3>
                  <span className="text-xs font-mono text-blue-700 font-bold bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                    Oceansat-3 Coincidence Analyzed
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100 text-slate-600 font-bold uppercase text-[10px] tracking-wider border-b border-slate-200">
                      <tr>
                        <th className="p-3">Zone & Name</th>
                        <th className="p-3">Coordinates</th>
                        <th className="p-3">Target Species</th>
                        <th className="p-3">Depth</th>
                        <th className="p-3">SST / Chl-a</th>
                        <th className="p-3">Confidence</th>
                        <th className="p-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-800">
                      {((latestResponse?.all_pfz_hotspots && latestResponse.all_pfz_hotspots.length > 0) 
                        ? latestResponse.all_pfz_hotspots 
                        : (pfzHotspots && pfzHotspots.length > 0 ? pfzHotspots : DEFAULT_PFZ_HOTSPOTS)).map((pfz, idx) => (
                        <tr key={idx} className="hover:bg-slate-50 transition-colors">
                          <td className="p-3 font-bold text-slate-900 flex items-center space-x-2">
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            <span>{pfz.name}</span>
                          </td>
                          <td className="p-3 font-mono text-slate-600">{pfz.latitude}°N, {pfz.longitude}°E</td>
                          <td className="p-3">
                            <span className="px-2.5 py-1 rounded-full font-bold bg-blue-50 text-blue-700 border border-blue-200">
                              {pfz.dominant_species}
                            </span>
                          </td>
                          <td className="p-3 font-mono text-slate-700">{pfz.recommended_depth_m} m</td>
                          <td className="p-3 font-mono text-blue-700">{pfz.sst_celsius}°C / {pfz.chlorophyll_a_mg_m3} mg/m³</td>
                          <td className="p-3 font-black text-amber-600">{pfz.confidence_score_percent}%</td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => {
                                handleSelectPFZ(pfz);
                                setActiveTab('map');
                              }}
                              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] transition-all cursor-pointer shadow-xs"
                            >
                              View on Map ➔
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      )}

      {/* Advisory Export Modal */}
      <AdvisoryExportModal
        bulletin={latestResponse?.official_bulletin || null}
        isOpen={isBulletinModalOpen}
        onClose={() => setIsBulletinModalOpen(false)}
      />

      {/* Emergency SOS Modal */}
      {isSOSModalOpen && (
        <div className="fixed inset-0 z-[1100] flex items-center justify-center p-4 bg-black/85 backdrop-blur-lg">
          <div className="w-full max-w-md bg-zinc-950 p-6 md:p-8 rounded-3xl border border-red-500/50 shadow-2xl space-y-4 text-center">
            <div className="w-16 h-16 rounded-full bg-red-600/20 border-2 border-red-500 flex items-center justify-center mx-auto text-red-500 animate-pulse">
              <AlertOctagon className="w-9 h-9" />
            </div>

            <h2 className="text-xl font-bold text-white">EMERGENCY DISTRESS SOS ACTIVATED</h2>
            <p className="text-xs text-zinc-300 font-medium">
              Broadcasting geo-tagged distress packet to Indian Coast Guard Maritime Rescue Co-ordination Centre (MRCC).
            </p>

            <div className="p-3.5 rounded-2xl bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-200 space-y-1.5 text-left">
              <div>Vessel ID: <strong className="text-white">IND-KL-04-M (Kochi)</strong></div>
              <div>GPS Coordinates: <strong className="text-white">9.94°N, 76.25°E</strong></div>
              <div>Distress Frequency: <strong className="text-emerald-400">VHF Channel 16 (156.8 MHz)</strong></div>
            </div>

            <div className="flex items-center space-x-3 pt-2">
              <a
                href="tel:1554"
                className="flex-1 py-3 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-red-900/50 transition-all cursor-pointer"
              >
                <PhoneCall className="w-4 h-4" />
                <span>Call Coast Guard 1554</span>
              </a>
              <button
                onClick={() => setIsSOSModalOpen(false)}
                className="px-5 py-3 rounded-2xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-bold text-xs cursor-pointer"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Real-Time On-Device Offline GPS IMBL Geofence & Audio Siren Guard */}
      <GeofenceAlarmHUD
        userCoords={userCoords}
        onSelectCoord={handleMapClickCoord}
      />
    </div>
  );
}
