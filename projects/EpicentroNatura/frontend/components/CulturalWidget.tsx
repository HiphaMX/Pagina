import React, { useState } from "react";
import {
  Calendar,
  MapPin,
  Users,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
} from "lucide-react";
import { CulturalEvent } from "@/types";
import { formatDateTime } from "@/lib/utils";

interface CulturalWidgetProps {
  events: CulturalEvent[];
  onRsvpSuccess?: (eventId: string, newRsvpCount: number) => void;
  apiBaseUrl?: string;
}

export const CulturalWidget: React.FC<CulturalWidgetProps> = ({
  events,
  onRsvpSuccess,
  apiBaseUrl = "http://localhost:8000",
}) => {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [confirmedIds, setConfirmedIds] = useState<Set<string>>(new Set());
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Mostrar los primeros 3 eventos
  const displayEvents = events.slice(0, 3);

  const handleRsvp = async (eventId: string) => {
    setLoadingId(eventId);
    setErrorMessage(null);

    try {
      const res = await fetch(`${apiBaseUrl}/api/v1/events/${eventId}/rsvp`, {
        method: "POST",
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "No se pudo completar el registro.");
      }

      setConfirmedIds((prev) => new Set(prev).add(eventId));
      if (onRsvpSuccess) {
        onRsvpSuccess(eventId, data.current_rsvp_count);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Error al conectar con el servidor.");
    } finally {
      setLoadingId(null);
    }
  };

  if (!events || events.length === 0) {
    return (
      <div className="rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200/60 p-6 text-center">
        <Sparkles className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
        <h3 className="text-base font-bold text-slate-800">
          Fin de Semana en la Casa de la Cultura
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          No hay eventos programados en este momento. ¡Vuelve a consultar pronto!
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-3xl bg-gradient-to-br from-slate-900 to-natura-950 text-white p-6 sm:p-8 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <div className="flex items-center gap-2 text-natura-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Agenda Cultural Natura</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white">
            Fin de Semana en la Casa de la Cultura
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Parque Central Natura · Prolongación Mariano Otero
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="mb-4 flex items-center gap-2 p-3 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-200 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {displayEvents.map((event) => {
          const isConfirmed = confirmedIds.has(event.id);
          const isLoading = loadingId === event.id;

          return (
            <div
              key={event.id}
              className="flex flex-col justify-between rounded-2xl bg-white/10 backdrop-blur-sm border border-white/10 p-5 hover:bg-white/15 transition-all"
            >
              <div>
                {/* Header con cupo y categoría */}
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-natura-500/30 text-natura-300 border border-natura-400/20">
                    {event.target_audience === "kids"
                      ? "Infantil"
                      : event.target_audience === "family"
                      ? "Familiar"
                      : event.target_audience === "adults"
                      ? "Adultos"
                      : "Comunitario"}
                  </span>

                  {event.capacity_limit !== null && (
                    <span
                      className={`text-[11px] font-medium ${
                        event.is_sold_out
                          ? "text-rose-400"
                          : "text-emerald-300"
                      }`}
                    >
                      {event.is_sold_out
                        ? "Cupo Lleno"
                        : `${event.spots_remaining} lugares`}
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-white mb-2 leading-snug">
                  {event.title}
                </h3>

                {event.description && (
                  <p className="text-xs text-slate-300 line-clamp-2 mb-3">
                    {event.description}
                  </p>
                )}

                <div className="space-y-1.5 text-xs text-slate-300 mb-4">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-natura-400" />
                    <span>{formatDateTime(event.start_datetime)}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-natura-400" />
                    <span className="truncate">{event.location_name}</span>
                  </div>
                </div>
              </div>

              {/* Botón de RSVP */}
              <div>
                {isConfirmed ? (
                  <div className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-semibold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>¡Lugar reservado!</span>
                  </div>
                ) : (
                  <button
                    disabled={event.is_sold_out || isLoading}
                    onClick={() => handleRsvp(event.id)}
                    className={`w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-bold transition-all ${
                      event.is_sold_out
                        ? "bg-white/10 text-slate-400 cursor-not-allowed"
                        : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 active:scale-95 shadow-sm shadow-emerald-500/30"
                    }`}
                  >
                    {isLoading ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : event.is_sold_out ? (
                      "Cupo Agotado"
                    ) : (
                      <>
                        <Users className="w-3.5 h-3.5" />
                        <span>Confirmar Asistencia (RSVP)</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
