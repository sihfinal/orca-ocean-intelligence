import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  Layers, 
  Play, 
  RotateCcw,
  Volume2, 
  VolumeX, 
  Mic, 
  MicOff, 
  ArrowUp,
  Compass, 
  Copy, 
  Check,
  ChevronDown,
  ChevronUp,
  Navigation,
  Bell,
  Download,
  Sparkles,
  GitCompare,
  FileCheck2,
  AlertTriangle,
  Info
} from 'lucide-react';
import { 
  PFZHotspot, 
  NavigationRoute, 
  WeatherObservation, 
  SatelliteTelemetry, 
  ChatResponsePayload,
  TemporalSelection,
  OperationalAlert
} from '../types';
import { speakText, stopSpeech } from '../utils/speechUtils';
import { INDIAN_EEZ_BOUNDARY, INDIAN_TERRITORIAL_WATERS_12NM } from '../utils/indiaBoundary';
import { LayerControlPanel, LayerVisibilityState } from './LayerControlPanel';
import { DataLegendBar } from './DataLegendBar';
import { TemporalControlBar } from './TemporalControlBar';
import { PFZDetailDrawer } from './PFZDetailDrawer';
import { DecisionEvidencePanel } from './DecisionEvidencePanel';
import { RouteComparisonModal } from './RouteComparisonModal';
import { OperationalAlertsDrawer } from './OperationalAlertsDrawer';
import { ExportDataModal } from './ExportDataModal';

interface GisCommandViewProps {
  pfzHotspots: PFZHotspot[];
  selectedPFZ: PFZHotspot | null;
  onSelectPFZ: (pfz: PFZHotspot) => void;
  activeRoute: NavigationRoute | null;
  weather: WeatherObservation | null;
  satellites: SatelliteTelemetry[];
  onSendMessage: (query: string, langOverride?: string) => Promise<any>;
  isLoading: boolean;
  latestResponse: ChatResponsePayload | null;
  currentLang: string;
  onMapClickCoord: (lat: number, lon: number) => void;
  userCoords?: { lat: number; lon: number } | null;
}

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

