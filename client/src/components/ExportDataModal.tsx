import React from 'react';
import { 
  X, 
  Download, 
  FileSpreadsheet, 
  Globe, 
  FileText, 
  Check,
  Share2
} from 'lucide-react';
import { PFZHotspot, NavigationRoute, DecisionObject } from '../types';

interface ExportDataModalProps {
  isOpen: boolean;
  onClose: () => void;
  pfzHotspots: PFZHotspot[];
  activeRoute: NavigationRoute | null;
  decision?: DecisionObject | null;
}

export const ExportDataModal: React.FC<ExportDataModalProps> = ({
  isOpen,
  onClose,
  pfzHotspots,
  activeRoute,
  decision
}) => {
  if (!isOpen) return null;

  // 1. Download GeoJSON FeatureCollection
  const handleExportGeoJSON = () => {
    const features = [];

    // PFZ Points
    pfzHotspots.forEach(pfz => {
      features.push({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [pfz.longitude, pfz.latitude]
        },
        properties: {
          id: pfz.id,
          name: pfz.name,
          confidence_percent: pfz.confidence_score_percent,
          sst_celsius: pfz.sst_celsius,
          chlorophyll_a_mg_m3: pfz.chlorophyll_a_mg_m3,
          species: pfz.dominant_species,
          multiplier: pfz.catch_enhancement_multiplier,
          nearest_port: pfz.nearest_port
        }
      });
    });

    // Navigation Route Polyline
    if (activeRoute && activeRoute.waypoints.length > 1) {
      features.push({
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: activeRoute.waypoints.map(w => [w.longitude, w.latitude])
        },
        properties: {
          name: "A* Least-Cost Safe Navigational Route",
          origin: activeRoute.origin.name,
          destination: activeRoute.destination.name,
          distance_nm: activeRoute.route_metrics.routed_distance_nm,
          eta_hours: activeRoute.route_metrics.estimated_transit_time_hours,
          status: activeRoute.route_metrics.route_status
        }
      });
    }

    const geojson = {
      type: "FeatureCollection",
      metadata: {
        system: "ORCA — Marine Ecosystem Reasoning with Collaborative Agents",
        generated_at: new Date().toISOString(),
        advisory_id: decision?.decision_id || "INCOIS-ISRO-2026"
      },
      features
    };

    const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: "application/geo+json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ORCA_Marine_Spatial_Intelligence_${Date.now()}.geojson`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // 2. Download CSV
  const handleExportCSV = () => {
    const headers = "ID,Name,Latitude,Longitude,ConfidenceScore,SST_Celsius,Chlorophyll_mg_m3,DominantSpecies,CatchMultiplier,NearestPort,DistanceKm\n";
    const rows = pfzHotspots.map(p => 
      `"${p.id}","${p.name}",${p.latitude},${p.longitude},${p.confidence_score_percent},${p.sst_celsius},${p.chlorophyll_a_mg_m3},"${p.dominant_species}","${p.catch_enhancement_multiplier}","${p.nearest_port}",${p.distance_from_port_km || 0}`
    ).join("\n");

    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ORCA_PFZ_Advisories_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-[1100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150 font-['Outfit',sans-serif]">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden text-slate-900 text-xs">
        {/* Header */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700">
              <Download className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-black text-slate-900">Export Spatial Ocean Intelligence</h2>
              <p className="text-[10px] text-slate-500 font-medium">GIS & Telemetry datasets for onboard ECDIS & GPS</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Options */}
        <div className="p-5 space-y-3">
          {/* GeoJSON */}
          <div 
            onClick={handleExportGeoJSON}
            className="p-3.5 rounded-2xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 cursor-pointer transition-all flex items-center justify-between group"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-blue-700">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <div className="font-bold text-slate-900 text-xs group-hover:text-blue-700">RFC 7946 GeoJSON Dataset</div>
                <div className="text-[11px] text-slate-500">PFZ polygons, centroids, and A* route waypoints for GIS</div>
              </div>
            </div>
            <Download className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
          </div>

          {/* CSV */}
          <div 
            onClick={handleExportCSV}
            className="p-3.5 rounded-2xl border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/40 cursor-pointer transition-all flex items-center justify-between group"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <div className="font-bold text-slate-900 text-xs group-hover:text-emerald-700">Tabular CSV Format</div>
                <div className="text-[11px] text-slate-500">Structured telemetry table for spreadsheet and logbook use</div>
              </div>
            </div>
            <Download className="w-4 h-4 text-slate-400 group-hover:text-emerald-600" />
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 border-t border-slate-100 bg-slate-50/60 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold text-xs cursor-pointer transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
