import React from "react";
import {
  Clock,
  MapPin,
  ShieldCheck,
  Dog,
  Briefcase,
  HeartHandshake,
  Megaphone,
} from "lucide-react";
import { CivicNotice, CivicNoticeType } from "@/types";
import { WhatsAppButton } from "./WhatsAppButton";

interface NoticeCardProps {
  notice: CivicNotice;
}

const TYPE_CONFIG: Record<
  CivicNoticeType,
  { label: string; bg: string; text: string; icon: React.ComponentType<{ className?: string }> }
> = {
  alerta_zona: {
    label: "Alerta de Zona",
    bg: "bg-amber-100",
    text: "text-amber-800",
    icon: Megaphone,
  },
  comunicado_oficial: {
    label: "Comunicado Oficial",
    bg: "bg-blue-100",
    text: "text-blue-800",
    icon: ShieldCheck,
  },
  mascota_perdida: {
    label: "Mascota Extraviada",
    bg: "bg-rose-100",
    text: "text-rose-800",
    icon: Dog,
  },
  empleo_local: {
    label: "Empleo Local",
    bg: "bg-emerald-100",
    text: "text-emerald-800",
    icon: Briefcase,
  },
  causa_social: {
    label: "Causa Social",
    bg: "bg-purple-100",
    text: "text-purple-800",
    icon: HeartHandshake,
  },
};

export const NoticeCard: React.FC<NoticeCardProps> = ({ notice }) => {
  const config = TYPE_CONFIG[notice.type] || TYPE_CONFIG.comunicado_oficial;
  const Icon = config.icon;

  return (
    <div className="flex flex-col justify-between rounded-2xl bg-white border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-all">
      <div>
        {/* Header badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold ${config.bg} ${config.text}`}
          >
            <Icon className="w-3.5 h-3.5" />
            {config.label}
          </span>

          {notice.is_official && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-900 text-white">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              Verificado
            </span>
          )}
        </div>

        {/* Title */}
        <h4 className="text-base sm:text-lg font-bold text-slate-900 mb-2 leading-snug">
          {notice.title}
        </h4>

        {/* Content */}
        <p className="text-sm text-slate-600 line-clamp-3 mb-4 leading-relaxed whitespace-pre-line">
          {notice.content}
        </p>
      </div>

      {/* Footer details */}
      <div className="pt-3 border-t border-slate-100">
        <div className="flex items-center justify-between gap-2 mb-3 text-xs text-slate-500">
          <div className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span className="truncate max-w-[150px]">
              {notice.community?.name || "Toda la Zona"}
            </span>
          </div>
          <div className="flex items-center gap-1 text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>Vigencia: {notice.days_remaining}d</span>
          </div>
        </div>

        {notice.whatsapp_link && (
          <WhatsAppButton
            url={notice.whatsapp_link}
            label="Contactar por WhatsApp"
            size="sm"
            className="w-full"
          />
        )}
      </div>
    </div>
  );
};
