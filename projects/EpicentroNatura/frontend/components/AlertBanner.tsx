import React from "react";
import { AlertTriangle, Clock, MapPin } from "lucide-react";
import { CivicNotice } from "@/types";

interface AlertBannerProps {
  alerts: CivicNotice[];
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="w-full space-y-3 mb-6">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="relative overflow-hidden rounded-2xl bg-amber-500/10 border border-amber-500/30 p-4 sm:p-5 shadow-sm"
        >
          <div className="flex items-start gap-3.5">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-sm shadow-amber-500/30">
              <AlertTriangle className="w-5 h-5 animate-pulse" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500 text-white">
                  Alerta de Zona
                </span>
                <span className="text-xs text-amber-900/80 font-medium flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {alert.community?.name || "Prolongación Mariano Otero / Zona Natura"}
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-amber-950 mb-1 leading-tight">
                {alert.title}
              </h3>
              <p className="text-sm text-amber-900/90 leading-relaxed">
                {alert.content}
              </p>
              <div className="mt-2.5 flex items-center gap-2 text-xs text-amber-800/70 font-medium">
                <Clock className="w-3.5 h-3.5" />
                <span>Vigencia restante: {alert.days_remaining} días</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
