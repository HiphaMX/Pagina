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
  User,
  Ticket,
  PlusCircle,
  X,
  Tag,
  CheckCircle2,
} from "lucide-react";

interface CulturalEvent {
  id: string;
  title: string;
  category: string;
  datetime: string;
  location: string;
  description: string;
  spots: number;
  instructor: string;
  cost: string;
  age: string;
  badgeColor: string;
}

const CULTURAL_EVENTS: CulturalEvent[] = [
  {
    id: "e1",
    title: "Taller Infantil de Barro & Pintura Botánica",
    category: "Talleres Infantiles & Juveniles",
    datetime: "Sábado 08 · 11:00 a 13:00 hrs",
    location: "Kiosco Parque Central Natura",
    description: "Modelado con arcilla natural de la zona y acuarelas sobre caballete al aire libre.",
    spots: 11,
    instructor: "Colectivo Raíces del Bosque",
    cost: "Gratuito con registro",
    age: "Niños de 5 a 14 años",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
  },
  {
    id: "e2",
    title: "Noche de Cine Vecinal al Aire Libre",
    category: "Cine al Aire Libre",
    datetime: "Sábado 15 · 19:30 hrs",
    location: "Explanada Verde Parque Central",
    description: "Proyección en pantalla gigante bajo las estrellas. Trae tu tapete o silla de camping. Palomitas de maíz gratuitas para niños de cotos.",
    spots: 38,
    instructor: "Comité Cultural Natura",
    cost: "Gratuito",
    age: "Todo público / Familiar",
    badgeColor: "bg-rose-100 text-rose-800 border-rose-300",
  },
  {
    id: "e3",
    title: "Clases Semanales de Danza Folclórica & Ritmos",
    category: "Danza y Música",
    datetime: "Martes y Jueves · 17:00 hrs",
    location: "Salón Polivalente Casa de Cultura",
    description: "Grupos infantiles y de adultos mayores con instructores del Instituto de Cultura Zapopan.",
    spots: 15,
    instructor: "Mtra. Carmen Salcedo (ICZ)",
    cost: "Aportación solidaria $30",
    age: "Infantil (17:00) y Adultos (18:15)",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
  },
  {
    id: "e4",
    title: "Taller de Huertos Urbanos y Compostaje en Casa",
    category: "Clases Formativas",
    datetime: "Domingo 16 · 10:00 hrs",
    location: "Jardín Botánico del Parque Central",
    description: "Aprende a cultivar hortalizas en espacios reducidos, control orgánico de plagas y elaboración de composta vecinal.",
    spots: 20,
    instructor: "Biol. Héctor Navarro",
    cost: "Gratuito",
    age: "Jóvenes y adultos",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
  },
  {
    id: "e5",
    title: "Ensamble Acústico al Atardecer: Cuerdas en el Bosque",
    category: "Danza y Música",
    datetime: "Domingo 23 · 18:00 hrs",
    location: "Kiosco Parque Central Natura",
    description: "Concierto íntimo con cuarteto de cuerdas interpretando música clásica y canciones mexicanas mientras cae el sol en el bosque.",
    spots: 50,
    instructor: "Ensamble Filarmónico Bosque de la Primavera",
    cost: "Entrada libre",
    age: "Todo público",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
  },
  {
    id: "e6",
    title: "Círculo de Lectura y Creación Literaria Vecinal",
    category: "Clases Formativas",
    datetime: "Miércoles · 18:30 hrs",
    location: "Terraza de la Casa de la Cultura",
    description: "Lectura colectiva, análisis de cuentos contemporáneos y ejercicios guiados de redacción poética y narrativa.",
    spots: 12,
    instructor: "Lic. Claudia Morales",
    cost: "Gratuito",
    age: "A partir de 15 años",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
  },
];

