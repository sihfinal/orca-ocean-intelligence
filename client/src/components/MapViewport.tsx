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
  Anchor
} from 'lucide-react';
import { PFZHotspot, NavigationRoute, WeatherObservation } from '../types';
import { INDIAN_EEZ_BOUNDARY } from '../utils/indiaBoundary';
import { t } from '../utils/translations';

const INDIAN_PORTS = [
  { id: 'munambam', name: 'Munambam Harbour', lat: 10.1800, lon: 76.1750, state: 'Kerala' },
  { id: 'neendakara', name: 'Neendakara Harbour', lat: 8.9350, lon: 76.5380, state: 'Kerala' },
  { id: 'sakthikulangara', name: 'Sakthikulangara Harbour', lat: 8.9220, lon: 76.5500, state: 'Kerala' },
  { id: 'vizhinjam', name: 'Vizhinjam Harbour', lat: 8.3760, lon: 76.9890, state: 'Kerala' },
  { id: 'koyilandy', name: 'Koyilandy Harbour', lat: 11.4360, lon: 75.6940, state: 'Kerala' },
  { id: 'malpe', name: 'Malpe Harbour', lat: 13.3496, lon: 74.7031, state: 'Karnataka' },
  { id: 'karwar', name: 'Karwar Harbour', lat: 14.8080, lon: 74.1250, state: 'Karnataka' },
  { id: 'mallet_bunder', name: 'New Ferry Wharf (Mallet Bunder)', lat: 18.9550, lon: 72.8480, state: 'Maharashtra' },
  { id: 'ratnagiri', name: 'Ratnagiri Harbour', lat: 16.9950, lon: 73.2820, state: 'Maharashtra' },
  { id: 'malim', name: 'Malim Jetty', lat: 15.5030, lon: 73.8320, state: 'Goa' },
  { id: 'mangrol', name: 'Mangrol Harbour', lat: 21.1200, lon: 70.1150, state: 'Gujarat' },
  { id: 'nagapattinam', name: 'Nagapattinam Harbour', lat: 10.7650, lon: 79.8450, state: 'Tamil Nadu' },
  { id: 'chinnamuttom', name: 'Chinnamuttom Harbour', lat: 8.0930, lon: 77.5620, state: 'Tamil Nadu' },
  { id: 'kakinada', name: 'Kakinada Harbour', lat: 16.9600, lon: 82.2500, state: 'Andhra Pradesh' },
  { id: 'dhamara', name: 'Dhamara Harbour', lat: 20.7950, lon: 86.9550, state: 'Odisha' },
  { id: 'petuaghat', name: 'Petuaghat Harbour', lat: 21.7890, lon: 87.8920, state: 'West Bengal' },
  { id: 'kochi', name: 'Kochi Harbour', lat: 9.9416, lon: 76.2575, state: 'Kerala' },
  { id: 'chennai', name: 'Chennai Kasimedu', lat: 13.1256, lon: 80.2974, state: 'Tamil Nadu' },
  { id: 'visakhapatnam', name: 'Vizag Harbour', lat: 17.6974, lon: 83.2986, state: 'Andhra Pradesh' },
  { id: 'mumbai', name: 'Sassoon Docks', lat: 18.9172, lon: 72.8228, state: 'Maharashtra' },
  { id: 'porbandar', name: 'Porbandar Port', lat: 21.6417, lon: 69.6293, state: 'Gujarat' },
  { id: 'rameswaram', name: 'Rameswaram Jetty', lat: 9.2876, lon: 79.3129, state: 'Tamil Nadu' },
  { id: 'mangalore', name: 'Mangalore Port', lat: 12.8596, lon: 74.8396, state: 'Karnataka' },
  { id: 'paradip', name: 'Paradip Port', lat: 20.2644, lon: 86.6698, state: 'Odisha' },
  { id: 'kanyakumari', name: 'Kanyakumari', lat: 8.0883, lon: 77.5385, state: 'Tamil Nadu' },
  { id: 'port_blair', name: 'Port Blair', lat: 11.6643, lon: 92.7305, state: 'Andaman & Nicobar' }
];

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
  const [showIMBL, setShowIMBL] = useState(true);
  const [showMPA, setShowMPA] = useState(true);
  const [showCyclone, setShowCyclone] = useState(true);
  const [showPorts, setShowPorts] = useState(true);

  // 2-Stage Multi-Modal Navigation State (Land Road + Sea Nautical)
  const [selectedTargetPort, setSelectedTargetPort] = useState<{ id: string; name: string; lat: number; lon: number; state: string } | null>(null);
  const [landRouteWaypoints, setLandRouteWaypoints] = useState<[number, number][]>([]);
  const [carProgress, setCarProgress] = useState(0);
  const [seaRouteWaypoints, setSeaRouteWaypoints] = useState<[number, number][]>([]);
  const [boatProgress, setBoatProgress] = useState(0);

  // Layer groups refs
  const pfzLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const eezLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const imblLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const mpaLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const portsLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const routeLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const landRouteLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const cycloneLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const userLocationGroup = useRef<L.LayerGroup>(L.layerGroup());
  const vesselMarkerRef = useRef<L.Marker | null>(null);

  // Helper: Find Nearest Coastal Harbour to a Coordinate
  const findNearestHarbour = (lat: number, lon: number) => {
    let minDistance = Infinity;
    let nearest = INDIAN_PORTS[0];

    INDIAN_PORTS.forEach((port) => {
      const dLat = (port.lat - lat) * (Math.PI / 180);
      const dLon = (port.lon - lon) * (Math.PI / 180);
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat * (Math.PI / 180)) * Math.cos(port.lat * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      const d = 6371 * c; // Earth radius in km

      if (d < minDistance) {
        minDistance = d;
        nearest = port;
      }
    });

    return nearest;
  };

  // Compute 2-Stage Navigation Route (Road 🚗 + Sea 🚢)
  const planTwoStageRoute = async (port: { id: string; name: string; lat: number; lon: number; state: string }, targetPFZOverride?: PFZHotspot) => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.closePopup();
    }
    const originLat = userCoords?.lat ?? 9.9312;
    const originLon = userCoords?.lon ?? 76.2673;

    setSelectedTargetPort(port);
    try {
      localStorage.setItem('orca_last_selected_port_id', port.id);
    } catch {}

    // Clear previous route layers completely
    landRouteLayerGroup.current.clearLayers();
    routeLayerGroup.current.clearLayers();

    // 1. Fetch Stage 1 OSRM Road Route from User Location to Harbour
    let waypoints: [number, number][] = [
      [originLat, originLon],
      [(originLat + port.lat) / 2, (originLon + port.lon) / 2],
      [port.lat, port.lon]
    ];

    try {
      const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${originLon},${originLat};${port.lon},${port.lat}?overview=full&geometries=geojson`;
      const res = await fetch(osrmUrl);
      if (res.ok) {
        const data = await res.json();
        if (data.routes && data.routes.length > 0 && data.routes[0].geometry?.coordinates) {
          waypoints = data.routes[0].geometry.coordinates.map((c: [number, number]) => [c[1], c[0]]);
        }
      }
    } catch (err) {
      console.warn('OSRM road route fetch fallback:', err);
    }

    setLandRouteWaypoints(waypoints);
    setCarProgress(0);

    // 2. Target PFZ offshore from Harbour
    const targetPFZ = targetPFZOverride
      || pfzHotspots.find(p => p.nearest_port?.toLowerCase().includes(port.name.toLowerCase()) || p.nearest_port?.toLowerCase().includes(port.id))
      || pfzHotspots[0];

    if (targetPFZ) {
      const seaPoints: [number, number][] = [
        [port.lat, port.lon],
        [(port.lat * 0.5 + targetPFZ.latitude * 0.5), (port.lon * 0.5 + targetPFZ.longitude * 0.5)],
        [targetPFZ.latitude, targetPFZ.longitude]
      ];
      setSeaRouteWaypoints(seaPoints);
      setBoatProgress(0);
      onSelectPFZ(targetPFZ);
    }
  };

  // Expose planTwoStageRoute handlers to window for Leaflet popup action buttons
  useEffect(() => {
    (window as any).planTwoStageRoute = (portId: string) => {
      const port = INDIAN_PORTS.find(p => p.id === portId);
      if (port) {
        planTwoStageRoute(port);
      }
    };

    (window as any).planTwoStageRouteForPFZ = (pfzId: string) => {
      const pfz = pfzHotspots.find(p => p.id === pfzId);
      if (pfz) {
        const nearestPort = findNearestHarbour(pfz.latitude, pfz.longitude);
        planTwoStageRoute(nearestPort, pfz);
      }
    };
  }, [userCoords, pfzHotspots, selectedPFZ]);

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

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ISRO Oceansat-3',
      maxZoom: 19
    }).addTo(map);

    L.control.zoom({ position: 'topright' }).addTo(map);

    // Add all layer groups to map
    pfzLayerGroup.current.addTo(map);
    eezLayerGroup.current.addTo(map);
    imblLayerGroup.current.addTo(map);
    mpaLayerGroup.current.addTo(map);
    portsLayerGroup.current.addTo(map);
    landRouteLayerGroup.current.addTo(map);
    routeLayerGroup.current.addTo(map);
    cycloneLayerGroup.current.addTo(map);
    userLocationGroup.current.addTo(map);

    map.on('click', (e: L.LeafletMouseEvent) => {
      onMapClickCoord(e.latlng.lat, e.latlng.lng);
    });

    mapInstanceRef.current = map;

    const timer1 = setTimeout(() => {
      map.invalidateSize();
    }, 150);

    const timer2 = setTimeout(() => {
      map.invalidateSize();
    }, 500);

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

  // Render Coastal Ports & Harbours Layer
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    portsLayerGroup.current.clearLayers();

    if (showPorts) {
      INDIAN_PORTS.forEach(port => {
        const portIcon = L.divIcon({
          className: 'port-marker',
          html: `
            <div class="flex items-center justify-center w-5 h-5 rounded-full bg-zinc-900 text-white text-[10px] border border-white shadow-sm hover:scale-125 transition-transform cursor-pointer">
              ⚓
            </div>
          `,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });

        const m = L.marker([port.lat, port.lon], { icon: portIcon })
          .on('click', () => onMapClickCoord(port.lat, port.lon))
          .bindPopup(`
            <div class="p-2 font-sans text-slate-900 min-w-[220px] space-y-1.5">
              <div class="flex items-center justify-between border-b pb-1 font-bold">
                <span class="text-xs text-blue-700">${port.name}</span>
                <span class="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">${port.state}</span>
              </div>
              <div class="text-[11px] text-slate-600">
                <div>Coordinates: ${port.lat.toFixed(4)}°N, ${port.lon.toFixed(4)}°E</div>
                <div>Harbour Base: <span class="text-emerald-700 font-semibold">Active Coastal Base</span></div>
              </div>
              <button onclick="window.planTwoStageRoute('${port.id}')" class="w-full mt-2 py-1.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold text-[11px] flex items-center justify-center space-x-1 cursor-pointer shadow-sm transition-all">
                <span>🚗 ➔ 🚢 Plan Route from My Location</span>
              </button>
            </div>
          `);
        portsLayerGroup.current.addLayer(m);
      });
    }
  }, [showPorts]);

  // Render Cyclone Layer
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    cycloneLayerGroup.current.clearLayers();

    if (showCyclone) {
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
              <button onclick="window.planTwoStageRouteForPFZ && window.planTwoStageRouteForPFZ('${pfz.id}')" class="w-full mt-2 py-1.5 text-center text-[10px] font-bold rounded bg-blue-600 hover:bg-blue-700 text-white border border-blue-600 cursor-pointer shadow-sm transition-all active:scale-95">
                Plan Multi-Modal Safe Route 🚗➔🚢
              </button>
            </div>
          `);

        pfzLayerGroup.current.addLayer(marker);
      });
    }
  }, [showPFZ, pfzHotspots, selectedPFZ]);

  // Vehicle progress intervals for Stage 1 (Car) & Stage 2 (Boat)
  useEffect(() => {
    if (landRouteWaypoints.length <= 1) return;
    const interval = setInterval(() => {
      setCarProgress(prev => (prev >= landRouteWaypoints.length - 1 ? 0 : prev + 1));
    }, 400);
    return () => clearInterval(interval);
  }, [landRouteWaypoints]);

  useEffect(() => {
    if (seaRouteWaypoints.length <= 1) return;
    const interval = setInterval(() => {
      setBoatProgress(prev => (prev >= seaRouteWaypoints.length - 1 ? 0 : prev + 1));
    }, 600);
    return () => clearInterval(interval);
  }, [seaRouteWaypoints]);

  // Render Stage 1 (Land Road Polyline + Car Animation 🚗)
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    landRouteLayerGroup.current.clearLayers();

    if (landRouteWaypoints.length > 1) {
      const landPolyline = L.polyline(landRouteWaypoints, {
        color: '#2563EB',
        weight: 5,
        opacity: 0.95
      }).bindPopup(`
        <div class="p-1 font-sans text-slate-900">
          <div class="text-xs font-bold text-blue-700">🚗 Stage 1: Driving Road Route</div>
          <div class="text-[11px] text-slate-600">Driving from Live GPS Position to ${selectedTargetPort?.name || 'Harbour'}</div>
        </div>
      `);
      landRouteLayerGroup.current.addLayer(landPolyline);

      const startMarker = L.circleMarker(landRouteWaypoints[0], {
        radius: 7,
        color: '#FFF',
        fillColor: '#2563EB',
        fillOpacity: 1,
        weight: 2
      }).bindPopup('<div class="text-xs font-bold text-blue-800 font-sans">Origin: Live GPS Position</div>');
      landRouteLayerGroup.current.addLayer(startMarker);

      const carPos = landRouteWaypoints[Math.min(carProgress, landRouteWaypoints.length - 1)];
      const carIcon = L.divIcon({
        className: 'car-icon',
        html: `
          <div class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white border-2 border-white shadow-xl text-base">
            🚗
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const carMarker = L.marker(carPos, { icon: carIcon })
        .bindPopup(`
          <div class="p-1 font-sans text-slate-900">
            <div class="text-xs font-bold text-blue-700">🚗 Road Driving Vehicle</div>
            <div class="text-[11px] text-slate-600">Transit En Route to ${selectedTargetPort?.name || 'Harbour'}</div>
          </div>
        `);

      landRouteLayerGroup.current.addLayer(carMarker);
    }
  }, [landRouteWaypoints, carProgress, selectedTargetPort]);

  // Render Stage 2 (Sea Ocean Polyline + Boat Animation 🚢)
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    routeLayerGroup.current.clearLayers();

    if (seaRouteWaypoints.length > 1) {
      const seaPolyline = L.polyline(seaRouteWaypoints, {
        color: '#0284C7',
        weight: 5,
        opacity: 0.95,
        dashArray: '8, 6'
      }).bindPopup(`
        <div class="p-1 font-sans text-slate-900">
          <div class="text-xs font-bold text-sky-700">🚢 Stage 2: Maritime Ocean Route</div>
          <div class="text-[11px] text-slate-600">Sailing from ${selectedTargetPort?.name || 'Harbour'} to PFZ Hotspot</div>
        </div>
      `);
      routeLayerGroup.current.addLayer(seaPolyline);

      const destMarker = L.circleMarker(seaRouteWaypoints[seaRouteWaypoints.length - 1], {
        radius: 8,
        color: '#FFF',
        fillColor: '#0284C7',
        fillOpacity: 1,
        weight: 2
      }).bindPopup('<div class="text-xs font-bold text-blue-800 font-sans">Destination: Ocean PFZ Hotspot</div>');
      routeLayerGroup.current.addLayer(destMarker);

      const boatPos = seaRouteWaypoints[Math.min(boatProgress, seaRouteWaypoints.length - 1)];
      const boatIcon = L.divIcon({
        className: 'vessel-icon',
        html: `
          <div class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white border-2 border-white shadow-xl text-base animate-pulse">
            🚢
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const vesselMarker = L.marker(boatPos, { icon: boatIcon })
        .bindPopup(`
          <div class="p-1 font-sans text-slate-900">
            <div class="text-xs font-bold text-blue-700">🛥️ Trawler IND-KL-04-M</div>
            <div class="text-[11px] text-slate-600">En route to selected PFZ Zone</div>
          </div>
        `);

      routeLayerGroup.current.addLayer(vesselMarker);
      vesselMarkerRef.current = vesselMarker;
    }
  }, [seaRouteWaypoints, boatProgress, selectedTargetPort]);

  // Live User GPS Location Beacon Effect
  useEffect(() => {
    userLocationGroup.current.clearLayers();
    if (!userCoords || !mapInstanceRef.current) return;

    const userGpsIcon = L.divIcon({
      className: 'custom-gps-user-beacon',
      html: `
        <div class="relative flex items-center justify-center cursor-pointer">
          <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-blue-500 opacity-75"></span>
          <div class="relative flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white ring-4 ring-blue-300 shadow-xl font-bold text-[10px]">
            📍
          </div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const userMarker = L.marker([userCoords.lat, userCoords.lon], { icon: userGpsIcon, zIndexOffset: 2500 })
      .bindPopup(`
        <div class="p-2 space-y-1 font-sans text-slate-900">
          <div class="text-xs font-bold text-blue-700">📍 Live Vessel / User GPS Location</div>
          <div class="text-[11px] text-slate-600">Lat: ${userCoords.lat.toFixed(4)}°N | Lon: ${userCoords.lon.toFixed(4)}°E</div>
          <div class="text-[10px] text-emerald-700 font-bold">Lock Location Active</div>
        </div>
      `);

    userLocationGroup.current.addLayer(userMarker);
  }, [userCoords]);

  return (
    <div className="relative w-full h-full bg-slate-900 font-['Outfit',sans-serif]">
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Floating Layer Control Overlay */}
      <div className="absolute top-4 left-4 z-[400] bg-white/95 backdrop-blur-md p-3 rounded-2xl border border-slate-200 shadow-lg space-y-2 text-xs font-semibold text-slate-800 max-w-[230px]">
        <div className="flex items-center space-x-1.5 border-b border-slate-200 pb-2 text-slate-900 font-black">
          <Layers className="w-4 h-4 text-blue-600" />
          <span>{t('gis_layers', currentLang)}</span>
        </div>

        <div className="space-y-1">
          <button
            onClick={() => setShowPFZ(!showPFZ)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
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
            onClick={() => setShowPorts(!showPorts)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
              showPorts ? 'bg-blue-50 border-blue-300 text-blue-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'
            }`}
          >
            <span className="flex items-center space-x-1.5">
              <Anchor className="w-3.5 h-3.5 text-blue-600" />
              <span>Coastal Harbours</span>
            </span>
            {showPorts ? <Eye className="w-3 h-3 text-blue-600" /> : <EyeOff className="w-3 h-3" />}
          </button>

          <button
            onClick={() => setShowIMBL(!showIMBL)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
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
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
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
            className={`w-full flex items-center justify-between px-3 py-2 rounded-xl border transition-all cursor-pointer ${
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
      </div>

      {/* Floating Bottom Quick Legend */}
      <div className="absolute bottom-4 left-4 z-[400] bg-white/95 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 text-xs font-semibold flex items-center space-x-4 text-slate-700 shadow-md hidden md:flex">
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span>Potential Fishing Zone</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-zinc-900 text-white flex items-center justify-center text-[8px]">⚓</span>
          <span>Coastal Harbour</span>
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
          <span>2-Stage Safe Route</span>
        </div>
      </div>
    </div>
  );
};
