import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  Layers, 
  Eye, 
  EyeOff, 
  Navigation, 
  Fish, 
  Wind, 
  ShieldAlert, 
  Play,
  RotateCcw
} from 'lucide-react';
import { PFZHotspot, NavigationRoute, WeatherObservation } from '../types';
import { INDIAN_EEZ_BOUNDARY } from '../utils/indiaBoundary';
import { t } from '../utils/translations';

interface MapViewportProps {
  pfzHotspots: PFZHotspot[];
  selectedPFZ: PFZHotspot | null;
  onSelectPFZ: (pfz: PFZHotspot) => void;
  activeRoute: NavigationRoute | null;
  weather: WeatherObservation | null;
  onMapClickCoord: (lat: number, lon: number) => void;
  userCoords?: { lat: number; lon: number } | null;
  currentLang?: string; 
}

export const MapViewport: React.FC<MapViewportProps> = ({
  pfzHotspots,
  selectedPFZ,
  onSelectPFZ,
  activeRoute,
  weather,
  onMapClickCoord,
  userCoords,
  currentLang = 'en'
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Layer toggles
  const [showPFZ, setShowPFZ] = useState(true);
  const [showEEZ, setShowEEZ] = useState(true);
  const [showSST, setShowSST] = useState(true);
  const [showChl, setShowChl] = useState(false);
  const [showIMBL, setShowIMBL] = useState(true);
  const [showMPA, setShowMPA] = useState(true);
  const [showRoute, setShowRoute] = useState(true);
  const [showCyclone, setShowCyclone] = useState(true);
  const [isSimulatingVessel, setIsSimulatingVessel] = useState(false);
  const [vesselProgress, setVesselProgress] = useState(0);

  // Layer groups refs
  const pfzLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const eezLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const sstLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const chlLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const imblLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const mpaLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const routeLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const cycloneLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const userLocationGroup = useRef<L.LayerGroup>(L.layerGroup());
  const vesselMarkerRef = useRef<L.Marker | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center on Indian Peninsula / Arabian Sea & Bay of Bengal
    const map = L.map(mapContainerRef.current, {
      center: [14.0, 78.5],
      zoom: 6,
      minZoom: 4,
      maxZoom: 14,
      zoomControl: false,
    });

    // High-Resolution OpenStreetMap Tiles (100% Free & No API Key Required)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ISRO Oceansat-3',
      maxZoom: 19
    }).addTo(map);

    // Zoom control in top right
    L.control.zoom({ position: 'topright' }).addTo(map);

    // Add all layer groups to map
    pfzLayerGroup.current.addTo(map);
    eezLayerGroup.current.addTo(map);
    sstLayerGroup.current.addTo(map);
    chlLayerGroup.current.addTo(map);
    imblLayerGroup.current.addTo(map);
    mpaLayerGroup.current.addTo(map);
    routeLayerGroup.current.addTo(map);
    cycloneLayerGroup.current.addTo(map);
    userLocationGroup.current.addTo(map);

    // Map click handler for arbitrary coordinate inspection
    map.on('click', (e: L.LeafletMouseEvent) => {
      onMapClickCoord(e.latlng.lat, e.latlng.lng);
    });

    mapInstanceRef.current = map;

    // Force invalidateSize after mount & layout computation
    const timer1 = setTimeout(() => {
      map.invalidateSize();
    }, 150);

    const timer2 = setTimeout(() => {
      map.invalidateSize();
    }, 500);

    // ResizeObserver to handle any window/tab resizing
    const resizeObserver = new ResizeObserver(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    });

    if (mapContainerRef.current) {
      resizeObserver.observe(mapContainerRef.current);
    }

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      resizeObserver.disconnect();
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Invalidate size whenever tab or active state updates
  useEffect(() => {
    if (mapInstanceRef.current) {
      const t = setTimeout(() => {
        mapInstanceRef.current?.invalidateSize();
      }, 100);
      return () => clearTimeout(t);
    }
  }, [pfzHotspots, activeRoute]);

  // Static Layers (200 NM Indian EEZ, IMBL & MPA)
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // 200 NM Indian Exclusive Economic Zone
    eezLayerGroup.current.clearLayers();
    if (showEEZ) {
      const eezBorder = L.polyline(INDIAN_EEZ_BOUNDARY, {
        color: '#0284C7',
        weight: 2.5,
        dashArray: '8, 6',
        opacity: 0.85
      }).bindPopup(`
        <div class="p-2 text-slate-900 font-['Outfit',sans-serif]">
          <div class="text-xs font-bold text-sky-700">🌊 200 NM Indian Exclusive Economic Zone (EEZ)</div>
          <div class="text-[11px] text-slate-600 mt-1">UNCLOS Sovereign Maritime Exploitation Boundary.</div>
        </div>
      `);
      eezLayerGroup.current.addLayer(eezBorder);
    }

    imblLayerGroup.current.clearLayers();
    mpaLayerGroup.current.clearLayers();

    if (showIMBL) {
      // 1. India - Sri Lanka IMBL
      const srilankaCoords: [number, number][] = [
        [10.0833, 79.8667], [9.9500, 79.6167], [9.7000, 79.4333],
        [9.3500, 79.3667], [9.1000, 79.2500], [8.8833, 79.0333],
        [8.4000, 78.8333], [7.8333, 78.6000]
      ];
      const slPoly = L.polyline(srilankaCoords, {
        color: '#DC2626',
        weight: 3.5,
        dashArray: '6, 8',
        opacity: 0.95
      }).bindPopup(`
        <div class="p-1 text-slate-900">
          <div class="text-xs font-bold text-red-600">🛑 India-Sri Lanka IMBL (1974/76)</div>
          <div class="text-[11px] text-slate-700 mt-1">Strict maritime border. 3 NM warning buffer active.</div>
        </div>
      `);
      imblLayerGroup.current.addLayer(slPoly);

      // 2. India - Pakistan IMBL
      const pakCoords: [number, number][] = [
        [23.5833, 68.1000], [23.4500, 67.8000], [23.2000, 67.4000],
        [22.8000, 66.8000], [22.3000, 66.2000], [21.5000, 65.5000]
      ];
      const pakPoly = L.polyline(pakCoords, {
        color: '#DC2626',
        weight: 3.5,
        dashArray: '6, 8',
        opacity: 0.95
      }).bindPopup(`
        <div class="p-1 text-slate-900">
          <div class="text-xs font-bold text-red-600">🛑 India-Pakistan IMBL (Sir Creek)</div>
          <div class="text-[11px] text-slate-700 mt-1">High-security maritime buffer zone. Zero tolerance.</div>
        </div>
      `);
      imblLayerGroup.current.addLayer(pakPoly);
    }

    if (showMPA) {
      // Gulf of Mannar Marine Biosphere
      const gomCircle = L.circle([9.05, 79.15], {
        radius: 25000,
        color: '#D97706',
        fillColor: '#F59E0B',
        fillOpacity: 0.2,
        weight: 2,
        dashArray: '5, 5'
      }).bindPopup(`
        <div class="p-1 text-slate-900">
          <div class="text-xs font-bold text-amber-700">🛡️ Gulf of Mannar Marine Biosphere</div>
          <div class="text-[11px] text-slate-700 mt-1">Strict No-Trawling Eco Zone. Coral Reef & Dugong Reserve.</div>
        </div>
      `);
      mpaLayerGroup.current.addLayer(gomCircle);

      // Gahirmatha Olive Ridley Sanctuary
      const gmCircle = L.circle([20.72, 87.05], {
        radius: 20000,
        color: '#D97706',
        fillColor: '#F59E0B',
        fillOpacity: 0.2,
        weight: 2,
        dashArray: '5, 5'
      }).bindPopup(`
        <div class="p-1 text-slate-900">
          <div class="text-xs font-bold text-amber-700">🐢 Gahirmatha Marine Sanctuary (Odisha)</div>
          <div class="text-[11px] text-slate-700 mt-1">Seasonal nesting ban in effect (Nov-May).</div>
        </div>
      `);
      mpaLayerGroup.current.addLayer(gmCircle);
    }
  }, [showEEZ, showIMBL, showMPA]);

  // Render Cyclone Layer
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    cycloneLayerGroup.current.clearLayers();

    if (showCyclone) {
      // Cyclone Eye & Danger Radius
      const eyeCircle = L.circle([15.8, 84.6], {
        radius: 180000,
        color: '#DC2626',
        fillColor: '#EF4444',
        fillOpacity: 0.18,
        weight: 2,
        dashArray: '5, 5'
      });

      const eyeCore = L.circleMarker([15.8, 84.6], {
        radius: 8,
        color: '#FFF',
        fillColor: '#DC2626',
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`
        <div class="p-1 text-slate-900">
          <div class="text-xs font-bold text-red-600">🌪️ Cyclone ASNA-II (VSCS)</div>
          <div class="text-[11px] text-slate-700 mt-1">Central Pressure: 982 hPa | Max Winds: 65-80 kts</div>
          <div class="text-[10px] text-red-700 font-semibold mt-1">Danger Radius: 180 km (No Sea Venture)</div>
        </div>
      `);

      cycloneLayerGroup.current.addLayer(eyeCircle);
      cycloneLayerGroup.current.addLayer(eyeCore);
    }
  }, [showCyclone]);

  // Render PFZ Hotspots
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    pfzLayerGroup.current.clearLayers();

    if (showPFZ && pfzHotspots.length > 0) {
      pfzHotspots.forEach((pfz) => {
        const isSelected = selectedPFZ?.id === pfz.id;
        
        // Custom vibrant pin icon for PFZ
        const customIcon = L.divIcon({
          className: 'custom-pfz-pin',
          html: `
            <div class="relative flex items-center justify-center cursor-pointer">
              <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full ${isSelected ? 'bg-blue-500 opacity-80' : 'bg-emerald-500 opacity-50'}"></span>
              <div class="relative flex items-center justify-center w-7 h-7 rounded-full ${isSelected ? 'bg-blue-600 text-white ring-4 ring-blue-300' : 'bg-emerald-600 text-white ring-2 ring-white'} shadow-lg font-bold text-xs transition-transform hover:scale-125">
                🐟
              </div>
            </div>
          `,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        const marker = L.marker([pfz.latitude, pfz.longitude], { icon: customIcon, zIndexOffset: 2000 })
          .on('click', () => onSelectPFZ(pfz))
          .bindPopup(`
            <div class="p-2 space-y-1.5 min-w-[220px] text-slate-900">
              <div class="flex items-center justify-between border-b border-slate-200 pb-1">
                <span class="text-xs font-bold text-blue-700">${pfz.name}</span>
                <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                  ${pfz.confidence_score_percent}% PFZ
                </span>
              </div>
              <div class="text-[11px] text-slate-700">
                <div>🎯 <strong>Species:</strong> <span class="text-emerald-700 font-bold">${pfz.dominant_species}</span></div>
                <div>⚡ <strong>Catch Boost:</strong> <span class="text-amber-700 font-bold">${pfz.catch_enhancement_multiplier}</span></div>
                <div>🌊 <strong>SST:</strong> ${pfz.sst_celsius}°C | <strong>Chl-a:</strong> ${pfz.chlorophyll_a_mg_m3} mg/m³</div>
                <div>⚓ <strong>Depth:</strong> ${pfz.recommended_depth_m}m | <strong>From ${pfz.nearest_port}:</strong> ${pfz.distance_from_port_km} km</div>
              </div>
              <button class="w-full mt-2 py-1 text-center text-[10px] font-bold rounded bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-300 cursor-pointer">
                Plan Navigation Route ➔
              </button>
            </div>
          `);

        pfzLayerGroup.current.addLayer(marker);
      });
    }
  }, [showPFZ, pfzHotspots, selectedPFZ]);

  // Render Navigation Route & Vessel Simulation
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    routeLayerGroup.current.clearLayers();

    if (showRoute && activeRoute && activeRoute.waypoints.length > 1) {
      const latlngs: [number, number][] = activeRoute.waypoints.map(w => [w.latitude, w.longitude]);

      const polyline = L.polyline(latlngs, {
        color: '#0284C7',
        weight: 4.5,
        opacity: 0.9,
        dashArray: '8, 6'
      });

      routeLayerGroup.current.addLayer(polyline);

      // Start & End markers
      const startMarker = L.circleMarker(latlngs[0], {
        radius: 7,
        color: '#FFF',
        fillColor: '#059669',
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`<div class="text-xs font-bold text-emerald-800">Departure: ${activeRoute.origin.name}</div>`);

      const endMarker = L.circleMarker(latlngs[latlngs.length - 1], {
        radius: 7,
        color: '#FFF',
        fillColor: '#0284C7',
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`<div class="text-xs font-bold text-blue-800">Destination: ${activeRoute.destination.name}</div>`);

      routeLayerGroup.current.addLayer(startMarker);
      routeLayerGroup.current.addLayer(endMarker);

      // Simulated moving boat marker
      const currentPos = latlngs[Math.min(vesselProgress, latlngs.length - 1)];
      const boatIcon = L.divIcon({
        className: 'vessel-icon',
        html: `
          <div class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white border-2 border-white shadow-xl animate-pulse">
            🚢
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const vesselMarker = L.marker(currentPos, { icon: boatIcon })
        .bindPopup(`
          <div class="p-1 text-slate-900">
            <div class="text-xs font-bold text-blue-700">🛥️ Trawler IND-KL-04-M</div>
            <div class="text-[11px] text-slate-600">Speed: 9.5 kts | ETA: ${activeRoute.route_metrics.estimated_transit_time_hours} hrs</div>
          </div>
        `);

      routeLayerGroup.current.addLayer(vesselMarker);
      vesselMarkerRef.current = vesselMarker;
    }
  }, [showRoute, activeRoute, vesselProgress]);

  // Live User GPS Location Beacon Effect
  useEffect(() => {
    userLocationGroup.current.clearLayers();
    if (!userCoords || !mapInstanceRef.current) return;

    const userGpsIcon = L.divIcon({
      className: 'custom-gps-user-beacon',
      html: `
        <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
          <span class="absolute w-12 h-12 rounded-full bg-blue-500/25 animate-ping"></span>
          <span class="absolute w-7 h-7 rounded-full bg-blue-500/50 animate-pulse"></span>
          <div class="relative w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow-xl flex items-center justify-center">
            <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
          </div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const marker = L.marker([userCoords.lat, userCoords.lon], { icon: userGpsIcon, zIndexOffset: 1500 })
      .bindPopup(`
        <div class="p-2 text-slate-900 text-xs space-y-1">
          <div class="font-bold text-blue-700 flex items-center space-x-1">
            <span>📍 Your Exact GPS Location</span>
          </div>
          <div class="text-[11px] text-slate-600 font-mono">
            ${userCoords.lat.toFixed(4)}°N, ${userCoords.lon.toFixed(4)}°E
          </div>
          <div class="text-[10px] text-emerald-600 font-bold">
            ✓ Live ISRO Satellite Stream Connected
          </div>
        </div>
      `);

    userLocationGroup.current.addLayer(marker);
  }, [userCoords]);

  // Zoom to selected harbour when selected from Safety Barometer
  useEffect(() => {
    if (weather && weather.latitude && weather.longitude && mapInstanceRef.current) {
      try {
        mapInstanceRef.current.invalidateSize();
        mapInstanceRef.current.flyTo([weather.latitude, weather.longitude], 10, { duration: 1.5 });
      } catch (e) {
        console.warn('[MapViewport] flyTo harbour failed:', e);
      }
    }
  }, [weather?.latitude, weather?.longitude]);

  // Vessel animation ticker
  useEffect(() => {
    if (!isSimulatingVessel || !activeRoute) return;
    const interval = setInterval(() => {
      setVesselProgress(prev => {
        if (prev >= activeRoute.waypoints.length - 1) {
          return 0; // loop
        }
        return prev + 1;
      });
    }, 1200);
    return () => clearInterval(interval);
  }, [isSimulatingVessel, activeRoute]);

  return (
    <div className="relative w-full h-full min-h-[520px] flex-1 overflow-hidden rounded-3xl border border-slate-200 shadow-lg bg-slate-100 flex flex-col">
      {/* Map Canvas */}
      <div 
        ref={mapContainerRef} 
        className="w-full h-full min-h-[520px] flex-1" 
        style={{ width: '100%', height: '100%', minHeight: '520px' }} 
      />

      {/* Floating My Location GPS Button */}
      {userCoords && (
        <button
          onClick={() => {
            if (userCoords && mapInstanceRef.current) {
              mapInstanceRef.current.flyTo([userCoords.lat, userCoords.lon], 10, { duration: 1.2 });
            }
          }}
          className="absolute bottom-6 right-6 z-[400] flex items-center space-x-2 px-3.5 py-2.5 rounded-2xl bg-white/95 backdrop-blur-md border border-slate-200 shadow-xl hover:bg-slate-50 text-xs font-bold text-slate-800 active:scale-95 transition-all cursor-pointer"
          title="Recenter to your GPS location"
        >
          <Navigation className="w-4 h-4 text-blue-600 animate-pulse" />
          <span>{t('my_gps_location', currentLang)}</span>
        </button>
      )}

      {/* Floating Layer Control Panel (Bright Glass) */}
      <div className="absolute top-4 left-4 z-[400] bg-white/95 backdrop-blur-md p-3.5 rounded-2xl border border-slate-200 shadow-xl max-w-xs space-y-2.5 text-xs text-slate-800">
        <div className="flex items-center justify-between font-bold text-slate-900 border-b border-slate-200 pb-2">
          <span className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-blue-600" />
            <span>{t('gis_marine_layers', currentLang)}</span>
          </span>
          <span className="text-[10px] text-blue-600 font-mono bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
            ISRO L3
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            onClick={() => setShowPFZ(!showPFZ)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
              showPFZ ? 'bg-emerald-50 border-emerald-300 text-emerald-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'
            }`}
          >
            <span className="flex items-center space-x-1.5">
              <Fish className="w-3.5 h-3.5 text-emerald-600" />
              <span>{t('pfz_zones', currentLang)}</span>
            </span>
            {showPFZ ? <Eye className="w-3 h-3 text-emerald-600" /> : <EyeOff className="w-3 h-3" />}
          </button>

          <button
            onClick={() => setShowIMBL(!showIMBL)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
              showIMBL ? 'bg-red-50 border-red-300 text-red-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'
            }`}
          >
            <span className="flex items-center space-x-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-red-600" />
              <span>{t('imbl_border', currentLang)}</span>
            </span>
            {showIMBL ? <Eye className="w-3 h-3 text-red-600" /> : <EyeOff className="w-3 h-3" />}
          </button>

          <button
            onClick={() => setShowMPA(!showMPA)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
              showMPA ? 'bg-amber-50 border-amber-300 text-amber-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'
            }`}
          >
            <span className="flex items-center space-x-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
              <span>{t('mpa_reserves', currentLang)}</span>
            </span>
            {showMPA ? <Eye className="w-3 h-3 text-amber-600" /> : <EyeOff className="w-3 h-3" />}
          </button>

          <button
            onClick={() => setShowCyclone(!showCyclone)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
              showCyclone ? 'bg-red-50 border-red-300 text-red-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'
            }`}
          >
            <span className="flex items-center space-x-1.5">
              <Wind className="w-3.5 h-3.5 text-red-600" />
              <span>{t('cyclone_track', currentLang)}</span>
            </span>
            {showCyclone ? <Eye className="w-3 h-3 text-red-600" /> : <EyeOff className="w-3 h-3" />}
          </button>
        </div>

        {/* Route Simulation Trigger */}
        {activeRoute && (
          <div className="pt-2 border-t border-slate-200 flex items-center justify-between">
            <span className="text-[11px] text-slate-600 font-medium">{t('simulate_trawler', currentLang)}</span>
            <div className="flex items-center space-x-1.5">
              <button
                onClick={() => setIsSimulatingVessel(!isSimulatingVessel)}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-bold cursor-pointer transition-all ${
                  isSimulatingVessel ? 'bg-red-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <Play className="w-3 h-3" />
                <span>{isSimulatingVessel ? t('pause_sim', currentLang) : t('start_sim', currentLang)}</span>
              </button>
              <button
                onClick={() => setVesselProgress(0)}
                className="p-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Floating Bottom Quick Legend */}
      <div className="absolute bottom-4 left-4 z-[400] bg-white/95 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 text-xs font-semibold flex items-center space-x-4 text-slate-700 shadow-md hidden md:flex">
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span>Potential Fishing Zone</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-1 bg-red-500 rounded"></span>
          <span>{t('imbl_border', currentLang)}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          <span>Protected Area</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-1 bg-blue-500 rounded"></span>
          <span>Safe Route</span>
        </div>
      </div>
    </div>
  );
};