export default function CulturaNaturaPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [rsvpModalEvent, setRsvpModalEvent] = useState<CulturalEvent | null>(null);
  const [isProposeOpen, setIsProposeOpen] = useState<boolean>(false);
  const [rsvpForm, setRsvpForm] = useState({ name: "", coto: "", count: "1", phone: "" });

  const filteredEvents =
    selectedCategory === "all"
      ? CULTURAL_EVENTS
      : CULTURAL_EVENTS.filter((e) => e.category === selectedCategory);

  const handleRsvpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`¡Gracias ${rsvpForm.name}! Tu asistencia a "${rsvpModalEvent?.title}" (${rsvpForm.count} personas, ${rsvpForm.coto}) ha quedado registrada.`);
    setRsvpModalEvent(null);
    setRsvpForm({ name: "", coto: "", count: "1", phone: "" });
  };

  const handleProposeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert("¡Gracias por tu propuesta cultural! El Comité de la Casa de la Cultura Natura revisará los requerimientos de espacio y se pondrá en contacto.");
    setIsProposeOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased selection:bg-amber-500 selection:text-white">
      {/* TOP BAR */}
      <aside className="bg-slate-950 text-white text-xs py-2 px-4 border-b border-slate-800 text-center">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <span className="font-extrabold tracking-wide text-xs">Comunidad Epicentro Natura</span>
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
                href="/comunidad-natura"
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <Megaphone className="w-3.5 h-3.5 text-blue-600" />
                <span className="hidden sm:inline">Comunidad Natura</span>
                <span className="sm:hidden">Avisos</span>
              </Link>
              <Link
                href="/categoria/comida-delivery"
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
              El punto de encuentro artístico, recreativo y formativo para familias y vecinos de Natura Bosque Residencial, Los Robles y Prolongación Mariano Otero. Talleres semanales, cine al aire libre y actividades al pie del bosque.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={() => {
                  const el = document.getElementById("cartelera-section");
                  if (el) el.scrollIntoView({ behavior: "smooth" });
                }}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs sm:text-sm shadow-lg shadow-amber-500/20 transition-all active:scale-95"
              >
                <Calendar className="w-4 h-4" />
                <span>Ver Cartelera de Eventos</span>
              </button>
              <button
                onClick={() => setIsProposeOpen(true)}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs sm:text-sm border border-white/20 backdrop-blur-md transition-all active:scale-95"
              >
                <PlusCircle className="w-4 h-4 text-amber-300" />
                <span>Proponer un Taller o Clase</span>
              </button>
            </div>
          </div>
        </div>

        {/* SECCIÓN DE CARTELERA CULTURAL */}
        <section id="cartelera-section" className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight flex items-center gap-2">
                <Palette className="w-6 h-6 text-amber-600" />
                <span>Cartelera de Actividades & Talleres</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Reserva tu lugar gratuito o de aportación simbólica para ti y tu familia.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                {filteredEvents.length} actividades activas
              </span>
            </div>
          </div>

          {/* BOTONES DE FILTRO */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-1">
            {[
              { id: "all", label: "Todos los Eventos" },
              { id: "Talleres Infantiles & Juveniles", label: "🎨 Talleres Infantiles" },
              { id: "Cine al Aire Libre", label: "🎬 Cine al Aire Libre" },
              { id: "Danza y Música", label: "🎵 Danza y Música" },
              { id: "Clases Formativas", label: "🌱 Huertos & Clases" },
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
            {filteredEvents.map((ev) => (
              <div
                key={ev.id}
                className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-7 flex flex-col justify-between shadow-sm hover:shadow-md hover:border-amber-400 transition-all group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-[11px] font-extrabold px-3 py-1 rounded-full border ${ev.badgeColor}`}>
                      {ev.category}
                    </span>
                    <span className="text-xs font-extrabold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                      {ev.spots} cupos
                    </span>
                  </div>

                  <h3 className="text-lg font-black text-slate-900 group-hover:text-amber-700 transition-colors leading-snug">
                    {ev.title}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed">{ev.description}</p>

                  <div className="pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                      <span className="font-bold text-slate-800">{ev.datetime}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                      <span>{ev.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                      <span>
                        Imparte: <strong className="text-slate-700">{ev.instructor}</strong>
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                      <span className="text-emerald-700 font-extrabold">
                        {ev.cost} · {ev.age}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-5 mt-4 border-t border-slate-100">
                  <button
                    onClick={() => setRsvpModalEvent(ev)}
                    className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold text-xs transition-all shadow-sm active:scale-95 flex items-center justify-center gap-1.5"
                  >
                    <Ticket className="w-4 h-4" />
                    <span>Inscribirse / Reservar Asistencia</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* BANNER CONVOCATORIA */}
        <section className="rounded-3xl bg-white border border-slate-200 p-8 sm:p-10 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <span className="text-[11px] font-mono font-extrabold uppercase tracking-widest text-amber-700 bg-amber-100 px-3 py-1 rounded-full border border-amber-300">
              CONVOCATORIA ABIERTA
            </span>
            <h3 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight">
              ¿Impartes clases, talleres de arte o música?
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              La Casa de la Cultura Natura y las terrazas del Parque Central están abiertas a propuestas de residentes y talleristas profesionales para enriquecer la vida comunitaria.
            </p>
          </div>
          <button
            onClick={() => setIsProposeOpen(true)}
            className="shrink-0 px-6 py-3.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-white font-extrabold text-xs sm:text-sm transition-all shadow-md active:scale-95"
          >
            Proponer una Actividad
          </button>
        </section>
      </main>

      {/* MODAL RSVP */}
      {rsvpModalEvent && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 border border-slate-200 shadow-2xl relative">
            <button
              onClick={() => setRsvpModalEvent(null)}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700">RESERVA DE ASISTENCIA</span>
                <h3 className="text-base font-black text-slate-950 leading-tight">{rsvpModalEvent.title}</h3>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-100 text-xs text-slate-700 space-y-1.5 mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-amber-700" />
                <span className="font-bold">{rsvpModalEvent.datetime}</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-amber-700" />
                <span>{rsvpModalEvent.location}</span>
              </div>
            </div>

            <form onSubmit={handleRsvpSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Nombre Completo *</label>
                <input
                  type="text"
                  required
                  value={rsvpForm.name}
                  onChange={(e) => setRsvpForm({ ...rsvpForm, name: e.target.value })}
                  placeholder="Ej. Ana Sofía Martínez"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Coto de Residencia *</label>
                  <input
                    type="text"
                    required
                    value={rsvpForm.coto}
                    onChange={(e) => setRsvpForm({ ...rsvpForm, coto: e.target.value })}
                    placeholder="Ej. Natura Coto Roble"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">No. Asistentes *</label>
                  <select
                    value={rsvpForm.count}
                    onChange={(e) => setRsvpForm({ ...rsvpForm, count: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs bg-white"
                  >
                    <option value="1">1 persona</option>
                    <option value="2">2 personas</option>
                    <option value="3">3 personas</option>
                    <option value="4">4 personas</option>
                    <option value="5+">5 o más</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">WhatsApp de Confirmación *</label>
                <input
                  type="tel"
                  required
                  value={rsvpForm.phone}
                  onChange={(e) => setRsvpForm({ ...rsvpForm, phone: e.target.value })}
                  placeholder="33 1234 5678"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-xs shadow-md transition-all active:scale-95"
              >
                Confirmar Lugar en Cartelera
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL PROPONER */}
      {isProposeOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 border border-slate-200 shadow-2xl relative">
            <button
              onClick={() => setIsProposeOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                <Sparkles className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700">CONVOCATORIA CULTURAL</span>
                <h3 className="text-base sm:text-lg font-black text-slate-950">Proponer Taller o Actividad</h3>
              </div>
            </div>

            <form onSubmit={handleProposeSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Nombre de la Actividad o Taller *</label>
                <input
                  type="text"
                  required
                  placeholder="Ej. Taller de Acuarela Inicial / Club de Ajedrez"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Descripción Breve *</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Objetivo, materiales necesarios y dinámica de las sesiones..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">WhatsApp del Instructor *</label>
                <input
                  type="tel"
                  required
                  placeholder="33 1234 5678"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-white font-extrabold text-xs shadow-md transition-all active:scale-95"
              >
                Enviar Propuesta al Comité Cultural
              </button>
            </form>
          </div>
        </div>
      )}

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
            <Link href="/categoria/comida-delivery" className="hover:text-white transition-colors">Directorio Comercial</Link>
            <Link href="/comunidad-natura" className="hover:text-white transition-colors">Comunidad Natura</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
