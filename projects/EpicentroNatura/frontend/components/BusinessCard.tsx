import React from "react";
import {
  MapPin,
  Clock,
  Bike,
  Home,
  Store,
  ChevronRight,
} from "lucide-react";
import { Business } from "@/types";
import { WhatsAppButton } from "./WhatsAppButton";

interface BusinessCardProps {
  business: Business;
}

export const BusinessCard: React.FC<BusinessCardProps> = ({ business }) => {
  return (
    <div className="group relative flex flex-col justify-between rounded-2xl bg-white border border-slate-200/80 p-5 shadow-sm hover:shadow-md hover:border-natura-300 transition-all">
      <div>
        {/* Header: Badges superiores */}
        <div className="flex items-center justify-between gap-2 mb-3">
          {/* Badge tipo de ubicación */}
          {business.is_home_based ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
              <Home className="w-3.5 h-3.5 text-emerald-600" />
              En Coto
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              <Store className="w-3.5 h-3.5 text-slate-500" />
              Establecimiento
            </span>
          )}

          {/* Semáforo de horario en vivo */}
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                business.is_open_now
                  ? "bg-emerald-500 animate-pulse"
                  : "bg-rose-500"
              }`}
            />
            <span
              className={`text-xs font-medium ${
                business.is_open_now ? "text-emerald-700" : "text-rose-600"
              }`}
            >
              {business.is_open_now ? "Abierto ahora" : "Cerrado"}
            </span>
          </div>
        </div>

        {/* Nombre y Categoría */}
        <div className="mb-2">
          {business.category && (
            <span className="text-[11px] font-bold uppercase tracking-wider text-natura-600 mb-0.5 block">
              {business.category.name}
            </span>
          )}
          <h4 className="text-lg font-bold text-slate-900 group-hover:text-natura-700 transition-colors">
            {business.name}
          </h4>
        </div>

        {/* Descripción */}
        {business.description && (
          <p className="text-sm text-slate-600 line-clamp-2 mb-3 leading-relaxed">
            {business.description}
          </p>
        )}

        {/* Ubicación / Coto */}
        <div className="space-y-1.5 mb-4 text-xs text-slate-500">
          <div className="flex items-start gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
            <span className="line-clamp-1">
              {business.community?.name || business.address_reference || "Zona Mariano Otero"}
            </span>
          </div>

          {business.delivery_available && (
            <div className="flex items-start gap-1.5 text-natura-700 font-medium">
              <Bike className="w-3.5 h-3.5 text-natura-600 mt-0.5 flex-shrink-0" />
              <span className="line-clamp-1">
                {business.delivery_scope
                  ? `Entrega: ${business.delivery_scope}`
                  : "Servicio a domicilio disponible"}
              </span>
            </div>
          )}

          {business.opening_status_text && (
            <div className="flex items-center gap-1.5 text-slate-500">
              <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
              <span>{business.opening_status_text}</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer / Acción de Contacto */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
        <WhatsAppButton
          url={business.whatsapp_link}
          label="Pedir por WhatsApp"
          size="sm"
          className="w-full"
        />
      </div>
    </div>
  );
};
