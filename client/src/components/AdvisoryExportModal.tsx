import React from 'react';
import { 
  FileText, 
  Printer, 
  Download, 
  X, 
  CheckCircle2, 
  QrCode, 
  ShieldCheck, 
  Waves, 
  Fish,
  Compass
} from 'lucide-react';
import { OfficialBulletin } from '../types';
import { t } from '../utils/translations';

interface AdvisoryExportModalProps {
  bulletin: OfficialBulletin | null;
  isOpen: boolean;
  onClose: () => void;
  currentLang?: string;
}

export const AdvisoryExportModal: React.FC<AdvisoryExportModalProps> = ({
  bulletin,
  isOpen,
  onClose,
  currentLang = 'en'
}) => {
  if (!isOpen || !bulletin) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-2xl space-y-6 text-slate-900 print:p-0 print:border-none print:shadow-none">
        {/* Modal Controls */}
        <div className="flex items-center justify-between border-b border-slate-200 pb-3 print:hidden">
          <div className="flex items-center space-x-2 text-blue-700 font-bold text-sm">
            <FileText className="w-4 h-4" />
            <span>{t('bulletin_generator', currentLang)}</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md transition-all cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Printable Bulletin Document */}
        <div className="space-y-5 print:space-y-3">
          {/* Government / ISRO Header */}
          <div className="text-center border-b-2 border-slate-800 pb-4">
            <div className="text-xs font-black uppercase tracking-widest text-orange-600">
              Government of India · Department of Space
            </div>
            <h1 className="text-xl md:text-2xl font-black text-slate-900 mt-1">
              INDIAN SPACE RESEARCH ORGANISATION (ISRO)
            </h1>
            <h2 className="text-sm font-bold text-blue-700">
              Joint Satellite Marine Intelligence & Potential Fishing Zone Advisory
            </h2>
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-500 mt-2 font-mono">
              <span>Bulletin ID: <strong>{bulletin.bulletin_id}</strong></span>
              <span>Issued: <strong>{bulletin.issue_date}</strong></span>
              <span>Validity: <strong>{bulletin.validity_period}</strong></span>
            </div>
          </div>

          {/* Sector & Clearance Verdict */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <div className="text-xs text-slate-500 font-semibold">Coastal Sector</div>
              <div className="text-sm font-black text-slate-900 mt-0.5">
                {bulletin.coastal_sector} & Surrounding EEZ
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-500 font-semibold">Sea-Venture Clearance</div>
                <div className={`text-sm font-black mt-0.5 ${
                  bulletin.sea_venture_verdict === 'SAFE_FOR_VENTURE' ? 'text-emerald-700' : 'text-amber-700'
                }`}>
                  {bulletin.sea_venture_verdict.replace(/_/g, ' ')}
                </div>
              </div>
              <div className="text-right font-mono text-xs font-bold text-blue-700">
                Score: {bulletin.safety_index_score}/100
              </div>
            </div>
          </div>

          {/* PFZ Coordinates Table */}
          <div className="space-y-2.5">
            <h3 className="text-xs font-black text-slate-900 flex items-center space-x-2">
              <Fish className="w-4 h-4 text-emerald-600" />
              <span>Recommended Potential Fishing Zones (ISRO Oceansat-3 Coincidence Analysis)</span>
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-slate-200 rounded-xl overflow-hidden shadow-xs">
                <thead className="bg-slate-100 text-slate-700 font-extrabold uppercase text-[10px] tracking-wider">
                  <tr>
                    <th className="p-2.5 border-b border-slate-200">{t('zone_name', currentLang)}</th>
                    <th className="p-2.5 border-b border-slate-200">{t('coordinates', currentLang)}</th>
                    <th className="p-2.5 border-b border-slate-200">{t('depth', currentLang)}</th>
                    <th className="p-2.5 border-b border-slate-200">{t('dominant_species', currentLang)}</th>
                    <th className="p-2.5 border-b border-slate-200">{t('confidence', currentLang)}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-[11px] text-slate-800">
                  {bulletin.top_pfz_advisories.map((pfz, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="p-2.5 font-bold text-blue-800">{pfz.name}</td>
                      <td className="p-2.5 font-mono">{pfz.latitude}°N, {pfz.longitude}°E</td>
                      <td className="p-2.5">{pfz.recommended_depth_m} m</td>
                      <td className="p-2.5 font-bold text-emerald-700">{pfz.dominant_species}</td>
                      <td className="p-2.5 font-black text-amber-700">{pfz.confidence_score_percent}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Meteorological & Geofence Summary */}
          <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-100 text-xs space-y-1.5 text-slate-800">
            <div>
              <strong>Meteorological Forecast:</strong> Wave Height: {bulletin.meteorological_summary.wave_height_m}m | 
              Winds: {bulletin.meteorological_summary.wind_speed_knots} kts | 
              Sea State: {bulletin.meteorological_summary.sea_state} | 
              Lightning Risk: {bulletin.meteorological_summary.squall_lightning_risk}
            </div>
            <div>
              <strong>Geofence Advisory:</strong> {bulletin.geofence_advisory}
            </div>
            <div>
              <strong>Emergency Assistance:</strong> {bulletin.emergency_contact}
            </div>
          </div>

          {/* Footer & QR Token */}
          <div className="flex items-center justify-between border-t border-slate-200 pt-3 text-xs text-slate-500">
            <div>
              Generated autonomously by <strong>Blue Orbit Agentic AI System (ISRO SIH 26176)</strong>
            </div>
            <div className="font-mono text-blue-700 font-bold">
              Auth Token: {bulletin.qr_verification_token}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
