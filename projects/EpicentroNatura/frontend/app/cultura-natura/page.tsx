"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Palette,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  ArrowLeft,
  Store,
  Megaphone,
  Tag,
  MessageCircle,
} from "lucide-react";

interface CulturalEvent {
  id: string;
  title: string;
  category: string;
  datetime: string;
  location: string;
  description: string;
  cost: string;
  badgeColor: string;
}

const CULTURAL_EVENTS: CulturalEvent[] = [
  {
    id: "c1",
    title: "Baile Trend & Ritmos Modernos",
    category: "Baile y Fitness",
    datetime: "Miércoles · 19:00 a 20:00 hrs",
    location: "Casa de la Cultura",
    description: "Clases dinámicas de ritmos urbanos, coreografías en tendencia y expresión corporal para jóvenes y adultos.",
    cost: "$60 MXN individual / $100 MXN pareja",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
  },
  {
    id: "c2",
    title: "Fútbol Infantil (Categoría 4 a 7 años)",
    category: "Deportes",
    datetime: "Viernes · 17:00 a 18:30 hrs",
    location: "Casa de la Cultura",
    description: "Iniciación formativa, coordinación motriz, desarrollo técnico de control de balón y compañerismo en equipo.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
  },
  {
    id: "c3",
    title: "Fútbol Infantil (Categoría 8 a 12 años)",
    category: "Deportes",
    datetime: "Viernes · 18:30 a 20:00 hrs",
    location: "Casa de la Cultura",
    description: "Entrenamiento táctico, fundamentos técnicos, resistencia física y partidos de práctica formativos.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
  },
  {
    id: "c4",
    title: "Fotografía Básica",
    category: "Arte y Música",
    datetime: "Viernes · 17:00 a 18:00 hrs",
    location: "Casa de la Cultura",
    description: "Aprende encuadre, iluminación, composición visual y manejo de cámara o smartphone en sesiones teórico-prácticas.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
  },
  {
    id: "c5",
    title: "Latin Fit & Acondicionamiento Físico",
    category: "Baile y Fitness",
    datetime: "Martes y Jueves · 08:00 a 09:00 hrs",
    location: "Casa de la Cultura",
    description: "Activación física matutina al ritmo de música latina, cardio, tonificación muscular y movilidad articular.",
    cost: "$50 MXN por sesión",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
  },
  {
    id: "c6",
    title: "Meditación & Sesiones de Respiración",
    category: "Bienestar",
    datetime: "Sábados · 10:00 a 11:30 hrs",
    location: "Casa de la Cultura",
    description: "Sesión de relajación guiada, técnicas de respiración consciente (pranayama) y mindfulness para reducir el estrés.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-cyan-100 text-cyan-800 border-cyan-300",
  },
  {
    id: "c7",
    title: "Taller de Música: Guitarra y Teclado",
    category: "Arte y Música",
    datetime: "Sábados · 11:30 a 13:00 hrs",
    location: "Casa de la Cultura",
    description: "Iniciación instrumental, lectura de acordes, ritmo y ensambles prácticos para principiantes e intermedios.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
  },
  {
    id: "c8",
    title: "Taller de Constelaciones Familiares & Bienestar",
    category: "Bienestar",
    datetime: "Sábados programados · 16:00 a 19:00 hrs",
    location: "Casa de la Cultura",
    description: "Taller vivencial de desarrollo personal, dinámicas sistémicas y reconciliación emocional en grupo guiado.",
    cost: "Consultar informes al WhatsApp",
    badgeColor: "bg-cyan-100 text-cyan-800 border-cyan-300",
  },
];

