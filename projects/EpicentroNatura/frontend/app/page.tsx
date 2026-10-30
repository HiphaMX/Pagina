"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Trees,
  Search,
  MapPin,
  Store,
  Home,
  Briefcase,
  Phone,
  MessageCircle,
  Clock,
  Leaf,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  Flame,
  Stethoscope,
  Wrench,
  Sparkles,
  Utensils,
  Pill,
  Dog,
  Coffee,
  HeartPulse,
  GraduationCap,
  Dumbbell,
  Hammer,
  ShoppingBasket,
  ShieldCheck,
  CheckCircle,
  Palette,
  Megaphone,
  X,
  Copy,
  ExternalLink,
  Crosshair,
  AlertCircle,
  ArrowRight,
} from "lucide-react";
import { Business, BusinessType } from "@/types";
import { AbstractCategoryIcon } from "@/components/AbstractCategoryIcon";

interface CommercialBusiness {
  id: string;
  name: string;
  category_slug: string;
  category_label: string;
  type_slug: BusinessType;
  type_label: string;
  address: string;
  community_slug: string;
  community_name: string;
  phone: string;
  whatsapp: string;
  hours: string;
  is_open_now: boolean;
  has_km0_badge: boolean;
  km0_reason: string | null;
  cta_type: "whatsapp_order" | "call_and_whatsapp" | "service_whatsapp";
  description: string;
}

const ALL_BUSINESSES: CommercialBusiness[] = [
  // 1. Comida y Delivery
  {
    id: "b1",
    name: "El Güero Taquero",
    category_slug: "comida-delivery",
    category_label: "Comida y Delivery",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Av. Mariano Otero #4290 (Frente al ingreso Coto Ceiba)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0202",
    whatsapp: "+523315550202",
    hours: "Abierto hoy · 18:00 a 01:30 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "whatsapp_order",
    description: "Tacos y costras de suadero, pastor con piña asada al carbón, carnaza, arrachera, pancita y tripita dorada. Servidos con tortillas calientitas y salsas caseras.",
  },
  {
    id: "b2",
    name: "Pizzas a la Leña La Cantera",
    category_slug: "comida-delivery",
    category_label: "Comida y Delivery",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prol. Mariano Otero esq. Las Rosas (Ingreso Los Robles)",
    community_slug: "los-robles",
    community_name: "Los Robles",
    phone: "33 1555 0105",
    whatsapp: "+523315550105",
    hours: "Martes a Domingo · 18:30 a 23:30 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Entrega limpia en bici y moto eléctrica a cotos",
    cta_type: "whatsapp_order",
    description: "Pizzas rústicas horneadas al momento en horno de piedra con masa madre fermentada 48 horas, salsa San Marzano y quesos artesanales.",
  },

  // 2. Farmacias
  {
    id: "b3",
    name: "Farmacia Mariano Otero 24 Horas",
    category_slug: "farmacias",
    category_label: "Farmacias",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prol. Mariano Otero #4500 (Zona El Fortín)",
    community_slug: "el-fortin",
    community_name: "El Fortín",
    phone: "33 1555 0201",
    whatsapp: "+523315550201",
    hours: "Abierto 24 Horas",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Reparto limpio en bici de carga a casetas de cotos",
    cta_type: "call_and_whatsapp",
    description: "Medicamentos de patente, genéricos, material de curación y fórmulas para bebés con servicio a domicilio.",
  },

  // 3. Mascotas y Veterinarias
  {
    id: "b4",
    name: "Veterinaria Huellitas Natura",
    category_slug: "veterinarias",
    category_label: "Veterinarias",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Plaza Natura Local 2 (Junto a Parque Central)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0207",
    whatsapp: "+523315550207",
    hours: "Lunes a Sábado · 09:00 a 20:00 hrs · Urgencias 24h",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Atención y traslado en coto en carrito eléctrico",
    cta_type: "call_and_whatsapp",
    description: "Consultas médicas veterinarias, cuadro completo de vacunas, desparasitaciones, cirugías menores y estética canina profesional.",
  },

  // 4. Postres y café
  {
    id: "b5",
    name: "Repostería Artesanal Dulce Bosque",
    category_slug: "postres-cafe",
    category_label: "Postres y café",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Luna Bosque Residencial · Casa 42",
    community_slug: "luna-bosque",
    community_name: "Luna Bosque",
    phone: "33 1555 0101",
    whatsapp: "+523315550101",
    hours: "Pedidos con 24h · Lunes a Domingo",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Horneado casero y entrega a pie a tu puerta",
    cta_type: "whatsapp_order",
    description: "Pasteles de zanahoria, pays de frutos rojos, galletas chispas de chocolate y brownies artesanales.",
  },

  // 5. Productos artesanales
  {
    id: "b6",
    name: "Velas & Jabones Botánicos La Primavera",
    category_slug: "productos-artesanales",
    category_label: "Productos artesanales",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Entorno Bosque de la Primavera · Taller Botánico",
    community_slug: "bosque-primavera",
    community_name: "Bosque de la primavera",
    phone: "33 1555 0107",
    whatsapp: "+523315550107",
    hours: "Bajo pedido semanal",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Cero emisiones; entrega a mano en cotos Natura",
    cta_type: "whatsapp_order",
    description: "Jabones de avena y miel, velas de cera de soya aromatizadas con esencias de pino y lavanda del bosque.",
  },

  // 6. Servicios hogar
  {
    id: "b7",
    name: "Planchaduría Doña Mary",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "La Granja (Prolongación Mariano Otero)",
    community_slug: "la-granja",
    community_name: "La Granja",
    phone: "33 1555 0208",
    whatsapp: "+523315550208",
    hours: "Lunes a Viernes · 08:00 a 19:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Recolección y entrega a pie en cotos Natura",
    cta_type: "service_whatsapp",
    description: "Planchado profesional por docena en prendas de vestir, camisas y uniformes escolares con almidón ligero y entrega protegida en ganchos.",
  },
  {
    id: "b8",
    name: "AquaWash Detallado en Cochera",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Puerta del Bosque y cotos vecinos",
    community_slug: "puerta-del-bosque",
    community_name: "Puerta del Bosque",
    phone: "33 1555 0103",
    whatsapp: "+523315550103",
    hours: "Lunes a Sábado · 08:00 a 18:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Lavado en seco sin gasolina ni desperdicio de agua",
    cta_type: "service_whatsapp",
    description: "Lavado automotriz en seco, abrillantado, encerado cerámico y aspirado profundo de tapicería directo en la cochera de tu casa.",
  },

  // 7. Atención médica y Servicios profesionales
  {
    id: "b9",
    name: "Consultorio Médico Familiar Dra. Sandra Morales",
    category_slug: "atencion-medica",
    category_label: "Atención médica",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Punta de Otero #120 (Consultorios Médicos)",
    community_slug: "punta-de-otero",
    community_name: "Punta de Otero",
    phone: "33 1555 0201",
    whatsapp: "+523315550201",
    hours: "Lunes a Domingo · 24 Horas",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "call_and_whatsapp",
    description: "Consulta médica general, certificados médicos, control de glucosa y presión arterial, suturas menores.",
  },
  {
    id: "b10",
    name: "VoltTech Electricistas & Plomería Exprés",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Monte Verde Coto 3",
    community_slug: "monte-verde",
    community_name: "Monte Verde",
    phone: "33 1555 0203",
    whatsapp: "+523315550203",
    hours: "Servicio de Urgencias 24/7",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Desplazamiento local en scooter eléctrico sin gasolina",
    cta_type: "service_whatsapp",
    description: "Reparación de cortocircuitos, bombas de agua, hidroneumáticos, fugas de gas y calentadores solares.",
  },
  {
    id: "b11",
    name: "Valeria Rivas Asesoría Inmobiliaria",
    category_slug: "servicios-profesionales",
    category_label: "Servicios profesionales",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Misión la Floresta esq. Prol. Mariano Otero",
    community_slug: "mision-la-floresta",
    community_name: "Misión la Floresta",
    phone: "33 1555 0209",
    whatsapp: "+523315550209",
    hours: "Lunes a Sábado · 09:00 a 19:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Atención vecinal a pie dentro de cotos Natura",
    cta_type: "service_whatsapp",
    description: "Especialista en compra, venta y arrendamiento de casas residenciales en cotos de Mariano Otero y El Fortín. Valuación comercial sin costo.",
  },
  {
    id: "b12",
    name: "Clases de Matemáticas & Física Ing. Alejandro Ruiz",
    category_slug: "clases-particulares",
    category_label: "Clases particulares",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Natura Bosque Residencial (Coto Encino)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0108",
    whatsapp: "+523315550108",
    hours: "Tardes · Lunes a Viernes",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Profesor residente en el coto; desplazamiento a pie",
    cta_type: "service_whatsapp",
    description: "Regularización y preparación para exámenes de secundaria, preparatoria y universidad. 10 años de experiencia.",
  },
];

