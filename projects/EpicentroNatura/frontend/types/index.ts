export type CommunityType = "coto_natura" | "fraccionamiento_vecino" | "espacio_publico";

export interface Community {
  id: string;
  name: string;
  slug: string;
  type: CommunityType;
  is_active: boolean;
}

export interface BusinessCategory {
  id: number;
  name: string;
  slug: string;
  icon_name: string;
}

export type BusinessStatus = "pending_approval" | "active" | "suspended";

export type BusinessType = "local_establecido" | "emprendimiento" | "servicios_profesionales";

export interface Business {
  id: string;
  community_id: string | null;
  category_id: number;
  name: string;
  slug: string;
  description: string | null;
  business_type: BusinessType;
  is_home_based: boolean;
  address_reference: string | null;
  phone_number: string | null;
  whatsapp_number: string;
  delivery_available: boolean;
  delivery_scope: string | null;
  has_km0_badge: boolean;
  km0_reason: string | null;
  opening_hours: Record<string, { open: string; close: string } | null> | null;
  status: BusinessStatus;
  created_at: string;
  category?: BusinessCategory;
  community?: Community;
  is_open_now: boolean;
  opening_status_text?: string;
  whatsapp_link?: string;
}

export type TargetAudience = "kids" | "family" | "adults" | "all";

export interface CulturalEvent {
  id: string;
  title: string;
  slug: string;
  organizer: string;
  description: string | null;
  start_datetime: string;
  end_datetime: string;
  location_name: string;
  target_audience: TargetAudience;
  capacity_limit: number | null;
  current_rsvp_count: number;
  is_cancelled: boolean;
  is_sold_out: boolean;
  spots_remaining: number | null;
}

export type CivicNoticeType =
  | "alerta_zona"
  | "comunicado_oficial"
  | "mascota_perdida"
  | "empleo_local"
  | "causa_social";

export type CivicNoticeStatus = "pending_moderation" | "active" | "expired" | "archived";

export interface CivicNotice {
  id: string;
  community_id: string | null;
  type: CivicNoticeType;
  title: string;
  content: string;
  contact_whatsapp: string | null;
  is_official: boolean;
  published_at: string;
  expires_at: string;
  status: CivicNoticeStatus;
  community?: Community;
  days_remaining: number;
  whatsapp_link?: string;
}
