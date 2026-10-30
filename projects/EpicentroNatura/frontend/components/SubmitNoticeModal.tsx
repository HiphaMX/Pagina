import React, { useState } from "react";
import { X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Community } from "@/types";
import { CivicNoticeSubmitSchema } from "@/lib/schemas";

interface SubmitNoticeModalProps {
  isOpen: boolean;
  onClose: () => void;
  communities: Community[];
  apiBaseUrl?: string;
  onSuccess?: () => void;
}

export const SubmitNoticeModal: React.FC<SubmitNoticeModalProps> = ({
  isOpen,
  onClose,
  communities,
  apiBaseUrl = "http://localhost:8000",
  onSuccess,
}) => {
  const [formData, setFormData] = useState({
    title: "",
    type: "mascota_perdida" as "mascota_perdida" | "empleo_local" | "causa_social",
    community_id: "",
    content: "",
    contact_whatsapp: "",
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors({});
    setServerError(null);

    const payload = {
      title: formData.title,
      type: formData.type,
      community_id: formData.community_id ? formData.community_id : null,
      content: formData.content,
      contact_whatsapp: formData.contact_whatsapp || null,
    };

    const validation = CivicNoticeSubmitSchema.safeParse(payload);
    if (!validation.success) {
      const errors: Record<string, string> = {};
      validation.error.issues.forEach((issue) => {
        const fieldName = issue.path[0] as string;
        errors[fieldName] = issue.message;
      });
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/v1/notices/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validation.data),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Error al publicar el aviso.");
      }

      setSuccessMessage(true);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setServerError(err.message || "Error al comunicarse con el servidor.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="relative w-full max-w-lg rounded-3xl bg-white p-6 sm:p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {successMessage ? (
          <div className="text-center py-8">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">
              ¡Aviso Vecinal Recibido!
            </h3>
            <p className="text-sm text-slate-600 mb-6">
              Tu reporte ha sido enviado a moderación comunitaria. Al ser aprobado, permanecerá visible durante 15 días en el tablero cívico.
            </p>
            <button
              onClick={onClose}
              className="w-full py-2.5 px-4 rounded-xl bg-natura-700 hover:bg-natura-800 text-white font-bold text-sm"
            >
              Listo
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <h3 className="text-xl font-black text-slate-900">
                Publicar en Tablero Cívico
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Reporta mascotas extraviadas, vacantes locales o iniciativas sociales para los vecinos.
              </p>
            </div>

            {serverError && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 text-rose-700 text-xs border border-rose-200">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{serverError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Tipo de Publicación *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      type: e.target.value as any,
                    })
                  }
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-natura-500"
                >
                  <option value="mascota_perdida">🐾 Mascota Extraviada</option>
                  <option value="empleo_local">💼 Empleo Local / Apoyo</option>
                  <option value="causa_social">🤝 Causa Social Vecinal</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Coto / Ubicación
                </label>
                <select
                  value={formData.community_id}
                  onChange={(e) => setFormData({ ...formData, community_id: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-natura-500"
                >
                  <option value="">Toda la Zona / General</option>
                  {communities.map((comm) => (
                    <option key={comm.id} value={comm.id}>
                      {comm.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Título del Aviso *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Ej. Perrito Pug extraviado en Coto Roble"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
              {formErrors.title && (
                <p className="text-xs text-rose-600 mt-1">{formErrors.title}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Descripción Detallada *
              </label>
              <textarea
                rows={3}
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Incluye señas particulares, fecha, hora, o requisitos del empleo..."
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
              {formErrors.content && (
                <p className="text-xs text-rose-600 mt-1">{formErrors.content}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                WhatsApp de Contacto (Opcional)
              </label>
              <input
                type="tel"
                value={formData.contact_whatsapp}
                onChange={(e) =>
                  setFormData({ ...formData, contact_whatsapp: e.target.value })
                }
                placeholder="+52 33 1234 5678"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
              {formErrors.contact_whatsapp && (
                <p className="text-xs text-rose-600 mt-1">
                  {formErrors.contact_whatsapp}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-natura-700 hover:bg-natura-800 text-white font-bold text-sm transition-all shadow-md shadow-natura-700/20 active:scale-95"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Enviar Reporte a Revisión"
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
