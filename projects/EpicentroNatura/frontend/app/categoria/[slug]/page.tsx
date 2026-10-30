"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
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
  ChevronRight,
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
  X,
  Copy,
  ExternalLink,
  Crosshair,
  ArrowLeft,
  ShieldCheck,
  CheckCircle,
} from "lucide-react";
import { BusinessType } from "@/types";
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
  cta_type: "whatsapp_order" | "service_whatsapp" | "call_and_whatsapp";
  description: string;
}

const ALL_CATEGORIES = [
  {
    slug: "atencion-medica",
    name: "Atención médica",
    icon: Stethoscope,
    bg: "bg-gradient-to-br from-teal-50 via-teal-50/70 to-teal-100/60 border border-teal-200/70 text-teal-600 shadow-teal-500/10",
    h1: "Atención Médica, Dental y Consultorios en Mariano Otero",
    desc: "Médicos generales, odontología preventiva, ortodoncia y pediatría con consultorios ubicados en las plazas de ingreso a cotos.",
    seo: "Profesionales de la salud cerca de tu hogar en Prolongación Mariano Otero.",
  },
  {
    slug: "clases-particulares",
    name: "Clases particulares",
    icon: GraduationCap,
    bg: "bg-gradient-to-br from-indigo-50 via-indigo-50/70 to-indigo-100/60 border border-indigo-200/70 text-indigo-600 shadow-indigo-500/10",
    h1: "Clases Particulares, Regularización y Talleres en Natura",
    desc: "Profesores de matemáticas, inglés, yoga en terraza y regularización escolar para niños y jóvenes residentes de cotos.",
    seo: "Aprende cerca de casa con maestros residentes en la zona.",
  },
  {
    slug: "comida-delivery",
    name: "Comida y Delivery",
    icon: Utensils,
    bg: "bg-gradient-to-br from-orange-50 via-orange-50/70 to-orange-100/60 border border-orange-200/70 text-orange-600 shadow-orange-500/10",
    h1: "Comida y Delivery en Natura Bosque Residencial & Mariano Otero",
    desc: "Taquerías, pizzas a la leña de masa madre, hamburguesas rústicas y comida con entrega a caseta de cotos en Natura, Los Robles y El Fortín.",
    seo: "Encuentra la mejor oferta gastronómica local en Prolongación Mariano Otero con entrega limpia directa a caseta de cotos.",
  },
  {
    slug: "escuelas",
    name: "Escuelas",
    icon: GraduationCap,
    bg: "bg-gradient-to-br from-blue-50 via-blue-50/70 to-blue-100/60 border border-blue-200/70 text-blue-600 shadow-blue-500/10",
    h1: "Escuelas, Colegios y Estancias Infantiles en Mariano Otero",
    desc: "Colegios bilingües, preescolar, primaria, secundaria y preparatoria con metodología activa y rutas escolares seguras en cotos.",
    seo: "Encuentra la mejor opción educativa cerca de tu hogar en Prolongación Mariano Otero.",
  },
  {
    slug: "farmacias",
    name: "Farmacias",
    icon: Pill,
    bg: "bg-gradient-to-br from-emerald-50 via-emerald-50/70 to-emerald-100/60 border border-emerald-200/70 text-emerald-600 shadow-emerald-500/10",
    h1: "Farmacias y Medicamentos 24 Horas en Mariano Otero",
    desc: "Farmacias con servicio 24 horas, toma de presión, curaciones menores y entrega de medicamentos a cotos sobre Prolongación Mariano Otero.",
    seo: "Farmacias cercanas a Natura Bosque Residencial con surtido de recetas y medicamentos de patente.",
  },
  {
    slug: "fitness",
    name: "Fitness",
    icon: Dumbbell,
    bg: "bg-gradient-to-br from-cyan-50 via-cyan-50/70 to-cyan-100/60 border border-cyan-200/70 text-cyan-600 shadow-cyan-500/10",
    h1: "Fitness, Gimnasios y Entrenadores Personales en Natura",
    desc: "Gimnasios boutique, entrenamiento funcional HIIT, calistenia, pilates reformer y coaches a domicilio en cotos de Mariano Otero.",
    seo: "Actívate sin salir de la zona con entrenadores y gimnasios locales.",
  },
  {
    slug: "hogar",
    name: "Hogar",
    icon: Home,
    bg: "bg-gradient-to-br from-emerald-50 via-teal-50/70 to-teal-100/60 border border-teal-200/70 text-teal-700 shadow-teal-500/10",
    h1: "Hogar, Persianas, Canceles y Jardinería en Mariano Otero",
    desc: "Fabricación de persianas, canceles de baño, toldos retráctiles, plantas de ornato, pasto en rollo y paisajismo para casas de cotos.",
    seo: "Mejora y decora tu casa en cotos residenciales con persianerías y viveros locales.",
  },
  {
    slug: "mascotas",
    name: "Mascotas",
    icon: Dog,
    bg: "bg-gradient-to-br from-amber-50 via-amber-50/70 to-amber-100/60 border border-amber-200/70 text-amber-600 shadow-amber-500/10",
    h1: "Alimentos, Accesorios y Estética Canina en Natura",
    desc: "Tiendas de mascotas, croquetas premium, baño y estética canina profesional con servicio de recogida y entrega en cotos de la zona.",
    seo: "Todo para tu mejor amigo en Natura Bosque Residencial y cotos vecinos.",
  },
  {
    slug: "postres-cafe",
    name: "Postres y café",
    icon: Coffee,
    bg: "bg-gradient-to-br from-rose-50 via-rose-50/70 to-rose-100/60 border border-rose-200/70 text-rose-600 shadow-rose-500/10",
    h1: "Pastelería Artesanal, Postres y Café en Cotos Natura",
    desc: "Pasteles de zanahoria, pays de frutos rojos, galletas chispas recién horneadas y café de especialidad para disfrutar en casa.",
    seo: "Emprendimientos reposteros y café gourmet en cotos residenciales de Mariano Otero.",
  },
  {
    slug: "productos-artesanales",
    name: "Productos artesanales",
    icon: Sparkles,
    bg: "bg-gradient-to-br from-purple-50 via-purple-50/70 to-purple-100/60 border border-purple-200/70 text-purple-600 shadow-purple-500/10",
    h1: "Productos Artesanales y Botica Natural de la Zona",
    desc: "Miel pura de floración de la primavera, jabones botánicos en barra, velas de cera de soya y cosmética natural elaborada por vecinas.",
    seo: "Consume local con productos hechos a mano en las faldas del Bosque La Primavera.",
  },
  {
    slug: "servicios-hogar",
    name: "Servicios hogar",
    icon: Wrench,
    bg: "bg-gradient-to-br from-blue-50 via-blue-50/70 to-blue-100/60 border border-blue-200/70 text-blue-700 shadow-blue-500/10",
    h1: "Mantenimiento del Hogar, Planchaduría y Limpieza en Cotos",
    desc: "Planchaduría por docena, electricistas residenciales certificados, lavado ecológico de autos y técnicos de confianza en cotos.",
    seo: "Servicios para el hogar en Mariano Otero y cotos Natura.",
  },
  {
    slug: "veterinarias",
    name: "Veterinarias",
    icon: HeartPulse,
    bg: "bg-gradient-to-br from-red-50 via-red-50/70 to-red-100/60 border border-red-200/70 text-red-600 shadow-red-500/10",
    h1: "Clínicas Veterinarias y Urgencias en Natura Bosque Residencial",
    desc: "Consultas médicas veterinarias, vacunas, desparasitaciones, cirugías menores y atención de urgencias para perros y gatos.",
    seo: "Atención veterinaria integral y responsable para mascotas en cotos de Zapopan.",
  },
];