const CULTURAL_OFFERINGS = [
  {
    title: "Taller Infantil de Escultura en Barro & Pintura",
    category: "Taller Infantil (5 a 12 años)",
    datetime: "Sábados · 10:00 a 12:00 hrs",
    location: "Kiosco Parque Central Natura",
    description: "Modelado con arcilla natural de la zona y acuarelas sobre caballete al aire libre.",
    spots: 11,
  },
  {
    title: "Noche de Cine Vecinal al Aire Libre",
    category: "Para Toda la Familia",
    datetime: "Sábado 15 · 19:30 hrs",
    location: "Explanada Verde Parque Central",
    description: "Proyección en pantalla gigante bajo las estrellas. Palomitas gratis para niños de cotos.",
    spots: 38,
  },
  {
    title: "Clases Semanales de Danza Folclórica & Ritmos",
    category: "Clases Presenciales",
    datetime: "Martes y Jueves · 17:00 hrs",
    location: "Salón Polivalente Casa de Cultura",
    description: "Grupos infantiles y de adultos mayores con instructores del Instituto de Cultura Zapopan.",
    spots: 15,
  },
];

const COMMUNITY_NOTICES = [
  {
    type: "Mascota Extraviada",
    badge_bg: "bg-rose-100 text-rose-700 border-rose-200",
    title: "Perrito Schnauzer gris extraviado cerca de Coto Encino",
    content: "Responde a 'Max', llevaba collar azul con placa. Si lo viste por favor comunícate a caseta o vía WhatsApp.",
    community: "Natura Bosque Residencial",
    days: 14,
    whatsapp: "+523318889901",
  },
  {
    type: "Comunicado Oficial",
    badge_bg: "bg-blue-100 text-blue-700 border-blue-200",
    title: "Nuevo tag vehicular de residentes en acceso principal",
    content: "A partir del lunes se requiere el nuevo tag RFID con chip para acceso automatizado por la pluma.",
    community: "Los Robles",
    days: 20,
    whatsapp: "+523315550999",
  },
  {
    type: "Empleo Local",
    badge_bg: "bg-emerald-100 text-emerald-800 border-emerald-200",
    title: "Se solicita apoyo para jardinería y mantenimiento",
    content: "Para áreas comunes de coto privado 3 días a la semana. Enviar mensaje por WhatsApp con referencias.",
    community: "El Fortín",
    days: 12,
    whatsapp: "+523318889902",
  },
];

