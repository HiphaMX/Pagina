import React, { useState } from "react";
import { X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { BusinessCategory, Community } from "@/types";
import { BusinessRegisterSchema } from "@/lib/schemas";

interface RegisterBusinessModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: BusinessCategory[];
  communities: Community[];
  apiBaseUrl?: string;
  onSuccess?: () => void;
}

export const RegisterBusinessModal: React.FC<RegisterBusinessModalProps> = ({
  isOpen,
  onClose,
  categories,
  communities,
  apiBaseUrl = "http://localhost:8000",
  onSuccess,
}) => {
  const [formData, setFormData] = useState({
    name: "",
    category_id: categories[0]?.id ? String(categories[0].id) : "1",
    community_id: "",
    is_home_based: false,
    address_reference: "",
    whatsapp_number: "",
    delivery_available: false,
    delivery_scope: "",
    description: "",
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

    // Validar con Zod
    const payloadToValidate = {
      name: formData.name,
      category_id: Number(formData.category_id),
      community_id: formData.community_id ? formData.community_id : null,
      is_home_based: formData.is_home_based,
      address_reference: formData.address_reference || null,
      whatsapp_number: formData.whatsapp_number,
      delivery_available: formData.delivery_available,
      delivery_scope: formData.delivery_scope || null,
      description: formData.description || null,
    };

    const validation = BusinessRegisterSchema.safeParse(payloadToValidate);
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
      const res = await fetch(`${apiBaseUrl}/api/v1/businesses/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validation.data),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Error al registrar el comercio.");
      }

      setSuccessMessage(true);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setServerError(err.message || "Error de conexión.");
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
              ¡Solicitud de Registro Enviada!
            </h3>
            <p className="text-sm text-slate-600 mb-6">
              Tu comercio o emprendimiento ha sido recibido y pasará a revisión vecinal. Una vez aprobado, aparecerá en el directorio comunitario.
            </p>
            <button
              onClick={onClose}
              className="w-full py-2.5 px-4 rounded-xl bg-natura-700 hover:bg-natura-800 text-white font-bold text-sm"
            >
              Entendido
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <h3 className="text-xl font-black text-slate-900">
                Registrar Comercio o Emprendimiento
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Conéctate con los residentes de cotos Natura y fraccionamientos vecinos.
              </p>
            </div>

            {serverError && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 text-rose-700 text-xs border border-rose-200">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{serverError}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Nombre del Negocio o Emprendimiento *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ej. Repostería Casera Dulce Bosque"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
              {formErrors.name && (
                <p className="text-xs text-rose-600 mt-1">{formErrors.name}</p>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Categoría *
                </label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-natura-500"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Coto / Fraccionamiento
                </label>
                <select
                  value={formData.community_id}
                  onChange={(e) => setFormData({ ...formData, community_id: e.target.value })}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-natura-500"
                >
                  <option value="">Sobre Avenida / Pie de Calle</option>
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
                WhatsApp de Pedidos (+52...) *
              </label>
              <input
                type="tel"
                value={formData.whatsapp_number}
                onChange={(e) => setFormData({ ...formData, whatsapp_number: e.target.value })}
                placeholder="+52 33 1234 5678"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
              {formErrors.whatsapp_number && (
                <p className="text-xs text-rose-600 mt-1">{formErrors.whatsapp_number}</p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_home_based"
                checked={formData.is_home_based}
                onChange={(e) => setFormData({ ...formData, is_home_based: e.target.checked })}
                className="w-4 h-4 rounded-sm text-natura-600 focus:ring-natura-500"
              />
              <label htmlFor="is_home_based" className="text-xs font-medium text-slate-700">
                Es un microemprendimiento dentro de casa (en coto privado)
              </label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="delivery_available"
                checked={formData.delivery_available}
                onChange={(e) => setFormData({ ...formData, delivery_available: e.target.checked })}
                className="w-4 h-4 rounded-sm text-natura-600 focus:ring-natura-500"
              />
              <label htmlFor="delivery_available" className="text-xs font-medium text-slate-700">
                Ofrezco servicio a domicilio / entrega en cotos
              </label>
            </div>

            {formData.delivery_available && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Cobertura de Entrega
                </label>
                <input
                  type="text"
                  value={formData.delivery_scope}
                  onChange={(e) => setFormData({ ...formData, delivery_scope: e.target.value })}
                  placeholder="Ej. Coto Roble, Encino, Ceiba y El Fortín"
                  className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Descripción de Productos o Servicios
              </label>
              <textarea
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe qué ofreces, especialidades y promociones..."
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-natura-500"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-natura-700 hover:bg-natura-800 text-white font-bold text-sm transition-all shadow-md shadow-natura-700/20 active:scale-95"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Enviar Registro para Aprobación"
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
