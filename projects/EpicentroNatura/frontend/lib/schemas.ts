import { z } from "zod";

// Validación de teléfono E.164 (permite prefijo '+' y entre 8 y 15 dígitos numéricos)
const phoneRegex = /^\+?[1-9]\d{7,14}$/;

export const BusinessRegisterSchema = z.object({
  name: z
    .string({ required_error: "El nombre es obligatorio" })
    .min(2, "El nombre debe tener al menos 2 caracteres")
    .max(150, "Máximo 150 caracteres"),
  category_id: z.coerce
    .number({ required_error: "Selecciona una categoría" })
    .int()
    .positive("Categoría inválida"),
  community_id: z
    .string()
    .uuid("Comunidad inválida")
    .nullable()
    .optional(),
  is_home_based: z.boolean().default(false),
  address_reference: z
    .string()
    .max(255, "Máximo 255 caracteres")
    .optional()
    .nullable(),
  whatsapp_number: z
    .string({ required_error: "El WhatsApp es obligatorio" })
    .regex(phoneRegex, "Ingresa un número válido con lada (ej: +523312345678 o 3312345678)"),
  delivery_available: z.boolean().default(false),
  delivery_scope: z
    .string()
    .max(500, "Máximo 500 caracteres")
    .optional()
    .nullable(),
  description: z
    .string()
    .max(1000, "Máximo 1000 caracteres")
    .optional()
    .nullable(),
});

export type BusinessRegisterInput = z.infer<typeof BusinessRegisterSchema>;


export const CivicNoticeSubmitSchema = z.object({
  title: z
    .string({ required_error: "El título es obligatorio" })
    .min(3, "Mínimo 3 caracteres")
    .max(150, "Máximo 150 caracteres"),
  content: z
    .string({ required_error: "La descripción es requerida" })
    .min(10, "Por favor sé más descriptivo (mínimo 10 caracteres)")
    .max(3000, "Máximo 3000 caracteres"),
  type: z.enum(["mascota_perdida", "empleo_local", "causa_social"], {
    errorMap: () => ({ message: "Selecciona un tipo de reporte válido" }),
  }),
  community_id: z
    .string()
    .uuid("Comunidad inválida")
    .nullable()
    .optional(),
  contact_whatsapp: z
    .string()
    .regex(phoneRegex, "Número de WhatsApp inválido")
    .optional()
    .nullable()
    .or(z.literal("")),
});

export type CivicNoticeSubmitInput = z.infer<typeof CivicNoticeSubmitSchema>;


export const RSVPSchema = z.object({
  event_id: z.string().uuid("ID de evento inválido"),
});

export type RSVPInput = z.infer<typeof RSVPSchema>;
