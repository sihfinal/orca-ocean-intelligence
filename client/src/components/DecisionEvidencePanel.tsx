import React, { useState } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  XCircle, 
  HelpCircle, 
  CheckCircle2, 
  Info, 
  ChevronRight, 
  ChevronDown, 
  Activity, 
  Layers, 
  Clock, 
  Database, 
  FileCheck2, 
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Compass
} from 'lucide-react';
import { DecisionObject, EvidencePackage, ClaimValidationResult, DecisionStatusType } from '../types';

interface DecisionEvidencePanelProps {
  decision?: DecisionObject | null;
  evidencePackage?: EvidencePackage | null;
  claimValidation?: ClaimValidationResult | null;
  currentLang?: string;
  onSelectCandidate?: (candidateId: string) => void;
}

export const DecisionEvidencePanel: React.FC<DecisionEvidencePanelProps> = ({
  decision,
  evidencePackage,
  claimValidation,
  onSelectCandidate
}) => {
  const [activeTab, setActiveTab] = useState<'decision' | 'evidence' | 'provenance' | 'tradeoffs'>('decision');
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  if (!decision && !evidencePackage) {
    return (
      <div className="p-6 rounded-2xl bg-white/95 border border-slate-200 text-center space-y-3 shadow-sm">
        <div className="w-10 h-10 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <Compass className="w-5 h-5" />
        </div>
        <div className="text-xs font-bold text-slate-700">No Active Operational Decision</div>
        <div className="text-[11px] text-slate-500 max-w-xs mx-auto">
          Query ORCA via map click or chat to synthesize a multi-objective, evidence-backed marine recommendation.
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: DecisionStatusType) => {
    switch (status) {
      case 'RECOMMENDED':
        return {
          icon: <ShieldCheck className="w-4 h-4 text-emerald-600" />,
          bg: 'bg-emerald-50 border-emerald-300 text-emerald-800',
          label: 'RECOMMENDED (HIGH COMPLIANCE)',
          accessibleLabel: 'Status: Safe & Highly Recommended'
        };
      case 'ACCEPTABLE':
        return {
          icon: <CheckCircle2 className="w-4 h-4 text-blue-600" />,
          bg: 'bg-blue-50 border-blue-300 text-blue-800',
          label: 'ACCEPTABLE (MODERATE)',
          accessibleLabel: 'Status: Acceptable with Normal Vigilance'
        };
      case 'CAUTION':
        return {
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />,
          bg: 'bg-amber-50 border-amber-300 text-amber-800',
          label: 'EXERCISE CAUTION',
          accessibleLabel: 'Status: Caution Required - Elevated Risk'
        };
      case 'NO_GO':
        return {
          icon: <XCircle className="w-4 h-4 text-rose-600" />,
          bg: 'bg-rose-50 border-rose-400 text-rose-800 font-black',
          label: 'NO-GO / HAZARD OVERRIDE',
          accessibleLabel: 'Status: Hard Safety Gate Triggered. No Venture.'
        };
      case 'INSUFFICIENT_EVIDENCE':
        return {
          icon: <HelpCircle className="w-4 h-4 text-purple-600" />,
          bg: 'bg-purple-50 border-purple-300 text-purple-800',
          label: 'INSUFFICIENT TELEMETRY',
          accessibleLabel: 'Status: Telemetry Incomplete'
        };
      default:
        return {
          icon: <Info className="w-4 h-4 text-slate-600" />,
          bg: 'bg-slate-100 border-slate-300 text-slate-800',
          label: status,
          accessibleLabel: `Status: ${status}`
        };
    }
  };

  const statusInfo = decision ? getStatusBadge(decision.decision_status) : null;
  const conf = decision?.confidence;

  return (
    <div className="w-full rounded-2xl bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-sm overflow-hidden text-slate-900 text-xs font-['Outfit',sans-serif]">
      {/* 1. Header with Decision Status & Recommendation */}
      <div className="p-4 border-b border-slate-100 space-y-2">
        <div className="flex items-center justify-between flex-wrap gap-2">
          {statusInfo && (
            <div 
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-full border text-[11px] font-bold ${statusInfo.bg}`}
              aria-label={statusInfo.accessibleLabel}
              role="status"
            >
              {statusInfo.icon}
              <span>{statusInfo.label}</span>
            </div>
          )}

          {/* Claim Validation Status */}
          {claimValidation && (
            <div 
              className={`flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                claimValidation.is_valid 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              }`}
              title={claimValidation.is_valid ? 'Numeric claims match telemetry' : 'Filtered through safe fallback'}
            >
              <FileCheck2 className="w-3 h-3" />
              <span>{claimValidation.validation_status}</span>
            </div>
          )}
        </div>

        {decision && (
          <div>
            <h3 className="text-sm font-black text-slate-900 leading-snug">
              {decision.recommendation_title}
            </h3>
            {decision.recommended_target_name && (
              <p className="text-[11px] text-slate-500 mt-0.5">
                Target Zone: <strong className="text-blue-700">{decision.recommended_target_name}</strong>
              </p>
            )}
          </div>
        )}

        {/* Confidence Progress Bar */}
        {conf && (
          <div className="space-y-1 pt-1">
            <div className="flex items-center justify-between text-[10px] font-bold text-slate-600">
              <span>Inspectable Confidence</span>
              <span className="font-mono text-blue-700">{(conf.overall_confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  conf.overall_confidence >= 0.8 ? 'bg-emerald-500' : conf.overall_confidence >= 0.5 ? 'bg-blue-500' : 'bg-amber-500'
                }`}
                style={{ width: `${Math.min(100, Math.max(5, conf.overall_confidence * 100))}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* 2. Sub-Navigation Tabs */}
      <div className="flex items-center border-b border-slate-100 bg-slate-50/70 px-2">
        <button
          onClick={() => setActiveTab('decision')}
          className={`px-3 py-2 text-[11px] font-bold border-b-2 transition-colors cursor-pointer ${
            activeTab === 'decision' 
              ? 'border-blue-600 text-blue-700 bg-white' 
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Why & Risks
        </button>
        <button
          onClick={() => setActiveTab('evidence')}
          className={`px-3 py-2 text-[11px] font-bold border-b-2 transition-colors cursor-pointer ${
            activeTab === 'evidence' 
              ? 'border-blue-600 text-blue-700 bg-white' 
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Evidence ({evidencePackage?.items.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('provenance')}
          className={`px-3 py-2 text-[11px] font-bold border-b-2 transition-colors cursor-pointer ${
            activeTab === 'provenance' 
              ? 'border-blue-600 text-blue-700 bg-white' 
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Provenance DAG
        </button>
        {decision && decision.candidate_tradeoffs?.length > 0 && (
          <button
            onClick={() => setActiveTab('tradeoffs')}
            className={`px-3 py-2 text-[11px] font-bold border-b-2 transition-colors cursor-pointer ${
              activeTab === 'tradeoffs' 
                ? 'border-blue-600 text-blue-700 bg-white' 
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Tradeoffs ({decision.candidate_tradeoffs.length})
          </button>
        )}
      </div>

      {/* 3. Tab Contents */}
      <div className="p-4 max-h-[380px] overflow-y-auto space-y-3">
        {/* Tab 1: Decision (Why & Risks) */}
        {activeTab === 'decision' && decision && (
          <div className="space-y-3.5">
            {/* Supporting Factors */}
            <div className="space-y-1.5">
              <div className="text-[11px] font-bold text-emerald-800 flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Supporting Drivers (Why Recommended)</span>
              </div>
              <ul className="space-y-1 pl-5 list-disc text-[11px] text-slate-700 marker:text-emerald-500">
                {decision.supporting_factors.map((factor, i) => (
                  <li key={i}>{factor}</li>
                ))}
              </ul>
            </div>

            {/* Negative Factors / Operational Risks */}
            {decision.negative_factors.length > 0 && (
              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <div className="text-[11px] font-bold text-amber-800 flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Negative Factors & Marine Vigilance</span>
                </div>
                <ul className="space-y-1 pl-5 list-disc text-[11px] text-slate-700 marker:text-amber-500">
                  {decision.negative_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Data Limitations */}
            {decision.data_limitations.length > 0 && (
              <div className="space-y-1 pt-2 border-t border-slate-100 text-[10px] text-slate-500">
                <div className="font-bold flex items-center space-x-1 text-slate-600">
                  <Info className="w-3 h-3 text-slate-400" />
                  <span>Reported Data Limitations:</span>
                </div>
                <p>{decision.data_limitations.join(', ')}</p>
              </div>
            )}

            {/* Reversibility Triggers */}
            {decision.reversibility_triggers.length > 0 && (
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[10px] space-y-1">
                <span className="font-bold text-slate-700">Reversibility Condition:</span>
                <p className="text-slate-600">{decision.reversibility_triggers.join('; ')}</p>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Evidence Items */}
        {activeTab === 'evidence' && evidencePackage && (
          <div className="space-y-2">
            {/* Freshness Summary Strip */}
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px]">
              {Object.entries(evidencePackage.data_freshness_summary).map(([v, f]) => (
                <div key={v} className="flex flex-col">
                  <span className="text-slate-400 font-medium truncate">{v.replace(/_/g, ' ')}</span>
                  <span className={`font-mono font-bold ${
                    f === 'FRESH' ? 'text-emerald-600' : f === 'STALE' ? 'text-amber-600' : 'text-rose-600'
                  }`}>
                    {f}
                  </span>
                </div>
              ))}
            </div>

            {/* Evidence List */}
            <div className="space-y-1.5">
              {evidencePackage.items.map((ev) => {
                const isExp = expandedItem === ev.evidence_id;
                return (
                  <div 
                    key={ev.evidence_id}
                    className="p-2.5 rounded-xl border border-slate-100 hover:border-slate-200 bg-white space-y-1.5 transition-all"
                  >
                    <div 
                      onClick={() => setExpandedItem(isExp ? null : ev.evidence_id)}
                      className="flex items-center justify-between cursor-pointer"
                    >
                      <div className="flex items-center space-x-2 truncate">
                        <span className={`w-2 h-2 rounded-full ${
                          ev.freshness === 'FRESH' ? 'bg-emerald-500' : 'bg-amber-500'
                        }`} />
                        <span className="font-bold text-slate-800 text-[11px] truncate">
                          {ev.parameter_name.replace(/_/g, ' ')}
                        </span>
                        {ev.numeric_value !== undefined && ev.numeric_value !== null && (
                          <span className="font-mono text-blue-700 font-bold text-[11px]">
                            {ev.numeric_value} {ev.unit}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-mono">
                        <span className="px-1.5 py-0.2 rounded bg-slate-100 text-slate-600">
                          {ev.is_forecast ? 'FORECAST' : 'OBSERVATION'}
                        </span>
                        {isExp ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-600 leading-snug">{ev.claim}</p>

                    {isExp && (
                      <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-[10px] text-slate-500 font-mono">
                        <div>Source: <strong className="text-slate-700 font-sans">{ev.source_name}</strong></div>
                        <div>Type: <strong>{ev.source_type}</strong></div>
                        <div>Timestamp: <strong>{new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong></div>
                        <div>Freshness: <strong className={ev.freshness === 'FRESH' ? 'text-emerald-600' : 'text-amber-600'}>{ev.freshness} ({ev.age_hours.toFixed(1)}h)</strong></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 3: Provenance DAG Chain */}
        {activeTab === 'provenance' && decision && (
          <div className="space-y-3">
            <div className="text-[11px] text-slate-500 font-medium">
              Transparent multi-agent lineage from raw Earth Observation to verified recommendation:
            </div>
            <div className="relative pl-6 space-y-3 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-blue-200">
              {decision.provenance_graph.map((step, idx) => (
                <div key={idx} className="relative space-y-0.5">
                  <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-blue-600 text-white flex items-center justify-center text-[9px] font-bold">
                    {idx + 1}
                  </span>
                  <div className="text-[11px] font-bold text-slate-800 flex items-center space-x-1">
                    <span>{step.stage}</span>
                    <span className="text-[10px] text-blue-700 font-mono">({step.parameter})</span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-medium">
                    Source: <strong className="text-slate-700">{step.source}</strong> ({step.type})
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Candidate Tradeoffs */}
        {activeTab === 'tradeoffs' && decision && (
          <div className="space-y-2">
            <div className="text-[11px] text-slate-500 font-medium">
              Multi-objective tradeoff analysis comparing primary choice against alternatives:
            </div>
            <div className="space-y-2">
              {decision.candidate_tradeoffs.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between font-bold text-[11px]">
                    <span className="text-slate-800">{item.name}</span>
                    <button 
                      onClick={() => onSelectCandidate?.(item.candidate_id)}
                      className="text-[10px] text-blue-700 hover:underline font-bold"
                    >
                      Inspect Zone
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-1 text-[10px] font-mono">
                    <div>Suitability: <strong className={item.suitability_delta >= 0 ? 'text-emerald-700' : 'text-slate-700'}>{item.suitability_delta > 0 ? `+${item.suitability_delta.toFixed(2)}` : item.suitability_delta.toFixed(2)}</strong></div>
                    <div>Risk: <strong className={item.risk_delta <= 0 ? 'text-emerald-700' : 'text-rose-700'}>{item.risk_delta > 0 ? `+${item.risk_delta.toFixed(2)}` : item.risk_delta.toFixed(2)}</strong></div>
                    <div>Distance: <strong>{item.distance_delta_km > 0 ? `+${item.distance_delta_km.toFixed(1)}` : item.distance_delta_km.toFixed(1)} km</strong></div>
                  </div>
                  <p className="text-[11px] text-slate-600 italic">"{item.preference_reason}"</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