export default function EpicentroNaturaCleanLight() {
  const [mainSection, setMainSection] = useState<"directorio" | "cultura" | "comunidad">("directorio");
  const [currentSlide, setCurrentSlide] = useState(0);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCoto, setSelectedCoto] = useState("all");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedType, setSelectedType] = useState<"all" | BusinessType>("all");
  const [km0Only, setKm0Only] = useState(false);

  // Modals
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [isNoticeOpen, setIsNoticeOpen] = useState(false);
  const [locationModalData, setLocationModalData] = useState<{
    isOpen: boolean;
    name: string;
    address: string;
    note: string;
    copied: boolean;
  }>({
    isOpen: false,
    name: "",
    address: "",
    note: "",
    copied: false,
  });

  // Geolocation near me state
  const [isNearMeLoading, setIsNearMeLoading] = useState(false);
  const [isNearMeActive, setIsNearMeActive] = useState(false);
  const [geoToast, setGeoToast] = useState<{ message: string; isSuccess: boolean } | null>(null);

  const handleDetectNearMe = () => {
    if (typeof window === "undefined" || !navigator.geolocation) {
      setGeoToast({ message: "Geolocalización no soportada por el navegador", isSuccess: false });
      setTimeout(() => setGeoToast(null), 4500);
      return;
    }

    setIsNearMeLoading(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsNearMeLoading(false);
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;

        const ZONES_GEO = [
          { slug: "natura-bosque-residencial", name: "Natura Bosque Residencial", lat: 20.6272, lon: -103.4682 },
          { slug: "los-robles", name: "Los Robles", lat: 20.6195, lon: -103.4750 },
          { slug: "bosque-primavera", name: "Bosque de la primavera", lat: 20.6350, lon: -103.4900 },
          { slug: "el-fortin", name: "El Fortín", lat: 20.6385, lon: -103.4560 },
          { slug: "luna-bosque", name: "Luna Bosque", lat: 20.6310, lon: -103.4610 },
          { slug: "la-granja", name: "La Granja", lat: 20.6340, lon: -103.4500 },
          { slug: "puerta-del-bosque", name: "Puerta del Bosque", lat: 20.6410, lon: -103.4520 },
          { slug: "punta-de-otero", name: "Punta de Otero", lat: 20.6230, lon: -103.4650 },
          { slug: "monte-verde", name: "Monte Verde", lat: 20.6170, lon: -103.4700 },
          { slug: "mision-la-floresta", name: "Misión la Floresta", lat: 20.6450, lon: -103.4470 },
        ];

        function getDistKm(lat1: number, lon1: number, lat2: number, lon2: number) {
          const R = 6371;
          const dLat = ((lat2 - lat1) * Math.PI) / 180;
          const dLon = ((lon2 - lon1) * Math.PI) / 180;
          const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos((lat1 * Math.PI) / 180) *
              Math.cos((lat2 * Math.PI) / 180) *
              Math.sin(dLon / 2) *
              Math.sin(dLon / 2);
          return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        }

        let nearestZone = ZONES_GEO[0];
        let minDist = getDistKm(userLat, userLon, ZONES_GEO[0].lat, ZONES_GEO[0].lon);

        for (let i = 1; i < ZONES_GEO.length; i++) {
          const d = getDistKm(userLat, userLon, ZONES_GEO[i].lat, ZONES_GEO[i].lon);
          if (d < minDist) {
            minDist = d;
            nearestZone = ZONES_GEO[i];
          }
        }

        setSelectedCoto(nearestZone.slug);
        setIsNearMeActive(true);

        const distStr = minDist < 1 ? `${Math.round(minDist * 1000)} m` : `${minDist.toFixed(1)} km`;
        setGeoToast({
          message: `📍 Ubicación detectada: ${nearestZone.name} (${distStr}). Mostrando opciones cercanas.`,
          isSuccess: true,
        });
        setTimeout(() => setGeoToast(null), 4500);
      },
      (error) => {
        setIsNearMeLoading(false);
        setSelectedCoto("natura-bosque-residencial");
        setIsNearMeActive(true);
        setGeoToast({
          message: "📍 Centrado en Epicentro Natura (Natura Bosque Residencial).",
          isSuccess: true,
        });
        setTimeout(() => setGeoToast(null), 4500);
      },
      { timeout: 7000, enableHighAccuracy: true }
    );
  };

  // Slide auto-rotation (6 slides)
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % 6);
    }, 7000);
    return () => clearInterval(timer);
  }, []);

  const filteredBusinesses = ALL_BUSINESSES.filter((b) => {
    const q = searchQuery.toLowerCase();
    const matchText =
      !q ||
      b.name.toLowerCase().includes(q) ||
      b.description.toLowerCase().includes(q) ||
      b.category_label.toLowerCase().includes(q);
    const matchCoto = selectedCoto === "all" || b.community_slug === selectedCoto;
    const matchCat = selectedCategory === "all" || b.category_slug === selectedCategory;
    const matchType = selectedType === "all" || b.type_slug === selectedType;
    const matchKm0 = !km0Only || b.has_km0_badge;
    return matchText && matchCoto && matchCat && matchType && matchKm0;
  });

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased selection:bg-emerald-500 selection:text-white">
      {/* 1. TOP BAR COMUNITARIA */}
      <aside className="bg-slate-950 text-white text-xs py-2 px-4 border-b border-slate-800 text-center">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <span className="font-bold text-slate-200 tracking-wide text-xs sm:text-[13px]">
            Comunidad Epicentro Natura
          </span>
        </div>
      </aside>

      {/* 2. NAVBAR LIMPIO APPLE / RAPPI CON BUSCADOR Y SELECTOR DE CERCANÍA */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 sm:gap-4">
            
            {/* Fila Superior / Izquierda: Logo y Botón Registrar Móvil */}
            <div className="w-full md:w-auto flex items-center justify-between gap-4">
              {/* Logo Requerido: Epicentro + etiqueta natura (sin subtítulo) */}
              <a href="#" className="flex items-center gap-2.5 group shrink-0">
                <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-gradient-to-tr from-emerald-800 to-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-600/20 group-hover:scale-105 transition-transform">
                  <Trees className="w-6 h-6 stroke-[2.2]" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-black tracking-tight text-slate-950">Epicentro</span>
                  <span className="text-[11px] font-extrabold lowercase tracking-wide px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                    natura
                  </span>
                </div>
              </a>

              {/* Botón Registrar en móvil */}
              <div className="flex md:hidden items-center gap-2">
                <button
                  onClick={() => setIsRegisterOpen(true)}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-all shadow-sm"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Registrar</span>
                </button>
              </div>
            </div>

            {/* BARRA DE BÚSQUEDA INTEGRADA EN NAVBAR CON FILTROS POR CERCANÍA GEOGRÁFICA */}
            <div className="w-full md:flex-1 md:max-w-2xl lg:max-w-3xl">
              <div className="relative flex items-center bg-slate-100 hover:bg-slate-200/70 focus-within:bg-white rounded-2xl border border-slate-200 focus-within:border-emerald-600 focus-within:ring-2 focus-within:ring-emerald-600/20 transition-all p-1.5 sm:p-2">
                <div className="pl-2.5 pr-2 text-emerald-600 shrink-0">
                  <Search className="w-4 h-4 sm:w-5 sm:h-5 stroke-[2.5]" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar comida, farmacia, servicios..."
                  className="w-full py-1 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 bg-transparent focus:outline-hidden font-medium"
                />

                {/* Selector de Cercanía Geográfica al Epicentro Natura Bosque Residencial */}
                <div className="flex items-center gap-1.5 border-l border-slate-200 pl-2 sm:pl-3 pr-1 shrink-0">
                  <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                  <select
                    value={selectedCoto}
                    onChange={(e) => {
                      setSelectedCoto(e.target.value);
                      if (e.target.value === "all") setIsNearMeActive(false);
                    }}
                    className="bg-transparent text-[11px] sm:text-xs font-bold text-slate-800 focus:outline-hidden cursor-pointer max-w-[105px] sm:max-w-[170px] truncate"
                  >
                    <option value="all">Toda la zona</option>
                    <option value="natura-bosque-residencial">Natura Bosque Residencial</option>
                    <option value="los-robles">Los Robles</option>
                    <option value="bosque-primavera">Bosque de la primavera</option>
                    <option value="el-fortin">El Fortín</option>
                    <option value="luna-bosque">Luna Bosque</option>
                    <option value="la-granja">La Granja</option>
                    <option value="puerta-del-bosque">Puerta del Bosque</option>
                    <option value="punta-de-otero">Punta de Otero</option>
                    <option value="monte-verde">Monte Verde</option>
                    <option value="mision-la-floresta">Misión la Floresta</option>
                  </select>

                  {/* Botón Cerca de mí (Geolocalización) */}
                  <button
                    type="button"
                    onClick={handleDetectNearMe}
                    title="Detectar opciones cercanas por geolocalización"
                    className={`inline-flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold shrink-0 transition-all active:scale-95 shadow-2xs ${
                      isNearMeActive
                        ? "bg-emerald-600 text-white border border-emerald-700"
                        : "text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 hover:border-emerald-500"
                    }`}
                  >
                    <Crosshair className={`w-3.5 h-3.5 ${isNearMeLoading ? "animate-spin" : isNearMeActive ? "text-white" : "text-emerald-600"}`} />
                    <span className="whitespace-nowrap">
                      {isNearMeLoading ? "Buscando..." : isNearMeActive ? "Cerca de ti ✓" : "Cerca de mí"}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Botón Registrar en Escritorio */}
            <div className="hidden md:flex items-center gap-2 shrink-0">
              <button
                onClick={() => setIsRegisterOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 active:scale-95 transition-all shadow-md shadow-emerald-600/20"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Registrar Negocio</span>
              </button>
            </div>

          </div>
        </div>
      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="flex-1 space-y-10">
        {/* 1. MEGA HERO 1 SLIDER CASI DEL TAMAÑO DE LA PANTALLA (6 MARCAS LOCALES) */}
        <section className="relative w-full px-3 sm:px-6 lg:px-8 pt-4">
          <div className="max-w-7xl mx-auto relative overflow-hidden rounded-3xl bg-slate-950 border border-slate-800 shadow-2xl">
            {/* Slider Container */}
            <div className="relative min-h-[76vh] sm:min-h-[82vh] flex items-stretch">
              {/* SLIDE 1: TAQUERÍA (El Güero Taquero) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 0 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-amber-400 block mb-2">
                    Comida & Delivery
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    El Güero Taquero
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Tacos y costras de suadero, pastor con piña asada al carbón, carnaza, arrachera, pancita y tripita dorada. Servidos con tortillas recién hechas, cebollitas cambray y salsas de molcajete directo a la pluma de tu coto.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550202?text=Hola%20El%20G%C3%BCero%20Taquero,%20quiero%20hacer%20un%20pedido%20a%20domicilio%20en%20mi%20coto"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550202"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "El Güero Taquero",
                        address: "Prol. Mariano Otero #4290 (Frente al ingreso Coto Ceiba)",
                        note: "Entrega en caseta de todos los cotos Natura y El Fortín",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>

              {/* SLIDE 2: VETERINARIA (Veterinaria Huellitas Natura) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 1 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1576201836106-db1758fd1c97?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-emerald-400 block mb-2">
                    Veterinarias
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    Veterinaria Huellitas Natura
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Consultas médicas veterinarias, cuadro completo de vacunas, desparasitaciones, cirugías menores y estética canina profesional con baño medicado y secado. Cuidamos a tu mejor amigo con entrega y atención en cotos.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550207?text=Hola%20Veterinaria%20Huellitas%20Natura,%20necesito%20atenci%C3%B3n%20para%20mi%20mascota"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550207"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "Veterinaria Huellitas Natura",
                        address: "Plaza Natura Local 2 (Junto a Parque Central)",
                        note: "Atención presencial y servicio a domicilio en cotos",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>

              {/* SLIDE 3: PLANCHADURÍA (Planchaduría Doña Mary) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 2 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-blue-400 block mb-2">
                    Servicios hogar
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    Planchaduría Doña Mary
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Planchado profesional por docena en prendas de vestir, camisas y uniformes escolares con almidón ligero y entrega protegida en ganchos. Recolección y entrega puntual a la puerta o caseta de tu coto.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550208?text=Hola%20Do%C3%B1a%20Mary,%20tengo%20ropa%20para%20planchar%20en%20mi%20coto"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550208"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "Planchaduría Doña Mary",
                        address: "Coto Roble Casa 24 / Servicio en toda la zona Natura",
                        note: "Recolección y entrega sin costo adicional en cotos",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>

              {/* SLIDE 4: CARWASH (AquaWash Detallado en Cochera) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 3 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1601362840469-51e4d8d58785?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-teal-400 block mb-2">
                    Servicios hogar
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    AquaWash Detallado en Cochera
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Lavado automotriz en seco, abrillantado, encerado cerámico y aspirado profundo de tapicería en la cochera de tu casa. Cuidamos la pintura de tu auto sin usar gasolina ni gastar agua comunitaria.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550103?text=Hola%20AquaWash,%20quiero%20agendar%20un%20lavado%20en%20mi%20cochera"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550103"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "AquaWash Detallado en Cochera",
                        address: "Servicio móvil a domicilio en todos los cotos Natura",
                        note: "Llegamos con equipo autónomo y productos biodegradables",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>

              {/* SLIDE 5: PIZZAS A LA LEÑA (Pizzas a la Leña La Cantera) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 4 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-orange-400 block mb-2">
                    Comida & Delivery
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    Pizzas a la Leña La Cantera
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Pizzas rústicas horneadas al momento en horno de piedra con masa madre de fermentación lenta de 48 horas, salsa de tomate San Marzano y quesos artesanales fundidos. Crujientes y calientitas hasta tu mesa.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550105?text=Hola%20Pizzas%20La%20Cantera,%20quiero%20hacer%20un%20pedido%20a%20domicilio"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550105"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "Pizzas a la Leña La Cantera",
                        address: "Prol. Mariano Otero esq. Las Rosas",
                        note: "Horno de piedra rústico con entrega a caseta de cotos",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>

              {/* SLIDE 6: AGENTE DE BIENES RAÍCES (Valeria Rivas Asesoría Inmobiliaria) */}
              <div
                className={`absolute inset-0 p-8 sm:p-14 lg:p-16 flex flex-col justify-between transition-opacity duration-700 bg-cover bg-center text-white ${
                  currentSlide === 5 ? "opacity-100 z-10" : "opacity-0 pointer-events-none z-0"
                }`}
                style={{
                  backgroundImage:
                    "linear-gradient(to right, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.8) 50%, rgba(15, 23, 42, 0.45) 100%), url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1920&q=80')",
                }}
              >
                <div>
                  <span className="text-xs sm:text-sm font-extrabold uppercase tracking-widest text-indigo-400 block mb-2">
                    Servicios profesionales
                  </span>
                </div>

                <div className="max-w-3xl space-y-4 py-4 z-10">
                  <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                    Valeria Rivas Asesoría Inmobiliaria
                  </h2>
                  <p className="text-sm sm:text-lg text-slate-200 font-normal leading-relaxed max-w-2xl">
                    Especialista en compra, venta y arrendamiento de casas residenciales en cotos de Mariano Otero y El Fortín. Valuación comercial certificada sin costo para vecinos, trámites notariales seguros y asesoría hipotecaria.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 z-10 pt-4 border-t border-white/15">
                  <a
                    href="https://wa.me/523315550209?text=Hola%20Valeria,%20me%20interesa%20asesor%C3%ADa%20inmobiliaria%20en%20Natura"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2.5 px-6 sm:px-8 py-3.5 sm:py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm sm:text-base shadow-xl transition-all active:scale-95"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Haz tu pedido por WhatsApp</span>
                  </a>
                  <a
                    href="tel:+523315550209"
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <Phone className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Llamar</span>
                  </a>
                  <button
                    onClick={() =>
                      setLocationModalData({
                        isOpen: true,
                        name: "Valeria Rivas Asesoría Inmobiliaria",
                        address: "Prol. Mariano Otero #4500 (Oficina Coto Encino)",
                        note: "Atención presencial en cotos de la zona previa cita",
                        copied: false,
                      })
                    }
                    className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 sm:py-4 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm sm:text-base border border-white/20 backdrop-blur-md transition-all shadow-sm active:scale-95"
                  >
                    <MapPin className="w-4 h-4 text-emerald-300 stroke-[2.2]" />
                    <span>Ver ubicación</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Barra inferior del Slider */}
            <div className="px-6 sm:px-10 py-4 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between text-xs text-slate-300">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setCurrentSlide((prev) => (prev - 1 + 6) % 6)}
                  className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setCurrentSlide((prev) => (prev + 1) % 6)}
                  className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
                <span className="font-mono text-slate-400 ml-2">{currentSlide + 1} de 6</span>
              </div>

              {/* Indicadores Apple-style (6 slides) */}
              <div className="flex items-center gap-2">
                {[0, 1, 2, 3, 4, 5].map((idx) => (
                  <button
                    key={idx}
                    onClick={() => setCurrentSlide(idx)}
                    className={`h-1.5 rounded-full transition-all ${
                      currentSlide === idx ? "w-8 bg-emerald-400" : "w-3 bg-slate-700 hover:bg-slate-600"
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* 2. EXPLORAR CATEGORÍAS (ENLACE A PÁGINAS INDEPENDIENTES) */}
        <section id="seccion-categorias" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 px-1">
              <div>
                <h3 className="text-xs font-black uppercase tracking-widest text-slate-500">
                  EXPLORAR CATEGORÍAS
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Encuentra comercios, servicios y delivery hiperlocal clasificado en cotos de Natura y Prolongación Mariano Otero
                </p>
              </div>
              <span className="text-xs text-emerald-800 font-bold self-start sm:self-auto bg-emerald-50 px-3 py-1 rounded-full border border-emerald-300">
                12 Categorías Activas
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
              {[
                { id: "atencion-medica", label: "Atención médica", hoverBorder: "hover:border-teal-500", textHover: "group-hover:text-teal-600", bg: "bg-gradient-to-br from-teal-50 via-teal-50/70 to-teal-100/60 border border-teal-200/70 text-teal-600 shadow-teal-500/10" },
                { id: "clases-particulares", label: "Clases particulares", hoverBorder: "hover:border-indigo-500", textHover: "group-hover:text-indigo-600", bg: "bg-gradient-to-br from-indigo-50 via-indigo-50/70 to-indigo-100/60 border border-indigo-200/70 text-indigo-600 shadow-indigo-500/10" },
                { id: "comida-delivery", label: "Comida y Delivery", hoverBorder: "hover:border-orange-500", textHover: "group-hover:text-orange-600", bg: "bg-gradient-to-br from-orange-50 via-orange-50/70 to-orange-100/60 border border-orange-200/70 text-orange-600 shadow-orange-500/10" },
                { id: "escuelas", label: "Escuelas", hoverBorder: "hover:border-blue-500", textHover: "group-hover:text-blue-600", bg: "bg-gradient-to-br from-blue-50 via-blue-50/70 to-blue-100/60 border border-blue-200/70 text-blue-600 shadow-blue-500/10" },
                { id: "farmacias", label: "Farmacias", hoverBorder: "hover:border-emerald-500", textHover: "group-hover:text-emerald-600", bg: "bg-gradient-to-br from-emerald-50 via-emerald-50/70 to-emerald-100/60 border border-emerald-200/70 text-emerald-600 shadow-emerald-500/10" },
                { id: "fitness", label: "Fitness", hoverBorder: "hover:border-cyan-500", textHover: "group-hover:text-cyan-600", bg: "bg-gradient-to-br from-cyan-50 via-cyan-50/70 to-cyan-100/60 border border-cyan-200/70 text-cyan-600 shadow-cyan-500/10" },
                { id: "hogar", label: "Hogar", hoverBorder: "hover:border-teal-600", textHover: "group-hover:text-teal-700", bg: "bg-gradient-to-br from-emerald-50 via-teal-50/70 to-teal-100/60 border border-teal-200/70 text-teal-700 shadow-teal-500/10" },
                { id: "mascotas", label: "Mascotas", hoverBorder: "hover:border-amber-500", textHover: "group-hover:text-amber-600", bg: "bg-gradient-to-br from-amber-50 via-amber-50/70 to-amber-100/60 border border-amber-200/70 text-amber-600 shadow-amber-500/10" },
                { id: "postres-cafe", label: "Postres y café", hoverBorder: "hover:border-rose-500", textHover: "group-hover:text-rose-600", bg: "bg-gradient-to-br from-rose-50 via-rose-50/70 to-rose-100/60 border border-rose-200/70 text-rose-600 shadow-rose-500/10" },
                { id: "productos-artesanales", label: "Productos artesanales", hoverBorder: "hover:border-purple-500", textHover: "group-hover:text-purple-600", bg: "bg-gradient-to-br from-purple-50 via-purple-50/70 to-purple-100/60 border border-purple-200/70 text-purple-600 shadow-purple-500/10" },
                { id: "servicios-hogar", label: "Servicios hogar", hoverBorder: "hover:border-blue-600", textHover: "group-hover:text-blue-700", bg: "bg-gradient-to-br from-blue-50 via-blue-50/70 to-blue-100/60 border border-blue-200/70 text-blue-700 shadow-blue-500/10" },
                { id: "veterinarias", label: "Veterinarias", hoverBorder: "hover:border-red-500", textHover: "group-hover:text-red-600", bg: "bg-gradient-to-br from-red-50 via-red-50/70 to-red-100/60 border border-red-200/70 text-red-600 shadow-red-500/10" },
              ].map((cat) => {
                return (
                  <Link
                    key={cat.id}
                    href={`/categoria/${cat.id}`}
                    className={`p-4 rounded-2xl bg-white border border-slate-200 ${cat.hoverBorder} hover:shadow-md transition-all text-center flex flex-col items-center justify-between group min-h-[128px]`}
                  >
                    <div className={`w-12 h-12 sm:w-14 sm:h-14 rounded-2xl flex items-center justify-center mb-2 group-hover:scale-110 group-hover:shadow-md transition-all shadow-xs ${cat.bg}`}>
                      <AbstractCategoryIcon id={cat.id} className="w-7 h-7 transition-transform group-hover:scale-110 duration-200" />
                    </div>
                    <span className={`text-xs font-bold text-slate-800 ${cat.textHover} leading-tight`}>
                      {cat.label}
                    </span>
                    <span className="text-[10px] text-slate-400 font-semibold mt-1">
                      Ver negocios →
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>

        {/* 3. BANNERS DESTACADOS: CULTURA NATURA Y COMUNIDAD NATURA */}
        <section id="seccion-banners-comunitarios" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
            {/* BANNER 1: CULTURA NATURA */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-amber-950 via-slate-950 to-slate-900 border border-amber-900/40 p-8 sm:p-10 text-white shadow-xl flex flex-col justify-between group hover:border-amber-500/50 transition-all">
              <div className="absolute -right-12 -top-12 w-48 h-48 rounded-full bg-amber-500/15 blur-2xl pointer-events-none group-hover:bg-amber-500/25 transition-all" />

              <div className="relative z-10 space-y-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-[11px] font-mono font-extrabold uppercase tracking-wider border border-amber-400/40">
                    <Palette className="w-3.5 h-3.5" />
                    <span>CASA DE LA CULTURA · PARQUE CENTRAL</span>
                  </span>
                  <span className="text-[11px] font-bold text-amber-400/80 bg-white/5 px-2.5 py-0.5 rounded-full border border-white/10">
                    Cartelera Abierta
                  </span>
                </div>

                <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-snug">
                  Cultura Natura
                </h3>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Talleres infantiles de barro, cine vecinal bajo las estrellas, danza y conciertos acústicos al aire libre en el Kiosco y Explanada Verde del Parque Central.
                </p>
              </div>

              <div className="relative z-10 pt-6 mt-6 border-t border-white/10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <span className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Eventos familiares y talleres gratuitos</span>
                </span>
                <Link
                  href="/cultura-natura"
                  className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs transition-all shadow-md active:scale-95"
                >
                  <span>Ver Cartelera Cultural</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* BANNER 2: COMUNIDAD NATURA */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-950 via-slate-950 to-slate-900 border border-blue-900/40 p-8 sm:p-10 text-white shadow-xl flex flex-col justify-between group hover:border-blue-500/50 transition-all">
              <div className="absolute -right-12 -top-12 w-48 h-48 rounded-full bg-blue-500/15 blur-2xl pointer-events-none group-hover:bg-blue-500/25 transition-all" />

              <div className="relative z-10 space-y-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-[11px] font-mono font-extrabold uppercase tracking-wider border border-blue-400/40">
                    <Megaphone className="w-3.5 h-3.5" />
                    <span>CANAL VECINAL · AVISOS EN COTOS</span>
                  </span>
                  <span className="text-[11px] font-bold text-blue-400/80 bg-white/5 px-2.5 py-0.5 rounded-full border border-white/10">
                    Enlace Directo
                  </span>
                </div>

                <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-snug">
                  Comunidad Natura
                </h3>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Muro vecinal para reporte urgente de mascotas extraviadas, comunicados de comités de colonos, ofertas de empleo local y causas solidarias de nuestra zona.
                </p>
              </div>

              <div className="relative z-10 pt-6 mt-6 border-t border-white/10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <span className="text-xs font-semibold text-blue-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Contacto directo entre residentes por WhatsApp</span>
                </span>
                <Link
                  href="/comunidad-natura"
                  className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs transition-all shadow-md active:scale-95"
                >
                  <span>Ir a Avisos Vecinales</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* 6. BANNER DE CIERRE COMERCIAL: VENDEMOS PUBLICIDAD PAPI */}
        <section id="anunciate" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="rounded-3xl bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 text-white p-8 sm:p-12 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 border border-slate-800">
            <div className="space-y-2 max-w-xl">
              <span className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-bold">
                VENDEMOS PUBLICIDAD PAPI
              </span>
              <h3 className="text-2xl sm:text-3xl font-black tracking-tight leading-snug">
                ¿Quieres que tu negocio esté en el Slider Gigante del inicio?
              </h3>
              <p className="text-xs sm:text-sm text-slate-300">
                Aparece en el billboard principal que ven todos los residentes al ingresar. Campañas mensuales con link directo a WhatsApp y llamadas telefónicas.
              </p>
            </div>
            <a
              href="https://wa.me/523315550000?text=Hola,%20me%20interesa%20contratar%20el%20Slider%20Gigante%20en%20Epicentro%20Natura"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-6 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-sm shadow-lg transition-all active:scale-95 shrink-0"
            >
              <Sparkles className="w-4 h-4" />
              <span>Contratar Slider Publicitario</span>
            </a>
          </div>
        </section>
      </main>

      {/* FOOTER LIMPIO */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-10 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
              <Trees className="w-4 h-4" />
            </div>
            <strong className="text-slate-900 font-bold">Epicentro Natura</strong>
            <span>·</span>
            <span>Prolongación Mariano Otero, Zapopan, Jalisco</span>
          </div>
          <p>© 2026 Plataforma Hiperlocal Comunitaria. Ecosistema digital Hipha.</p>
        </div>
      </footer>

      {/* MODAL DE UBICACIÓN */}
      {locationModalData.isOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-800 flex items-center justify-center">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                </div>
                <span className="text-xs font-black uppercase tracking-wider text-emerald-600">
                  Ubicación y Cobertura
                </span>
              </div>
              <button
                onClick={() => setLocationModalData((prev) => ({ ...prev, isOpen: false }))}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-5 space-y-3">
              <h3 className="text-lg font-black text-slate-900 leading-tight">{locationModalData.name}</h3>
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-1">
                <span className="text-[10px] font-extrabold uppercase tracking-wide text-slate-500">
                  Dirección o Punto de Entrega:
                </span>
                <p className="text-sm font-semibold text-slate-800 leading-snug">{locationModalData.address}</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-emerald-800 font-semibold">
                <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{locationModalData.note}</span>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
              <button
                onClick={() => setLocationModalData((prev) => ({ ...prev, isOpen: false }))}
                className="w-1/3 py-3 px-4 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 transition-all text-center"
              >
                Cerrar
              </button>
              <div className="flex items-center gap-2 w-2/3">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(locationModalData.address);
                    setLocationModalData((prev) => ({ ...prev, copied: true }));
                    setTimeout(() => {
                      setLocationModalData((prev) => ({ ...prev, copied: false }));
                    }, 2500);
                  }}
                  className="w-1/2 py-3 px-2 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-bold hover:bg-emerald-100 transition-all flex items-center justify-center gap-1.5"
                >
                  <Copy className="w-4 h-4" />
                  <span>{locationModalData.copied ? "¡Copiado!" : "Copiar"}</span>
                </button>
                <a
                  href={`https://maps.google.com/?q=${encodeURIComponent(
                    locationModalData.name + " " + locationModalData.address
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-1/2 py-3 px-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Maps</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TOAST DE GEOLOCALIZACIÓN */}
      {geoToast && (
        <div
          className={`fixed bottom-5 right-5 z-50 max-w-sm px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 text-xs font-bold transition-all duration-300 transform translate-y-0 opacity-100 ${
            geoToast.isSuccess
              ? "bg-slate-900 text-white border border-emerald-500 shadow-emerald-950/20"
              : "bg-red-900 text-white border border-red-500"
          }`}
        >
          <div
            className={`w-6 h-6 rounded-lg ${
              geoToast.isSuccess ? "bg-emerald-600" : "bg-red-600"
            } text-white flex items-center justify-center shrink-0`}
          >
            {geoToast.isSuccess ? <MapPin className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
          </div>
          <span>{geoToast.message}</span>
        </div>
      )}
    </div>
  );
}
