import React from 'react';
import { 
  X, 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  CheckCheck, 
  Bell, 
  Radio, 
  Compass,
  MapPin,
  Clock
} from 'lucide-react';
import { OperationalAlert } from '../types';

interface OperationalAlertsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: OperationalAlert[];
  onAcknowledgeAlert: (alertId: string) => void;
  onAcknowledgeAll: () => void;
  onFocusRegion?: (zone: string) => void;
}

export const OperationalAlertsDrawer: React.FC<OperationalAlertsDrawerProps> = ({
  isOpen,
  onClose,
  alerts,
  onAcknowledgeAlert,
  onAcknowledgeAll
}) => {
  if (!isOpen) return null;

  const getSeverityBadge = (sev: OperationalAlert['severity']) => {
    switch (sev) {
      case 'CRITICAL':
        return {
          icon: <AlertOctagon className="w-4 h-4 text-rose-600 animate-pulse" />,
          bg: 'bg-rose-50 border-rose-300 text-rose-900',
          label: 'CRITICAL WARNING'
        };
      case 'WARNING':
        return {
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />,
          bg: 'bg-amber-50 border-amber-300 text-amber-900',
          label: 'HAZARD WARNING'
        };
      case 'ADVISORY':
        return {
          icon: <Radio className="w-4 h-4 text-blue-600" />,
          bg: 'bg-blue-50 border-blue-300 text-blue-900',
          label: 'COASTAL ADVISORY'
        };
      default:
        return {
          icon: <Info className="w-4 h-4 text-slate-600" />,
          bg: 'bg-slate-100 border-slate-300 text-slate-800',
          label: 'OPERATIONAL INFO'
        };
    }
  };

  const unreadCount = alerts.filter(a => !a.acknowledged).length;

  return (
    <div className="fixed top-14 bottom-0 right-0 z-[1200] w-full max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col font-['Outfit',sans-serif] text-slate-900 animate-in slide-in-from-right duration-200 max-h-[calc(100dvh-3.5rem)]">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center text-rose-700">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-900">Maritime Disaster & Hazard Alerts</h2>
            <p className="text-[10px] text-slate-500 font-medium">
              Verified IMD, INCOIS & GDACS emergency dispatches
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {unreadCount > 0 && (
            <button
              onClick={onAcknowledgeAll}
              className="text-[10px] font-bold text-blue-600 hover:text-blue-800 cursor-pointer"
            >
              Acknowledge All
            </button>
          )}
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-200 text-slate-500 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
        {alerts.length === 0 ? (
          <div className="p-8 text-center space-y-2 text-slate-500">
            <CheckCheck className="w-8 h-8 mx-auto text-emerald-500" />
            <div className="font-bold text-slate-700 text-sm">All Clear in Coastal Basins</div>
            <p className="text-[11px] text-slate-400">No active cyclones, gale warnings, or boundary breaches tracked.</p>
          </div>
        ) : (
          alerts.map(alert => {
            const badge = getSeverityBadge(alert.severity);
            return (
              <div 
                key={alert.alert_id}
                className={`p-3.5 rounded-2xl border transition-all space-y-2 ${
                  alert.acknowledged 
                    ? 'bg-slate-50/70 border-slate-200 text-slate-600 opacity-70' 
                    : `${badge.bg} shadow-sm`
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 text-[10px] font-bold">
                    {badge.icon}
                    <span>{badge.label}</span>
                  </div>
                  <span className="text-[10px] font-mono opacity-70">
                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <div>
                  <h3 className="text-xs font-black text-slate-900">{alert.title}</h3>
                  <p className="text-[11px] mt-1 leading-relaxed">{alert.message}</p>
                </div>

                <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[10px] font-medium">
                  <span className="truncate max-w-[180px]">Source: <strong>{alert.source}</strong></span>
                  {!alert.acknowledged ? (
                    <button
                      onClick={() => onAcknowledgeAlert(alert.alert_id)}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold cursor-pointer transition-colors"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="text-emerald-700 font-bold flex items-center space-x-1">
                      <CheckCheck className="w-3 h-3" />
                      <span>Acknowledged</span>
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Emergency Broadcast Contact Footer */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50/90 text-[11px] text-slate-600 flex items-center justify-between">
        <span>Coast Guard Distress: <strong>1554 / VHF Ch 16</strong></span>
        <span className="text-[10px] text-slate-400 font-mono">ISRO SIH-26176</span>
      </div>
    </div>
  );
};