const ALL_BUSINESSES: CommercialBusiness[] = [
  // 1. Comida
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
    description: "Tacos y costras de suadero, pastor con piña asada al carbón, carnaza, arrachera, pancita y tripita dorada.",
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
    description: "Pizzas rústicas horneadas al momento en horno de piedra con masa madre fermentada 48 horas y salsa San Marzano.",
  },
  // 2. Farmacias
  {
    id: "b3",
    name: "Farmacia Mariano Otero 24 Horas",
    category_slug: "farmacias",
    category_label: "Farmacias",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prol. Mariano Otero #4500 (Frente al ingreso Coto Encino)",
    community_slug: "punta-de-otero",
    community_name: "Punta de Otero",
    phone: "33 1555 0201",
    whatsapp: "+523315550201",
    hours: "Abierto 24 Horas · Lunes a Domingo",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Reparto limpio en bici de carga a casetas de cotos",
    cta_type: "call_and_whatsapp",
    description: "Medicamentos genéricos y de patente, curaciones menores, toma de presión y surtido de recetas.",
  },
  // 3. Mascotas
  {
    id: "b4",
    name: "Pet Shop & Estética Canina Natura",
    category_slug: "mascotas",
    category_label: "Mascotas",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Plaza Natura Local 3 (Prol. Mariano Otero #4250)",
    community_slug: "los-robles",
    community_name: "Los Robles",
    phone: "33 1555 0206",
    whatsapp: "+523315550206",
    hours: "Lunes a Sábado · 09:00 a 19:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Recogida y entrega de mascotas en carrito eléctrico",
    cta_type: "whatsapp_order",
    description: "Alimentos súper premium, accesorios, premios naturales y baño con secado profesional.",
  },
  // 4. Postres
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
    description: "Pasteles de zanahoria, pays de frutos rojos, galletas chispas y brownies artesanales.",
  },
  // 5. Artesanales
  {
    id: "b6",
    name: "Miel & Jabones Artesanales del Bosque",
    category_slug: "productos-artesanales",
    category_label: "Productos artesanales",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Natura Bosque Residencial (Coto Ceiba casa 14)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0102",
    whatsapp: "+523315550102",
    hours: "Lunes a Sábado · 10:00 a 18:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Cosecha local y entrega peatonal entre cotos",
    cta_type: "whatsapp_order",
    description: "Miel pura 100% de abeja de la Primavera, propóleo, jabones de avena, romero y lavanda.",
  },
  // 6. Servicios hogar
  {
    id: "b7",
    name: "Planchaduría y Tintorería Doña Mary",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prol. Mariano Otero #4300 (Plaza Ceiba)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0203",
    whatsapp: "+523315550203",
    hours: "Lunes a Viernes · 08:30 a 19:30 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "whatsapp_order",
    description: "Servicio de planchaduría profesional por docena, tintorería y almidonado de camisas.",
  },
  {
    id: "b8",
    name: "AquaWash Carwash Ecológico a Domicilio",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Atención directa en la cochera de tu coto",
    community_slug: "bosque-primavera",
    community_name: "Bosque de la primavera",
    phone: "33 1555 0103",
    whatsapp: "+523315550103",
    hours: "Lunes a Domingo con cita previa",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Lavado en seco sin uso de mangueras ni emisiones",
    cta_type: "service_whatsapp",
    description: "Lavado de autos en seco en tu cochera con polímeros biodegradables que cuidan el agua.",
  },
  {
    id: "b10",
    name: "Electricista y Mantenimiento Morales",
    category_slug: "servicios-hogar",
    category_label: "Servicios hogar",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Servicio a domicilio en todos los cotos",
    community_slug: "el-fortin",
    community_name: "El Fortín",
    phone: "33 1555 0208",
    whatsapp: "+523315550208",
    hours: "Lunes a Sábado · Urgencias 24h",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "service_whatsapp",
    description: "Instalaciones eléctricas 110V/220V, balanceo de cargas, bombas presurizadoras y cortos.",
  },
  // 7. Atención Médica
  {
    id: "b9",
    name: "Consultorio Médico y Dental Dra. Carmen",
    category_slug: "atencion-medica",
    category_label: "Atención médica",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Plaza Coto Encino Local 2 (Prol. Mariano Otero #4480)",
    community_slug: "punta-de-otero",
    community_name: "Punta de Otero",
    phone: "33 1555 0204",
    whatsapp: "+523315550204",
    hours: "Lunes a Sábado · 09:00 a 20:00 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "call_and_whatsapp",
    description: "Medicina general, odontología preventiva, resinas, limpiezas y blanqueamiento dental.",
  },
  // 8. Veterinarias
  {
    id: "b11",
    name: "Veterinaria Huellitas Natura",
    category_slug: "veterinarias",
    category_label: "Veterinarias",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prol. Mariano Otero #4280 (Plaza Olivo)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0207",
    whatsapp: "+523315550207",
    hours: "Abierto hoy · 09:00 a 20:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Atención de urgencia a pie y bici a cotos cercanos",
    cta_type: "call_and_whatsapp",
    description: "Consultas médicas veterinarias, vacunas, desparasitaciones y cirugías menores.",
  },
  // 9. Clases particulares
  {
    id: "b12",
    name: "Profesor de Matemáticas e Inglés Coto Ceiba",
    category_slug: "clases-particulares",
    category_label: "Clases particulares",
    type_slug: "servicios_profesionales",
    type_label: "Servicios profesionales",
    address: "Natura Bosque Residencial (Coto Ceiba)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0205",
    whatsapp: "+523315550205",
    hours: "Lunes a Viernes · 15:00 a 20:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Profesor residente en el coto; desplazamiento a pie",
    cta_type: "service_whatsapp",
    description: "Clases particulares de regularización en matemáticas, álgebra, física e inglés.",
  },
  // 10. Fitness
  {
    id: "b14",
    name: "VitalFit Studio Natura",
    category_slug: "fitness",
    category_label: "Fitness",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Av. Prolongación Mariano Otero #4350 (Plaza Coto Ceiba)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0310",
    whatsapp: "+523315550310",
    hours: "Lunes a Viernes · 06:00 a 22:00 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "call_and_whatsapp",
    description: "Gimnasio boutique, entrenamiento funcional HIIT, pilates reformer y asesoría deportiva.",
  },
  {
    id: "b15",
    name: "Coach David - Entrenamiento Cero Emisiones",
    category_slug: "fitness",
    category_label: "Fitness",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Atención a domicilio en áreas verdes de cotos",
    community_slug: "los-robles",
    community_name: "Los Robles",
    phone: "33 1555 0311",
    whatsapp: "+523315550311",
    hours: "Lunes a Sábado · 06:30 a 19:30 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Desplazamiento 100% en bicicleta entre cotos",
    cta_type: "service_whatsapp",
    description: "Entrenador personal a domicilio en cotos Natura, Los Robles y El Fortín. Calistenia y acondicionamiento.",
  },
  // 11. Escuelas
  {
    id: "b16",
    name: "Instituto Tepeyac Campus Mariano Otero",
    category_slug: "escuelas",
    category_label: "Escuelas",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Prolongación Mariano Otero #4200 (Frente al corredor residencial)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0320",
    whatsapp: "+523315550320",
    hours: "Lunes a Viernes · 07:00 a 17:00 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "call_and_whatsapp",
    description: "Educación bilingüe desde Maternal hasta Preparatoria. Vanguardia pedagógica, canchas deportivas, laboratorios y transporte escolar en cotos.",
  },
  {
    id: "b17",
    name: "Colegio Finlandés - Campus Bosque",
    category_slug: "escuelas",
    category_label: "Escuelas",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Av. Los Robles #310 (Ingreso fraccionamiento)",
    community_slug: "los-robles",
    community_name: "Los Robles",
    phone: "33 1555 0321",
    whatsapp: "+523315550321",
    hours: "Lunes a Viernes · 07:30 a 16:00 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Rutas seguras peatonales y ciclistas para alumnos de coto",
    cta_type: "call_and_whatsapp",
    description: "Metodología activa nórdica centrada en el bienestar infantil, bilingüe, aulas al aire libre frente al bosque, Preescolar y Primaria.",
  },
  // 12. Hogar
  {
    id: "b18",
    name: "Persianas, Toldos & Cancelería Natura",
    category_slug: "hogar",
    category_label: "Hogar",
    type_slug: "local_establecido",
    type_label: "Local establecido",
    address: "Plaza Natura Local 5 (Prolongación Mariano Otero)",
    community_slug: "natura-bosque-residencial",
    community_name: "Natura Bosque Residencial",
    phone: "33 1555 0330",
    whatsapp: "+523315550330",
    hours: "Lunes a Sábado · 09:00 a 19:00 hrs",
    is_open_now: true,
    has_km0_badge: false,
    km0_reason: null,
    cta_type: "service_whatsapp",
    description: "Fabricación e instalación de persianas sheer elegance, blackout, toldos retráctiles, mosquiteros y canceles de baño en cristal templado para casas de coto.",
  },
  {
    id: "b19",
    name: "Vivero & Jardines Paisajismo Bosque Vivo",
    category_slug: "hogar",
    category_label: "Hogar",
    type_slug: "emprendimiento",
    type_label: "Emprendimiento (solo entrega a domicilio)",
    address: "Luna Bosque Coto 2 casa 18 (Vivero demostrativo)",
    community_slug: "luna-bosque",
    community_name: "Luna Bosque",
    phone: "33 1555 0331",
    whatsapp: "+523315550331",
    hours: "Lunes a Domingo · 09:00 a 18:30 hrs",
    is_open_now: true,
    has_km0_badge: true,
    km0_reason: "Traslado ecológico en bici de carga sin emisiones",
    cta_type: "whatsapp_order",
    description: "Plantas de ornato, pasto en rollo, suculentas, macetas de autor y mantenimiento de jardinería para cocheras y terrazas en cotos privados.",
  },
];