export default function CulturaNaturaPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const filteredEvents =
    selectedCategory === "all"
      ? CULTURAL_EVENTS
      : CULTURAL_EVENTS.filter((e) => e.category === selectedCategory);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased selection:bg-amber-500 selection:text-white">
      {/* TOP BAR */}
      <aside className="bg-slate-950 text-white text-xs py-2 px-4 border-b border-slate-800 text-center">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-1.5 text-slate-400 hover:text-purple-400 transition-colors text-xs font-semibold">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Volver a Inicio</span>
          </Link>
          <span className="font-extrabold tracking-wide text-xs">Comunidad Epicentro Natura</span>
          <span className="text-[11px] font-mono text-slate-400">by Hipha</span>
        </div>
      </aside>

      {/* HEADER / NAVBAR */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20 gap-3">
            {/* LOGO */}
            <Link href="/" className="flex items-center gap-2 group shrink-0">
              <div className="w-10 h-10 rounded-2xl bg-amber-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-amber-600/20 group-hover:scale-105 transition-transform">
                <Palette className="w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="text-lg font-black tracking-tight text-slate-950">Epicentro</span>
                  <span className="text-[10px] font-extrabold lowercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                    natura
                  </span>
                </div>
                <span className="text-[10px] font-semibold text-slate-500">Cultura Natura</span>
              </div>
            </Link>

            {/* ACCIONES RÁPIDAS */}
            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                href="https://whatsapp.com/channel/0029VbDrARy3GJOsfBGbg83b"
                target="_blank"
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <Megaphone className="w-3.5 h-3.5 text-blue-600" />
                <span className="hidden sm:inline">Comunidad Natura</span>
                <span className="sm:hidden">Avisos</span>
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <Store className="w-3.5 h-3.5 text-emerald-600" />
                <span className="hidden sm:inline">Directorio Comercial</span>
                <span className="sm:hidden">Directorio</span>
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-1 px-3 sm:px-3.5 py-2 rounded-xl text-xs font-bold text-white bg-slate-950 hover:bg-slate-800 transition-all shadow-xs"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Inicio</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
        {/* BREADCRUMBS */}
        <nav className="flex items-center gap-2 text-xs font-medium text-slate-500 py-1" aria-label="Breadcrumb">
          <Link href="/" className="hover:text-amber-700 transition-colors flex items-center gap-1">
            <span>Inicio</span>
          </Link>
          <span className="text-slate-400">/</span>
          <span className="font-bold text-slate-900">Cultura Natura</span>
        </nav>

        {/* MEGA HERO DE CULTURA NATURA */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-amber-950 via-slate-950 to-slate-900 text-white p-8 sm:p-12 border border-amber-900/40 shadow-2xl">
          <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-amber-500/15 blur-3xl pointer-events-none" />
          <div className="absolute -left-20 -bottom-20 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 text-xs font-bold tracking-wide">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>ESPACIO CULTURAL COMUNITARIO · PARQUE CENTRAL</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight text-white">
              Cultura Natura
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              El punto de encuentro artístico, formativo, deportivo y de bienestar para familias y vecinos de Natura Bosque Residencial, Los Robles y Prolongación Mariano Otero. Conoce los talleres y clases presenciales en la Casa de la Cultura.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={() => {
                  const el = document.getElementById("cartelera-section");
                  if (el) el.scrollIntoView({ behavior: "smooth" });
                }}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs sm:text-sm shadow-lg shadow-amber-500/20 transition-all active:scale-95"
              >
                <Calendar className="w-4 h-4" />
                <span>Ver Clases y Talleres</span>
              </button>
              <a
                href="https://wa.me/523333883199?text=Hola,%20me%20gustar%C3%ADa%20pedir%20m%C3%A1s%20informaci%C3%B3n%20sobre%20las%20clases%20y%20talleres%20en%20Casa%20de%20la%20Cultura"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs sm:text-sm border border-white/20 backdrop-blur-md transition-all active:scale-95"
              >
                <MessageCircle className="w-4 h-4 text-emerald-400" />
                <span>Pedir Información por WhatsApp</span>
              </a>
            </div>
          </div>
        </div>

        {/* SECCIÓN DE CARTELERA CULTURAL */}
        <section id="cartelera-section" className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight flex items-center gap-2">
                <Palette className="w-6 h-6 text-amber-600" />
                <span>Clases & Talleres en Casa de la Cultura</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Consulta horarios y costos. Pide informes directos al WhatsApp de Casa de la Cultura (33 3388 3199).
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                {filteredEvents.length} clases activas
              </span>
            </div>
          </div>

          {/* BOTONES DE FILTRO */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-1">
            {[
              { id: "all", label: "Todas las Clases" },
              { id: "Baile y Fitness", label: "💃 Baile & Fitness" },
              { id: "Deportes", label: "⚽ Fútbol Infantil" },
              { id: "Arte y Música", label: "📸 Arte & Música" },
              { id: "Bienestar", label: "🧘 Bienestar" },
            ].map((f) => {
              const isActive = selectedCategory === f.id;
              return (
                <button
                  key={f.id}
                  onClick={() => setSelectedCategory(f.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-extrabold border transition-all whitespace-nowrap ${
                    isActive
                      ? "bg-slate-950 text-white border-slate-950 shadow-sm"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-amber-50 hover:text-amber-800 hover:border-amber-200"
                  }`}
                >
                  {f.label}
                </button>
              );
            })}
          </div>

          {/* GRID DE EVENTOS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredEvents.map((ev) => {
              const whatsappMsg = encodeURIComponent(
                `Hola, me interesa pedir más información sobre la clase de ${ev.title} en Casa de la Cultura`
              );
              const whatsappUrl = `https://wa.me/523333883199?text=${whatsappMsg}`;

              return (
                <div
                  key={ev.id}
                  className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-7 flex flex-col justify-between shadow-sm hover:shadow-md hover:border-amber-400 transition-all group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[11px] font-extrabold px-3 py-1 rounded-full border ${ev.badgeColor}`}>
                        {ev.category}
                      </span>
                      <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                        {ev.cost.includes("$") ? ev.cost.split("/")[0].trim() : "Informes WhatsApp"}
                      </span>
                    </div>

                    <h3 className="text-lg font-black text-slate-900 group-hover:text-amber-700 transition-colors leading-snug">
                      {ev.title}
                    </h3>

                    <p className="text-xs text-slate-600 leading-relaxed">{ev.description}</p>

                    <div className="pt-3 border-t border-slate-100 space-y-2 text-xs text-slate-600">
                      <div className="flex items-center gap-2">
                        <Clock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span className="font-bold text-slate-900">{ev.datetime}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span className="font-semibold text-slate-700">Casa de la Cultura</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Tag className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span className="font-bold text-emerald-700">{ev.cost}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-5 mt-4 border-t border-slate-100">
                    <a
                      href={whatsappUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full py-3.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs transition-all shadow-sm active:scale-95 flex items-center justify-center gap-2"
                    >
                      <MessageCircle className="w-4 h-4" />
                      <span>Pedir más información por WhatsApp</span>
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* BANNER CONVOCATORIA */}
        <section className="rounded-3xl bg-white border border-slate-200 p-8 sm:p-10 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <span className="text-[11px] font-mono font-extrabold uppercase tracking-widest text-amber-700 bg-amber-100 px-3 py-1 rounded-full border border-amber-300">
              CASA DE LA CULTURA NATURA
            </span>
            <h3 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight">
              ¿Impartes clases, talleres o actividades formativas?
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              La Casa de la Cultura Natura está abierta para recibir propuestas de instructores y talleristas para enriquecer la vida comunitaria de los cotos.
            </p>
          </div>
          <a
            href="https://wa.me/523333883199?text=Hola,%20me%20gustar%C3%ADa%20proponer%20o%20impartir%20un%20taller%20o%20clase%20en%20Casa%20de%20la%20Cultura"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 px-6 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs sm:text-sm transition-all shadow-md active:scale-95 inline-flex items-center gap-2"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Pedir informes o proponer taller</span>
          </a>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="bg-slate-950 text-white text-xs py-8 px-4 border-t border-slate-800 mt-12">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-base font-black text-white">Epicentro</span>
            <span className="text-[10px] font-extrabold lowercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800">
              natura
            </span>
            <span className="text-slate-400 text-xs ml-2">© 2026 Plataforma Hiperlocal Comunitaria</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400 text-xs">
            <Link href="/" className="hover:text-white transition-colors">Inicio</Link>
            <Link href="/" className="hover:text-white transition-colors">Directorio Comercial</Link>
            <Link href="https://whatsapp.com/channel/0029VbDrARy3GJOsfBGbg83b" target="_blank" className="hover:text-white transition-colors">Comunidad Natura</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