export const GisCommandView: React.FC<GisCommandViewProps> = ({
  pfzHotspots,
  selectedPFZ,
  onSelectPFZ,
  activeRoute,
  weather,
  satellites,
  onSendMessage,
  isLoading,
  latestResponse,
  currentLang = 'en',
  onMapClickCoord,
  userCoords
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Grouped Layer State
  const [layers, setLayers] = useState<LayerVisibilityState>({
    showSST: true,
    showChl: false,
    showWaves: true,
    showFronts: true,
    showPFZ: true,
    showRasterContours: false,
    showEEZ: true,
    showIMBL: true,
    showMPA: true,
    showCyclone: true,
    showPorts: true,
    showRoute: true,
    showAlternates: true
  });

  const toggleLayer = (key: keyof LayerVisibilityState) => {
    setLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Temporal Horizon State
  const [temporal, setTemporal] = useState<TemporalSelection>({
    mode: 'OBSERVATION',
    target_datetime: new Date().toISOString(),
    time_label: 'Now (Observation)'
  });

  // Modals and Drawers
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isDecisionPanelOpen, setIsDecisionPanelOpen] = useState(false);
  const [isRouteComparisonOpen, setIsRouteComparisonOpen] = useState(false);
  const [isAlertsDrawerOpen, setIsAlertsDrawerOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Dynamic Operational Alerts generated from real conditions
  const [alerts, setAlerts] = useState<OperationalAlert[]>([]);

  // Simulation
  const [isSimulatingVessel, setIsSimulatingVessel] = useState(false);
  const [vesselProgress, setVesselProgress] = useState(0);

  // Cursor Coordinates
  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lng: number } | null>(null);

  // Layer Groups
  const pfzCentroidGroup = useRef<L.LayerGroup>(L.layerGroup());
  const pfzPolygonGroup = useRef<L.LayerGroup>(L.layerGroup());
  const eezLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const imblLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const mpaLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const portsLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const routeLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const alternateRouteGroup = useRef<L.LayerGroup>(L.layerGroup());
  const cycloneLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const rasterContourGroup = useRef<L.LayerGroup>(L.layerGroup());
  const sstLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const chlLayerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const clickMarkerGroup = useRef<L.LayerGroup>(L.layerGroup());
  const userLocationGroup = useRef<L.LayerGroup>(L.layerGroup());
  const vesselMarkerRef = useRef<L.Marker | null>(null);


  // Ingest Real Alerts from Backend Response
  useEffect(() => {
    const list: OperationalAlert[] = [];
    const nowIso = new Date().toISOString();

    if (weather) {
      if (weather.significant_wave_height_m >= 4.0) {
        list.push({
          alert_id: 'ALT-WAVE-SURVIVAL',
          type: 'EXTREME_SEA',
          severity: 'CRITICAL',
          title: 'Extreme High-Sea Survival Warning',
          message: `Significant wave height (${weather.significant_wave_height_m}m) exceeds craft survival threshold. Coastal ventures strictly prohibited.`,
          timestamp: nowIso,
          source: 'INCOIS & Open-Meteo Hydrodynamics',
          acknowledged: false
        });
      } else if (weather.significant_wave_height_m >= 2.5) {
        list.push({
          alert_id: 'ALT-WAVE-CAUTION',
          type: 'EXTREME_SEA',
          severity: 'WARNING',
          title: 'Rough Sea Condition Advisory',
          message: `Elevated wave height (${weather.significant_wave_height_m}m) with winds at ${weather.wind_speed_knots} kts. Exercise navigation vigilance.`,
          timestamp: nowIso,
          source: 'INCOIS Ocean State Forecast',
          acknowledged: false
        });
      }
    }

    // Cyclone Alerts
    if (latestResponse?.weather_and_safety?.cyclone_influence?.active_cyclone) {
      list.push({
        alert_id: 'ALT-CYCLONE-BASIN',
        type: 'CYCLONE',
        severity: 'CRITICAL',
        title: `Tropical Cyclone Warning: ${latestResponse.weather_and_safety.cyclone_influence.active_cyclone}`,
        message: `Cyclonic system tracked in basin. Maintain MRCC radio watch on VHF Ch 16.`,
        timestamp: nowIso,
        source: 'GDACS & IMD RSMC New Delhi',
        acknowledged: false
      });
    }

    // Geofence / Restriction Alerts
    if (latestResponse?.geofence_status?.nearest_imbl?.threat_level === 'BUFFER_PROXIMITY_ALERT') {
      list.push({
        alert_id: 'ALT-IMBL-PROXIMITY',
        type: 'IMBL_BREACH',
        severity: 'WARNING',
        title: 'International Maritime Boundary Line Proximity',
        message: `Vessel within 5 NM of ${latestResponse.geofence_status.nearest_imbl.border_name}. Do not cross boundary.`,
        timestamp: nowIso,
        source: 'MEA & UNCLOS Maritime Treaty Database',
        acknowledged: false
      });
    }

    setAlerts(list);
  }, [weather, latestResponse]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: userCoords ? [userCoords.lat, userCoords.lon] : [14.0, 78.5],
      zoom: userCoords ? 8 : 6,
      minZoom: 4,
      maxZoom: 15,
      zoomControl: false,
    });

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap | ISRO Oceansat-3 & INSAT-3DR',
      maxZoom: 19
    }).addTo(map);

    L.control.zoom({ position: 'bottomleft' }).addTo(map);

    // Add layer groups
    rasterContourGroup.current.addTo(map);
    sstLayerGroup.current.addTo(map);
    chlLayerGroup.current.addTo(map);
    pfzPolygonGroup.current.addTo(map);
    eezLayerGroup.current.addTo(map);
    imblLayerGroup.current.addTo(map);
    mpaLayerGroup.current.addTo(map);
    portsLayerGroup.current.addTo(map);
    routeLayerGroup.current.addTo(map);
    alternateRouteGroup.current.addTo(map);
    cycloneLayerGroup.current.addTo(map);
    pfzCentroidGroup.current.addTo(map);
    clickMarkerGroup.current.addTo(map);
    userLocationGroup.current.addTo(map);

    // Map mouse move for cursor coordinate display
    map.on('mousemove', (e: L.LeafletMouseEvent) => {
      setCursorCoords({ lat: e.latlng.lat, lng: e.latlng.lng });
    });

    // Map click handler
    map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;
      clickMarkerGroup.current.clearLayers();
      const clickIcon = L.divIcon({
        className: 'custom-click-pin',
        html: `
          <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
            <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-blue-500 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3.5 w-3.5 bg-blue-600 border-2 border-white shadow-md"></span>
          </div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      const clickMarker = L.marker([lat, lng], { icon: clickIcon });
      clickMarkerGroup.current.addLayer(clickMarker);
      onMapClickCoord(lat, lng);
    });

    mapInstanceRef.current = map;

    setTimeout(() => map.invalidateSize(), 150);
    setTimeout(() => map.invalidateSize(), 500);

    const resizeObserver = new ResizeObserver(() => {
      mapInstanceRef.current?.invalidateSize();
    });
    if (mapContainerRef.current) resizeObserver.observe(mapContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Render EEZ, IMBL, and MPA Layers
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    eezLayerGroup.current.clearLayers();
    if (layers.showEEZ) {
      const eezBorder = L.polyline(INDIAN_EEZ_BOUNDARY, {
        color: '#0284C7',
        weight: 2,
        dashArray: '6, 6',
        opacity: 0.8
      }).bindPopup('<div class="p-1 text-xs font-bold text-sky-800 font-sans">200 NM Indian EEZ Sovereign Boundary</div>');
      eezLayerGroup.current.addLayer(eezBorder);
    }

    imblLayerGroup.current.clearLayers();
    if (layers.showIMBL) {
      const slCoords: [number, number][] = [
        [10.0833, 79.8667], [9.9500, 79.6167], [9.7000, 79.4333],
        [9.3500, 79.3667], [9.1000, 79.2500], [8.8833, 79.0333],
        [8.4000, 78.8333], [7.8333, 78.6000]
      ];
      const slPoly = L.polyline(slCoords, {
        color: '#DC2626',
        weight: 3.5,
        dashArray: '6, 8',
        opacity: 0.95
      }).bindPopup('<div class="p-1 text-xs font-bold text-red-600 font-sans">🛑 India-Sri Lanka IMBL (1974/76 Treaty)</div>');
      imblLayerGroup.current.addLayer(slPoly);
    }

    mpaLayerGroup.current.clearLayers();
    if (layers.showMPA) {
      const gomCircle = L.circle([9.05, 79.15], {
        radius: 25000,
        color: '#D97706',
        fillColor: '#F59E0B',
        fillOpacity: 0.2,
        weight: 2,
        dashArray: '4, 4'
      }).bindPopup('<div class="p-1 text-xs font-bold text-amber-800 font-sans">🛡️ Gulf of Mannar Marine Biosphere Reserve (No Trawling)</div>');
      mpaLayerGroup.current.addLayer(gomCircle);
    }
  }, [layers.showEEZ, layers.showIMBL, layers.showMPA]);

  // Render Ports Layer
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    portsLayerGroup.current.clearLayers();

    if (layers.showPorts) {
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
            <div class="p-1 font-sans text-slate-900">
              <strong class="text-xs text-blue-700 font-bold">${port.name}</strong>
              <div class="text-[10px] text-slate-500">${port.state} • Port Base</div>
            </div>
          `);
        portsLayerGroup.current.addLayer(m);
      });
    }
  }, [layers.showPorts]);

  // Render SST Thermal Field Layer — circles at PFZ positions with temperature-scaled colour
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    sstLayerGroup.current.clearLayers();

    if (layers.showSST && pfzHotspots.length > 0) {
      pfzHotspots.forEach(pfz => {
        // Map SST to a heat colour: cool (26 °C → blue) → warm (31 °C → red)
        const t = Math.max(0, Math.min(1, (pfz.sst_celsius - 26) / 5));
        const r = Math.round(30 + t * 215);
        const g = Math.round(100 - t * 60);
        const b = Math.round(220 - t * 190);
        const colour = `rgb(${r},${g},${b})`;

        const circle = L.circle([pfz.latitude, pfz.longitude], {
          radius: 35000,
          color: colour,
          fillColor: colour,
          fillOpacity: 0.22,
          weight: 1.5,
          opacity: 0.7
        }).bindPopup(
          `<div class="p-1.5 font-sans text-slate-900">` +
          `<div class="text-xs font-bold text-rose-700">🌡️ SST Thermal Reading</div>` +
          `<div class="text-[11px] text-slate-700 mt-0.5"><strong>${pfz.sst_celsius}°C</strong> — ${pfz.name}</div>` +
          `<div class="text-[10px] text-slate-500 mt-0.5">Gradient: ${pfz.thermal_gradient_c_per_10km} °C/10 km</div>` +
          `</div>`
        );
        sstLayerGroup.current.addLayer(circle);
      });
    }
  }, [layers.showSST, pfzHotspots]);

  // Render Chlorophyll-a Biomass Layer — circles at PFZ positions with Chl-scaled colour
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    chlLayerGroup.current.clearLayers();

    if (layers.showChl && pfzHotspots.length > 0) {
      pfzHotspots.forEach(pfz => {
        // Map Chl-a (0.5–3.0 mg/m³) to green intensity
        const t = Math.max(0, Math.min(1, (pfz.chlorophyll_a_mg_m3 - 0.5) / 2.5));
        const r = Math.round(20 + t * 20);
        const g = Math.round(120 + t * 110);
        const b = Math.round(80 - t * 40);
        const colour = `rgb(${r},${g},${b})`;

        const circle = L.circle([pfz.latitude, pfz.longitude], {
          radius: 30000,
          color: colour,
          fillColor: colour,
          fillOpacity: 0.25,
          weight: 1.5,
          opacity: 0.75
        }).bindPopup(
          `<div class="p-1.5 font-sans text-slate-900">` +
          `<div class="text-xs font-bold text-teal-700">🟢 Chlorophyll-a Biomass</div>` +
          `<div class="text-[11px] text-slate-700 mt-0.5"><strong>${pfz.chlorophyll_a_mg_m3} mg/m³</strong> — ${pfz.name}</div>` +
          `<div class="text-[10px] text-slate-500 mt-0.5">Chl gradient: ${pfz.chlorophyll_gradient_per_10km}/10 km</div>` +
          `</div>`
        );
        chlLayerGroup.current.addLayer(circle);
      });
    }
  }, [layers.showChl, pfzHotspots]);

  // Render PFZ Centroids & Spatial Polygons
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    pfzCentroidGroup.current.clearLayers();
    pfzPolygonGroup.current.clearLayers();

    if (layers.showPFZ && pfzHotspots.length > 0) {
      pfzHotspots.forEach(pfz => {
        const isSelected = selectedPFZ?.id === pfz.id;

        // Render synthetic polygon boundary around centroid for realistic spatial extent
        const delta = 0.08;
        const polyCoords: [number, number][] = [
          [pfz.latitude - delta, pfz.longitude - delta * 1.2],
          [pfz.latitude - delta * 0.4, pfz.longitude + delta * 1.4],
          [pfz.latitude + delta, pfz.longitude + delta * 0.8],
          [pfz.latitude + delta * 0.8, pfz.longitude - delta * 1.1]
        ];

        const polygon = L.polygon(polyCoords, {
          color: isSelected ? '#2563EB' : '#059669',
          fillColor: isSelected ? '#3B82F6' : '#10B981',
          fillOpacity: isSelected ? 0.25 : 0.15,
          weight: isSelected ? 2.5 : 1.5,
          dashArray: isSelected ? undefined : '4, 4'
        }).on('click', () => {
          onSelectPFZ(pfz);
          setIsDetailDrawerOpen(true);
        });

        pfzPolygonGroup.current.addLayer(polygon);

        // Centroid Pin
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

        const marker = L.marker([pfz.latitude, pfz.longitude], { icon: customIcon })
          .on('click', () => {
            onSelectPFZ(pfz);
            setIsDetailDrawerOpen(true);
          })
          .bindPopup(`
            <div class="p-2 space-y-1 min-w-[200px] text-slate-900 font-sans">
              <div class="flex items-center justify-between border-b pb-1 font-bold">
                <span class="text-xs text-blue-700">${pfz.name}</span>
                <span class="text-[10px] text-emerald-700 px-1 py-0.5 bg-emerald-50 rounded">${pfz.confidence_score_percent}% PFZ</span>
              </div>
              <div class="text-[11px] text-slate-600 space-y-0.5 pt-1">
                <div>Species: <strong>${pfz.dominant_species}</strong></div>
                <div>SST: <strong>${pfz.sst_celsius}°C</strong> | Chl-a: <strong>${pfz.chlorophyll_a_mg_m3} mg/m³</strong></div>
                <div>Catch Boost: <strong class="text-amber-700">${pfz.catch_enhancement_multiplier}</strong></div>
              </div>
            </div>
          `);

        pfzCentroidGroup.current.addLayer(marker);
      });
    }
  }, [layers.showPFZ, pfzHotspots, selectedPFZ]);

  // Render Navigation Route
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    routeLayerGroup.current.clearLayers();
    alternateRouteGroup.current.clearLayers();

    if (layers.showRoute && activeRoute && activeRoute.waypoints.length > 1) {
      const latlngs: [number, number][] = activeRoute.waypoints.map(w => [w.latitude, w.longitude]);

      // Preferred Plan A Route
      const polyline = L.polyline(latlngs, {
        color: '#0284C7',
        weight: 4.5,
        opacity: 0.9,
        dashArray: '8, 6'
      });
      routeLayerGroup.current.addLayer(polyline);

      // Start Marker
      const startMarker = L.circleMarker(latlngs[0], {
        radius: 7,
        color: '#FFF',
        fillColor: '#059669',
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`<div class="text-xs font-bold text-emerald-800 font-sans">Departure: ${activeRoute.origin.name}</div>`);
      routeLayerGroup.current.addLayer(startMarker);

      // End Marker
      const endMarker = L.circleMarker(latlngs[latlngs.length - 1], {
        radius: 7,
        color: '#FFF',
        fillColor: '#0284C7',
        fillOpacity: 1,
        weight: 2
      }).bindPopup(`<div class="text-xs font-bold text-blue-800 font-sans">Destination: ${activeRoute.destination.name}</div>`);
      routeLayerGroup.current.addLayer(endMarker);

      // Render Alternate Straight-Line Route if enabled
      if (layers.showAlternates) {
        const altPoints: [number, number][] = [
          latlngs[0],
          latlngs[latlngs.length - 1]
        ];
        const altPoly = L.polyline(altPoints, {
          color: '#9333EA',
          weight: 2.5,
          opacity: 0.6,
          dashArray: '4, 4'
        }).bindPopup('<div class="text-xs font-bold text-purple-800 font-sans">Alternative Plan B: Direct Route (Higher Wave Risk)</div>');
        alternateRouteGroup.current.addLayer(altPoly);
      }
    }
  }, [layers.showRoute, layers.showAlternates, activeRoute]);

  // User GPS Beacon
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

    const marker = L.marker([userCoords.lat, userCoords.lon], { icon: userGpsIcon, zIndexOffset: 1500 });
    userLocationGroup.current.addLayer(marker);
    mapInstanceRef.current.flyTo([userCoords.lat, userCoords.lon], 9, { duration: 1.5 });
  }, [userCoords]);

  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden font-['Outfit',sans-serif] select-none bg-slate-100 z-0">
      {/* 1. Fullscreen Map Canvas */}
      <div 
        ref={mapContainerRef} 
        className="absolute inset-0 w-full h-full z-0 cursor-crosshair" 
      />

      {/* 2. Top-Left Grouped Layer Controls */}
      <div className="absolute top-20 left-6 z-20 pointer-events-auto">
        <LayerControlPanel
          layers={layers}
          onToggleLayer={toggleLayer}
          currentLang={currentLang}
        />
      </div>

      {/* 3. Top-Center Temporal Control Bar */}
      <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 pointer-events-auto hidden md:block">
        <TemporalControlBar
          selection={temporal}
          onSelectTemporal={setTemporal}
          currentLang={currentLang}
        />
      </div>

      {/* 4. Top-Right Operational Command Bar */}
      <div className="absolute top-20 right-6 z-20 pointer-events-auto flex items-center space-x-2">
        {/* Decision & Evidence Drawer Trigger */}
        <button
          onClick={() => setIsDecisionPanelOpen(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-md text-xs font-bold text-zinc-900 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer"
          title="Inspect structured decision, confidence & evidence package"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Decision & Evidence</span>
        </button>

        {/* Route Comparison Trigger */}
        {activeRoute && (
          <button
            onClick={() => setIsRouteComparisonOpen(true)}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-md text-xs font-bold text-zinc-900 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer"
            title="Compare A* Route with Alternative Paths"
          >
            <GitCompare className="w-3.5 h-3.5 text-purple-600" />
            <span>Compare Routes</span>
          </button>
        )}

        {/* Operational Alerts Trigger */}
        <button
          onClick={() => setIsAlertsDrawerOpen(true)}
          className="relative p-2 rounded-xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-md text-zinc-800 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer"
          title="Maritime Disaster & Weather Warnings"
        >
          <Bell className="w-4 h-4 text-rose-600" />
          {alerts.filter(a => !a.acknowledged).length > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[9px] font-bold flex items-center justify-center animate-pulse">
              {alerts.filter(a => !a.acknowledged).length}
            </span>
          )}
        </button>

        {/* Export Data Button */}
        <button
          onClick={() => setIsExportModalOpen(true)}
          className="p-2 rounded-xl bg-white/95 backdrop-blur-xl border border-zinc-200/90 shadow-md text-zinc-800 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer"
          title="Export GeoJSON & CSV"
        >
          <Download className="w-4 h-4 text-blue-600" />
        </button>
      </div>

      {/* 5. Bottom-Left Scientific Legends & Ocean Pill */}
      <div className="absolute bottom-6 left-6 z-20 pointer-events-auto flex items-center space-x-3">
        <DataLegendBar weather={weather} currentLang={currentLang} />

        <div className="hidden lg:flex items-center space-x-3 px-3.5 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-zinc-200/80 shadow-sm text-xs text-zinc-700 font-mono">
          <div>Wave: <strong className="text-zinc-900 font-bold">{weather?.significant_wave_height_m || "1.03"}m</strong></div>
          <div className="w-px h-3 bg-zinc-200" />
          <div>Wind: <strong className="text-zinc-900 font-bold">{weather?.wind_speed_knots || "14.9"} kts</strong></div>
          <div className="w-px h-3 bg-zinc-200" />
          <div>Safety: <strong className="text-emerald-700 font-bold">{weather?.safety_index || "74.2"}/100</strong></div>
        </div>
      </div>

      {/* 6. Bottom-Right Cursor Coordinate Display */}
      {cursorCoords && (
        <div className="absolute bottom-6 right-6 z-20 pointer-events-auto px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-zinc-200/80 shadow-sm text-[11px] font-mono text-zinc-600 hidden sm:block">
          <span>Cursor: </span>
          <strong className="text-zinc-900 font-bold">{cursorCoords.lat.toFixed(4)}°N, {cursorCoords.lng.toFixed(4)}°E</strong>
          <span className="text-[10px] text-zinc-400 ml-1.5">(WGS-84)</span>
        </div>
      )}

      {/* 7. Drawers and Modals */}
      {/* PFZ Detail Drawer */}
      {isDetailDrawerOpen && (
        <PFZDetailDrawer
          pfz={selectedPFZ}
          onClose={() => setIsDetailDrawerOpen(false)}
          onComputeRoute={(pfz) => {
            setIsDetailDrawerOpen(false);
            onSelectPFZ(pfz);
          }}
          weather={weather}
          geofence={latestResponse?.geofence_status}
          currentLang={currentLang}
        />
      )}

      {/* Slide-out Decision & Evidence Panel */}
      {isDecisionPanelOpen && (
        <div className="fixed top-14 bottom-0 right-0 z-[1050] w-full max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-200 max-h-[calc(100dvh-3.5rem)]">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="font-bold text-slate-800 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>ORCA Cognitive Decision & Evidence</span>
            </div>
            <button 
              onClick={() => setIsDecisionPanelOpen(false)}
              className="p-1 rounded-full hover:bg-slate-200 text-slate-500 cursor-pointer"
            >
              ✕
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <DecisionEvidencePanel
              decision={latestResponse?.decision}
              evidencePackage={latestResponse?.evidence_package}
              claimValidation={latestResponse?.claim_validation}
              currentLang={currentLang}
              onSelectCandidate={(id) => {
                const found = pfzHotspots.find(p => p.id === id);
                if (found) onSelectPFZ(found);
              }}
            />
          </div>
        </div>
      )}

      {/* Route Comparison Modal */}
      <RouteComparisonModal
        isOpen={isRouteComparisonOpen}
        onClose={() => setIsRouteComparisonOpen(false)}
        activeRoute={activeRoute}
        currentLang={currentLang}
      />

      {/* Operational Alerts Drawer */}
      <OperationalAlertsDrawer
        isOpen={isAlertsDrawerOpen}
        onClose={() => setIsAlertsDrawerOpen(false)}
        alerts={alerts}
        onAcknowledgeAlert={(id) => {
          setAlerts(prev => prev.map(a => a.alert_id === id ? { ...a, acknowledged: true } : a));
        }}
        onAcknowledgeAll={() => {
          setAlerts(prev => prev.map(a => ({ ...a, acknowledged: true })));
        }}
      />

      {/* Export Data Modal */}
      <ExportDataModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        pfzHotspots={pfzHotspots}
        activeRoute={activeRoute}
        decision={latestResponse?.decision}
      />
    </div>
  );
};