export default function CategoryPage() {
  const params = useParams();
  const rawSlug = (params?.slug as string) || "comida-delivery";

  const [currentCategory, setCurrentCategory] = useState(
    ALL_CATEGORIES.find((c) => c.slug === rawSlug) || ALL_CATEGORIES[0]
  );
  const [selectedType, setSelectedType] = useState<string>("all");
  const [isKm0Active, setIsKm0Active] = useState<boolean>(false);
  const [selectedCommunity, setSelectedCommunity] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [locationModalData, setLocationModalData] = useState<{
    isOpen: boolean;
    name: string;
    address: string;
    scope: string;
  }>({
    isOpen: false,
    name: "",
    address: "",
    scope: "",
  });

  const [copiedAddress, setCopiedAddress] = useState(false);

  useEffect(() => {
    const found = ALL_CATEGORIES.find((c) => c.slug === rawSlug);
    if (found) {
      setCurrentCategory(found);
    }
  }, [rawSlug]);

  const filteredBusinesses = ALL_BUSINESSES.filter((b) => {
    const matchCat =
      currentCategory.slug === "all" || b.category_slug === currentCategory.slug;
    const matchType = selectedType === "all" || b.type_slug === selectedType;
    const matchKm0 = !isKm0Active || b.has_km0_badge;
    const matchCommunity =
      selectedCommunity === "all" || b.community_slug === selectedCommunity;
    const matchQuery =
      !searchQuery ||
      b.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.address.toLowerCase().includes(searchQuery.toLowerCase());

    return matchCat && matchType && matchKm0 && matchCommunity && matchQuery;
  });

  const handleCopyAddress = (addr: string) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(addr);
      setCopiedAddress(true);
      setTimeout(() => setCopiedAddress(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased selection:bg-emerald-500 selection:text-white">
      {/* 1. TOP BAR */}
      <aside className="bg-slate-950 text-white text-xs py-2 px-4 border-b border-slate-800 text-center">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <span className="font-bold text-slate-200 tracking-wide text-xs sm:text-[13px]">
            Comunidad Epicentro Natura
          </span>
        </div>
      </aside>

      {/* 2. NAVBAR */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 sm:gap-4">
            <div className="w-full md:w-auto flex items-center justify-between gap-4">
              <Link href="/" className="flex items-center gap-2.5 group shrink-0">
                <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-gradient-to-tr from-emerald-800 to-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-600/20 group-hover:scale-105 transition-transform">
                  <Trees className="w-6 h-6 stroke-[2.2]" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-black tracking-tight text-slate-950">
                    Epicentro
                  </span>
                  <span className="text-[11px] font-extrabold lowercase tracking-wide px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                    natura
                  </span>
                </div>
              </Link>

              <Link
                href="/"
                className="inline-flex md:hidden items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 border border-slate-200"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Inicio</span>
              </Link>
            </div>

            {/* BUSCADOR */}
            <div className="w-full md:flex-1 md:max-w-2xl lg:max-w-3xl">
              <div className="relative flex items-center bg-slate-100 hover:bg-slate-200/70 focus-within:bg-white rounded-2xl border border-slate-200 focus-within:border-emerald-600 focus-within:ring-2 focus-within:ring-emerald-600/20 transition-all p-1.5 sm:p-2">
                <div className="pl-2.5 pr-2 text-emerald-600 shrink-0">
                  <Search className="w-4 h-4 sm:w-5 sm:h-5 stroke-[2.5]" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar en esta categoría..."
                  className="w-full bg-transparent text-xs sm:text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none pr-2"
                />

                <div className="relative shrink-0 border-l border-slate-300 pl-2 sm:pl-3 pr-1 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400" />
                  <select
                    value={selectedCommunity}
                    onChange={(e) => setSelectedCommunity(e.target.value)}
                    className="bg-transparent text-[11px] sm:text-xs font-bold text-slate-700 focus:outline-none cursor-pointer pr-4 appearance-none"
                  >
                    <option value="all">Toda la zona (Mariano Otero)</option>
                    <option value="natura-bosque-residencial">
                      Natura Bosque Residencial
                    </option>
                    <option value="los-robles">Los Robles</option>
                    <option value="bosque-primavera">Bosque de la primavera</option>
                    <option value="el-fortin">El Fortín</option>
                    <option value="luna-bosque">Luna Bosque</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-2">
              <Link
                href="/"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Volver al Inicio</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 3. MAIN CONTENT */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs font-medium text-slate-500 py-1">
          <Link href="/" className="hover:text-emerald-600 transition-colors">
            Inicio
          </Link>
          <ChevronRight className="w-3 h-3 text-slate-400" />
          <Link href="/#seccion-categorias" className="hover:text-emerald-600 transition-colors">
            Categorías
          </Link>
          <ChevronRight className="w-3 h-3 text-slate-400" />
          <span className="font-bold text-slate-900">{currentCategory.name}</span>
        </nav>

        {/* Hero Header de Categoría */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center gap-4">
            <div
              className={`w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${currentCategory.bg}`}
            >
              <AbstractCategoryIcon id={currentCategory.slug} className="w-9 h-9 sm:w-11 sm:h-11 transition-transform group-hover:scale-105" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-[11px] font-mono font-extrabold uppercase tracking-widest text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-300">
                  Directorio Especializado
                </span>
                <span className="text-[11px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                  {filteredBusinesses.length} negocio
                  {filteredBusinesses.length === 1 ? "" : "s"}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-950 tracking-tight leading-tight">
                {currentCategory.h1}
              </h1>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 max-w-3xl leading-relaxed">
                {currentCategory.desc}
              </p>
            </div>
          </div>
        </div>

        {/* Tira rápida de categorías */}
        <div className="space-y-2">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-extrabold uppercase tracking-widest text-slate-500">
              Explorar otras categorías
            </span>
          </div>
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {ALL_CATEGORIES.map((c) => {
              const isActive = c.slug === currentCategory.slug;
              return (
                <button
                  key={c.slug}
                  onClick={() => setCurrentCategory(c)}
                  className={`shrink-0 flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all border ${
                    isActive
                      ? "bg-slate-950 text-white border-slate-950 shadow-sm"
                      : "bg-white text-slate-700 border-slate-200 hover:border-emerald-600 hover:text-emerald-600"
                  }`}
                >
                  <AbstractCategoryIcon id={c.slug} className={`w-3.5 h-3.5 ${isActive ? "text-emerald-400" : ""}`} />
                  <span>{c.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Filtros por tipo de negocio y Km 0 */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {[
              { id: "all", label: "Toda la Oferta" },
              { id: "local_establecido", label: "🏪 Local establecido" },
              { id: "emprendimiento", label: "🛵 Emprendimiento (a domicilio)" },
              { id: "servicios_profesionales", label: "💼 Servicios profesionales" },
            ].map((tab) => {
              const active = selectedType === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedType(tab.id)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-extrabold border transition-all ${
                    active
                      ? "bg-slate-950 text-white border-slate-950 hover:bg-slate-800"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:text-emerald-600 hover:border-slate-300"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => setIsKm0Active(!isKm0Active)}
            className={`self-start md:self-auto inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold border transition-all ${
              isKm0Active
                ? "bg-emerald-600 text-white border-emerald-600"
                : "bg-white text-slate-700 border-slate-200 hover:border-emerald-600 hover:text-emerald-600"
            }`}
          >
            <Leaf className="w-3.5 h-3.5" />
            <span>Solo Distintivo Km 0 (0 Emisiones)</span>
          </button>
        </div>

        {/* Grid de Fichas Comerciales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          {filteredBusinesses.length === 0 ? (
            <div className="col-span-full bg-white rounded-3xl border border-slate-200 p-12 text-center">
              <Store className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h4 className="text-base font-bold text-slate-800">
                No hay negocios que coincidan con estos filtros
              </h4>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Prueba restableciendo los filtros o seleccionando otra categoría.
              </p>
              <button
                onClick={() => {
                  setSelectedType("all");
                  setIsKm0Active(false);
                  setSelectedCommunity("all");
                  setSearchQuery("");
                }}
                className="mt-4 px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold"
              >
                Restablecer Filtros
              </button>
            </div>
          ) : (
            filteredBusinesses.map((b) => {
              const waUrl = `https://wa.me/${b.whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(
                `Hola ${b.name}, vi su ficha en Epicentro Natura y me gustaría solicitar información.`
              )}`;

              return (
                <div
                  key={b.id}
                  className="p-6 rounded-3xl bg-white border border-slate-200 hover:border-emerald-600 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <span className="text-[11px] font-extrabold uppercase tracking-wide text-emerald-600">
                          {b.category_label}
                        </span>
                        <h3 className="text-lg font-black text-slate-950 group-hover:text-emerald-600 transition-colors leading-tight">
                          {b.name}
                        </h3>
                      </div>
                      {b.has_km0_badge && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          <Leaf className="w-3 h-3 text-emerald-600" />
                          <span>Km 0</span>
                        </span>
                      )}
                    </div>

                    <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 text-slate-700">
                      <span>{b.type_label}</span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed line-clamp-3">
                      {b.description}
                    </p>

                    <div className="pt-2 space-y-1.5 text-xs text-slate-500">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="truncate">{b.address}</span>
                        <button
                          onClick={() =>
                            setLocationModalData({
                              isOpen: true,
                              name: b.name,
                              address: b.address,
                              scope: `Cobertura en cotos de ${b.community_name}`,
                            })
                          }
                          className="text-emerald-600 hover:underline text-[11px] font-bold shrink-0 ml-auto"
                        >
                          Ver mapa
                        </button>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="text-emerald-700 font-semibold">{b.hours}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <a
                      href={waUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-all"
                    >
                      <MessageCircle className="w-4 h-4" />
                      <span>Haz tu pedido por WhatsApp</span>
                    </a>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Sección SEO Grounding */}
        <section className="mt-12 p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 text-emerald-800">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <h3 className="text-base sm:text-lg font-bold text-slate-900">
              Guía Local y Cobertura de Cotos
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            {currentCategory.seo} En Epicentro Natura impulsamos la economía hiperlocal conectando a
            residentes de cotos en Prolongación Mariano Otero con proveedores de confianza y
            entregas cero emisiones a casetas.
          </p>
        </section>
      </main>

      {/* MODAL DE UBICACIÓN */}
      {locationModalData.isOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 border border-slate-200 shadow-2xl relative">
            <button
              onClick={() =>
                setLocationModalData({ isOpen: false, name: "", address: "", scope: "" })
              }
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-900"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                <MapPin className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-950">
                  {locationModalData.name}
                </h3>
                <span className="text-xs font-bold text-emerald-600">
                  Ubicación & Cobertura Residencial
                </span>
              </div>
            </div>

            <div className="space-y-4 py-2">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Dirección Física o Referencia:
                </span>
                <p className="text-xs sm:text-sm font-semibold text-slate-800">
                  {locationModalData.address}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200">
                <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block mb-1">
                  Cobertura y Entrega en Cotos:
                </span>
                <p className="text-xs sm:text-sm font-medium text-emerald-950">
                  {locationModalData.scope}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  onClick={() => handleCopyAddress(locationModalData.address)}
                  className="py-3 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold border border-slate-200 flex items-center justify-center gap-1.5"
                >
                  <Copy className="w-4 h-4" />
                  <span>{copiedAddress ? "¡Copiado!" : "Copiar Dirección"}</span>
                </button>
                <a
                  href={`https://maps.google.com/?q=${encodeURIComponent(
                    `${locationModalData.name} ${locationModalData.address} Zapopan`
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="py-3 px-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-white text-xs font-bold flex items-center justify-center gap-1.5"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Google Maps</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
