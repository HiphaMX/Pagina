"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Palette,
  Clock,
  MapPin,
  Sparkles,
  ArrowLeft,
  Store,
  Megaphone,
  MessageCircle,
  X,
  Send,
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
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [contactData, setContactData] = useState({
    name: "",
    phone: "",
    email: "",
    title: "",
    category: "Baile y Fitness",
    audience: "Infantil (4 a 12 años)",
    schedule: "",
    description: "",
  });

  const handleContactSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const waMsg = encodeURIComponent(
      `Hola Epicentro Natura, deseo proponer un taller / clase para Cultura Natura:\n\n` +
      `👤 Instructor / Colectivo: ${contactData.name}\n` +
      `📞 Teléfono / WhatsApp: ${contactData.phone}\n` +
      (contactData.email ? `✉️ Correo: ${contactData.email}\n` : ``) +
      `🎨 Taller propuesto: ${contactData.title}\n` +
      `🏷️ Disciplina: ${contactData.category}\n` +
      `👥 Público: ${contactData.audience}\n` +
      `⏰ Horario sugerido: ${contactData.schedule || "Por definir"}\n` +
      `📝 Descripción / Requerimientos: ${contactData.description || "Sin detalles adicionales"}`
    );

    window.open(`https://wa.me/523333883199?text=${waMsg}`, "_blank");
    alert("¡Gracias por tu interés! Tu propuesta ha sido registrada y enviada al equipo de Epicentro Natura.");
    setIsContactModalOpen(false);
    setContactData({
      name: "",
      phone: "",
      email: "",
      title: "",
      category: "Baile y Fitness",
      audience: "Infantil (4 a 12 años)",
      schedule: "",
      description: "",
    });
  };

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
              <span>ESPACIO CULTURAL COMUNITARIO</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight text-white">
              Cultura Natura
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              Las sedes que son un punto de encuentro artístico, formativo, deportivo y de bienestar para familias y vecinos de Epicentro Natura.
            </p>
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
                    </div>
                  </div>

                  <div className="pt-5 mt-4 border-t border-slate-100">
                    <a
                      href={whatsappUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full py-3.5 rounded-xl bg-slate-950 hover:bg-amber-500 text-white hover:text-slate-950 font-black text-xs transition-all shadow-md active:scale-95 flex items-center justify-center gap-2 group/btn"
                    >
                      <MessageCircle className="w-4 h-4 text-emerald-400 group-hover/btn:text-slate-950 transition-colors" />
                      <span>Pedir más información</span>
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
              CULTURA NATURA
            </span>
            <h3 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight">
              ¿Impartes clases, talleres o actividades formativas?
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Cultura Natura es un espacio abierto para recibir propuestas de instructores y talleristas para enriquecer la vida comunitaria de nuestro epicentro
            </p>
          </div>
          <button
            type="button"
            onClick={() => setIsContactModalOpen(true)}
            className="shrink-0 px-6 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs sm:text-sm transition-all shadow-md active:scale-95 inline-flex items-center gap-2 cursor-pointer"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Contácta a Epicentro</span>
          </button>
        </section>
      </main>

      {/* MODAL: CONTACTA A EPICENTRO */}
      {isContactModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs">
          <div className="relative w-full max-w-lg rounded-3xl bg-white p-6 sm:p-8 shadow-2xl max-h-[92vh] overflow-y-auto border border-slate-200">
            <button
              type="button"
              onClick={() => setIsContactModalOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
              aria-label="Cerrar modal"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="mb-5 space-y-1.5">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-900 text-[10px] font-extrabold uppercase tracking-wide">
                <Sparkles className="w-3 h-3 text-amber-600" />
                <span>CULTURA NATURA · CONVOCATORIA</span>
              </div>
              <h3 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight">
                Contácta a Epicentro
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Cuéntanos sobre tu clase, curso o actividad formativa. Nuestro equipo evaluará tu propuesta para integrarla a la cartelera cultural.
              </p>
            </div>

            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Nombre completo o Colectivo *</label>
                <input
                  type="text"
                  required
                  placeholder="Ej. Profa. Ana Martínez / Colectivo Danza Viva"
                  value={contactData.name}
                  onChange={(e) => setContactData({ ...contactData, name: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Teléfono / WhatsApp *</label>
                  <input
                    type="tel"
                    required
                    placeholder="33 1234 5678"
                    value={contactData.phone}
                    onChange={(e) => setContactData({ ...contactData, phone: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Correo Electrónico (opcional)</label>
                  <input
                    type="email"
                    placeholder="correo@ejemplo.com"
                    value={contactData.email}
                    onChange={(e) => setContactData({ ...contactData, email: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Nombre de la clase o taller propuesto *</label>
                <input
                  type="text"
                  required
                  placeholder="Ej. Taller de Acuarela / Yoga Restaurativo / Fútbol Kids"
                  value={contactData.title}
                  onChange={(e) => setContactData({ ...contactData, title: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Disciplina / Categoría *</label>
                  <select
                    value={contactData.category}
                    onChange={(e) => setContactData({ ...contactData, category: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none cursor-pointer"
                  >
                    <option value="Baile y Fitness">💃 Baile & Fitness</option>
                    <option value="Deportes">⚽ Deportes y Fútbol</option>
                    <option value="Arte y Música">🎨 Arte, Música y Fotografía</option>
                    <option value="Bienestar">🧘 Bienestar y Mindfulness</option>
                    <option value="Académico / Idiomas">📚 Formación / Idiomas / Ajedrez</option>
                    <option value="Otro">✨ Otra disciplina</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Público objetivo *</label>
                  <select
                    value={contactData.audience}
                    onChange={(e) => setContactData({ ...contactData, audience: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none cursor-pointer"
                  >
                    <option value="Infantil (4 a 12 años)">Infantil (4 a 12 años)</option>
                    <option value="Jóvenes y Adolescentes">Jóvenes y Adolescentes</option>
                    <option value="Adultos">Adultos</option>
                    <option value="Adultos Mayores">Adultos Mayores</option>
                    <option value="Familiar / Todas las edades">Familiar / Todas las edades</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Días u horarios sugeridos</label>
                <input
                  type="text"
                  placeholder="Ej. Martes y Jueves 17:00 hrs / Sábados 10:00 hrs"
                  value={contactData.schedule}
                  onChange={(e) => setContactData({ ...contactData, schedule: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Breve descripción de la propuesta o requerimientos</label>
                <textarea
                  rows={3}
                  placeholder="Cuéntanos brevemente de qué trata la actividad, requerimientos de espacio o materiales..."
                  value={contactData.description}
                  onChange={(e) => setContactData({ ...contactData, description: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition-colors resize-none"
                />
              </div>

              <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                <button
                  type="submit"
                  className="w-full py-3.5 px-4 rounded-xl bg-slate-950 hover:bg-slate-800 text-white font-extrabold text-xs sm:text-sm shadow-md transition-all active:scale-95 flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Send className="w-4 h-4 text-amber-400" />
                  <span>Enviar Propuesta a Epicentro</span>
                </button>
                <button
                  type="button"
                  onClick={() => setIsContactModalOpen(false)}
                  className="w-full sm:w-auto py-3.5 px-5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
              </div>

              <p className="text-[11px] text-slate-400 text-center pt-1">
                Al enviar, se abrirá también una copia en WhatsApp para contacto directo con el equipo.
              </p>
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
            <Link href="/" className="hover:text-white transition-colors">Directorio Comercial</Link>
            <Link href="https://whatsapp.com/channel/0029VbDrARy3GJOsfBGbg83b" target="_blank" className="hover:text-white transition-colors">Comunidad Natura</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
