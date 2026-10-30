"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Megaphone,
  Search,
  MapPin,
  MessageCircle,
  PlusCircle,
  X,
  Palette,
  Store,
  ArrowLeft,
  Users,
  AlertTriangle,
  HeartHandshake,
  Briefcase,
  Dog,
  ShieldAlert,
} from "lucide-react";

interface CommunityNotice {
  id: string;
  type: string;
  badgeBg: string;
  title: string;
  content: string;
  communitySlug: string;
  communityName: string;
  daysRemaining: number;
  whatsapp: string;
}

const COMMUNITY_NOTICES: CommunityNotice[] = [
  {
    id: "n1",
    type: "Mascota Extraviada",
    badgeBg: "bg-rose-100 text-rose-700 border-rose-200",
    title: "Perrito Schnauzer gris extraviado cerca de Coto Encino",
    content: "Responde a 'Max', llevaba collar azul con placa. Si lo viste por favor comunícate a caseta o vía WhatsApp. Muy amigable.",
    communitySlug: "natura-bosque-residencial",
    communityName: "Natura Bosque Residencial",
    daysRemaining: 14,
    whatsapp: "+523318889901",
  },
  {
    id: "n2",
    type: "Comunicado Oficial",
    badgeBg: "bg-blue-100 text-blue-700 border-blue-200",
    title: "Nuevo tag vehicular de residentes en acceso principal",
    content: "A partir del próximo lunes se requerirá el nuevo tag RFID con chip para acceso automatizado por la pluma de residentes.",
    communitySlug: "los-robles",
    communityName: "Los Robles",
    daysRemaining: 20,
    whatsapp: "+523315550999",
  },
  {
    id: "n3",
    type: "Empleo Local",
    badgeBg: "bg-emerald-100 text-emerald-800 border-emerald-200",
    title: "Se solicita apoyo para jardinería y mantenimiento",
    content: "Para áreas comunes de coto privado 3 días a la semana. Enviar mensaje por WhatsApp con referencias y experiencia previa.",
    communitySlug: "el-fortin",
    communityName: "El Fortín",
    daysRemaining: 12,
    whatsapp: "+523318889902",
  },
  {
    id: "n4",
    type: "Causa Solidaria",
    badgeBg: "bg-purple-100 text-purple-700 border-purple-200",
    title: "Colecta vecinal de chamarras y cobijas para invierno",
    content: "Punto de acopio en Casa de la Cultura del Parque Central los fines de semana. Ropa limpia en buen estado para albergues.",
    communitySlug: "natura-bosque-residencial",
    communityName: "Natura Bosque Residencial",
    daysRemaining: 25,
    whatsapp: "+523315550202",
  },
  {
    id: "n5",
    type: "Reporte de Zona",
    badgeBg: "bg-amber-100 text-amber-800 border-amber-200",
    title: "Bache reportado en carril poniente de Prol. Mariano Otero",
    content: "Reportado ante SIOP y Obras Públicas Zapopan folio #9812. Precaución al circular al descender hacia el cruce con Los Robles.",
    communitySlug: "punta-de-otero",
    communityName: "Punta de Otero",
    daysRemaining: 7,
    whatsapp: "+523315550201",
  },
  {
    id: "n6",
    type: "Mascota Extraviada",
    badgeBg: "bg-rose-100 text-rose-700 border-rose-200",
    title: "Gatita carey encontrada en áreas verdes de Coto Luna",
    content: "Está resguardada temporalmente en cochera, tiene collar morado sin placa. Se busca a sus dueños legítimos.",
    communitySlug: "luna-bosque",
    communityName: "Luna Bosque",
    daysRemaining: 10,
    whatsapp: "+523315550101",
  },
];

export default function ComunidadNaturaPage() {
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedCoto, setSelectedCoto] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isNoticeOpen, setIsNoticeOpen] = useState<boolean>(false);
  const [noticeForm, setNoticeForm] = useState({
    title: "",
    type: "Mascota Extraviada",
    coto: "natura-bosque-residencial",
    content: "",
    phone: "",
  });

  const filteredNotices = COMMUNITY_NOTICES.filter((n) => {
    const matchType = selectedType === "all" || n.type === selectedType;
    const matchCoto = selectedCoto === "all" || n.communitySlug === selectedCoto;
    const q = searchQuery.toLowerCase().trim();
    const matchText =
      !q ||
      n.title.toLowerCase().includes(q) ||
      n.content.toLowerCase().includes(q) ||
      n.communityName.toLowerCase().includes(q);
    return matchType && matchCoto && matchText;
  });

  const handleNoticeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`¡Gracias por publicar! Tu aviso "${noticeForm.title}" ha sido enviado y se publicará en el muro de Comunidad Natura.`);
    setIsNoticeOpen(false);
    setNoticeForm({
      title: "",
      type: "Mascota Extraviada",
      coto: "natura-bosque-residencial",
      content: "",
      phone: "",
    });
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans flex flex-col antialiased selection:bg-blue-600 selection:text-white">
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
              <div className="w-10 h-10 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-blue-600/20 group-hover:scale-105 transition-transform">
                <Megaphone className="w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="text-lg font-black tracking-tight text-slate-950">Epicentro</span>
                  <span className="text-[10px] font-extrabold lowercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                    natura
                  </span>
                </div>
                <span className="text-[10px] font-semibold text-slate-500">Comunidad Natura</span>
              </div>
            </Link>

            {/* ACCIONES RÁPIDAS */}
            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                href="/cultura-natura"
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <Palette className="w-3.5 h-3.5 text-amber-600" />
                <span className="hidden sm:inline">Cultura Natura</span>
                <span className="sm:hidden">Cultura</span>
              </Link>
              <Link
                href="/categoria/comida-delivery"
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
              >
                <Store className="w-3.5 h-3.5 text-emerald-600" />
                <span className="hidden sm:inline">Directorio Comercial</span>
                <span className="sm:hidden">Directorio</span>
              </Link>
              <button
                onClick={() => setIsNoticeOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 active:scale-95 transition-all shadow-md shadow-blue-600/20"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>+ Publicar Aviso</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
        {/* BREADCRUMBS */}
        <nav className="flex items-center gap-2 text-xs font-medium text-slate-500 py-1" aria-label="Breadcrumb">
          <Link href="/" className="hover:text-blue-700 transition-colors flex items-center gap-1">
            <span>Inicio</span>
          </Link>
          <span className="text-slate-400">/</span>
          <span className="font-bold text-slate-900">Comunidad Natura</span>
        </nav>

        {/* MEGA HERO DE COMUNIDAD NATURA */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-950 via-slate-950 to-slate-900 text-white p-8 sm:p-12 border border-blue-900/40 shadow-2xl">
          <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-blue-500/15 blur-3xl pointer-events-none" />
          <div className="absolute -left-20 -bottom-20 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/40 text-blue-300 text-xs font-bold tracking-wide">
              <Users className="w-3.5 h-3.5 text-blue-300" />
              <span>CANAL OFICIAL VECINAL · COMUNICACIÓN ENTRE COTOS</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight text-white">
              Comunidad Natura
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              El muro oficial y canal de comunicación directa para los residentes de Natura Bosque Residencial, Los Robles, El Fortín, Luna Bosque y cotos aledaños de Prolongación Mariano Otero. Reportes de mascotas, comunicados de comités, empleo local y causas solidarias.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={() => setIsNoticeOpen(true)}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs sm:text-sm shadow-lg shadow-blue-600/30 transition-all active:scale-95"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Publicar un Aviso Comunitario</span>
              </button>
              <button
                onClick={() => {
                  const el = document.getElementById("muro-section");
                  if (el) el.scrollIntoView({ behavior: "smooth" });
                }}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs sm:text-sm border border-white/20 backdrop-blur-md transition-all active:scale-95"
              >
                <span>Explorar Muro Vecinal</span>
              </button>
            </div>
          </div>
        </div>

        {/* SECCIÓN DE MURO VECINAL */}
        <section id="muro-section" className="space-y-6">
          {/* BARRA DE BÚSQUEDA Y SELECTOR DE COTO */}
          <div className="p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar por palabra clave (ej. perro, jardín, tag, reunión)..."
                className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-hidden bg-slate-50 focus:bg-white"
              />
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <label htmlFor="coto-select" className="text-xs font-bold text-slate-600 whitespace-nowrap">
                Filtrar por Coto:
              </label>
              <select
                id="coto-select"
                value={selectedCoto}
                onChange={(e) => setSelectedCoto(e.target.value)}
                className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
              >
                <option value="all">Todos los Cotos</option>
                <option value="natura-bosque-residencial">Natura Bosque Residencial</option>
                <option value="los-robles">Los Robles</option>
                <option value="bosque-primavera">Bosque de la Primavera</option>
                <option value="el-fortin">El Fortín</option>
                <option value="luna-bosque">Luna Bosque</option>
                <option value="la-granja">La Granja</option>
                <option value="puerta-del-bosque">Puerta del Bosque</option>
                <option value="punta-de-otero">Punta de Otero</option>
                <option value="monte-verde">Monte Verde</option>
                <option value="mision-la-floresta">Misión la Floresta</option>
              </select>
            </div>
          </div>

          {/* BOTONES DE CATEGORÍA DE AVISO */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-1">
            {[
              { id: "all", label: "Todos los Avisos" },
              { id: "Mascota Extraviada", label: "🐶 Mascotas Extraviadas" },
              { id: "Comunicado Oficial", label: "📢 Comunicados de Comités" },
              { id: "Empleo Local", label: "💼 Empleo Local" },
              { id: "Causa Solidaria", label: "🤝 Causas Solidarias" },
              { id: "Reporte de Zona", label: "⚠️ Reportes Viales" },
            ].map((t) => {
              const isActive = selectedType === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setSelectedType(t.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-extrabold border transition-all whitespace-nowrap ${
                    isActive
                      ? "bg-slate-950 text-white border-slate-950 shadow-sm"
                      : "bg-white text-slate-700 border-slate-200 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200"
                  }`}
                >
                  {t.label}
                </button>
              );
            })}
          </div>

          {/* ENCABEZADO DE RESULTADOS */}
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold text-slate-500">
              {filteredNotices.length} aviso{filteredNotices.length === 1 ? "" : "s"} vigente{filteredNotices.length === 1 ? "" : "s"}
            </span>
            <span className="text-xs text-blue-700 font-semibold">
              Actualización constante por comités vecinales
            </span>
          </div>

          {/* GRID DE AVISOS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredNotices.map((n) => {
              const waUrl = `https://wa.me/${n.whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(
                `Hola, vi tu aviso en Comunidad Natura: "${n.title}"`
              )}`;
              return (
                <div
                  key={n.id}
                  className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-7 flex flex-col justify-between shadow-sm hover:shadow-md hover:border-blue-400 transition-all group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-[11px] font-extrabold px-3 py-1 rounded-full border ${n.badgeBg}`}>
                        {n.type}
                      </span>
                      <span className="text-[11px] font-mono font-bold text-slate-400">
                        {n.daysRemaining} días vigentes
                      </span>
                    </div>

                    <h3 className="text-base sm:text-lg font-black text-slate-950 group-hover:text-blue-700 transition-colors leading-snug">
                      {n.title}
                    </h3>

                    <p className="text-xs text-slate-600 leading-relaxed">{n.content}</p>

                    <div className="pt-3 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-500">
                      <MapPin className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span className="font-bold text-slate-800">{n.communityName}</span>
                    </div>
                  </div>

                  <div className="pt-5 mt-4 border-t border-slate-100">
                    <a
                      href={waUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full py-3 px-4 rounded-xl bg-slate-100 hover:bg-blue-50 text-slate-800 hover:text-blue-700 font-bold text-xs transition-colors flex items-center justify-center gap-2 group-hover:border-blue-300 border border-slate-200"
                    >
                      <MessageCircle className="w-4 h-4 text-emerald-600" />
                      <span>Contactar al Vecino por WhatsApp</span>
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* BANNER COMPROMISO */}
        <section className="rounded-3xl bg-white border border-slate-200 p-8 sm:p-10 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <span className="text-[11px] font-mono font-extrabold uppercase tracking-widest text-blue-700 bg-blue-100 px-3 py-1 rounded-full border border-blue-200">
              COMPROMISO COMUNITARIO
            </span>
            <h3 className="text-xl sm:text-2xl font-black text-slate-950 tracking-tight">
              Cuidemos y mantengamos segura nuestra zona
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Los avisos son revisados para mantener un canal confiable, libre de spam y enfocado en la seguridad, convivencia y apoyo mutuo entre familias de cotos.
            </p>
          </div>
          <button
            onClick={() => setIsNoticeOpen(true)}
            className="shrink-0 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs sm:text-sm transition-all shadow-md active:scale-95"
          >
            Publicar Aviso Ahora
          </button>
        </section>
      </main>

      {/* MODAL PUBLICAR AVISO */}
      {isNoticeOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 border border-slate-200 shadow-2xl relative">
            <button
              onClick={() => setIsNoticeOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-blue-100 text-blue-800 flex items-center justify-center shrink-0">
                <Megaphone className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700">CANAL VECINAL</span>
                <h3 className="text-base sm:text-lg font-black text-slate-950">Publicar Aviso a la Comunidad</h3>
              </div>
            </div>

            <form onSubmit={handleNoticeSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Título del Aviso *</label>
                <input
                  type="text"
                  required
                  value={noticeForm.title}
                  onChange={(e) => setNoticeForm({ ...noticeForm, title: e.target.value })}
                  placeholder="Ej. Perrito extraviado cerca de caseta / Vacante de guardia"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Tipo de Aviso *</label>
                  <select
                    value={noticeForm.type}
                    onChange={(e) => setNoticeForm({ ...noticeForm, type: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs bg-white"
                  >
                    <option value="Mascota Extraviada">🐶 Mascota Extraviada</option>
                    <option value="Comunicado Oficial">📢 Comunicado Oficial</option>
                    <option value="Empleo Local">💼 Empleo Local</option>
                    <option value="Causa Solidaria">🤝 Causa Solidaria</option>
                    <option value="Reporte de Zona">⚠️ Reporte de Zona</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-800 mb-1">Coto o Fraccionamiento *</label>
                  <select
                    value={noticeForm.coto}
                    onChange={(e) => setNoticeForm({ ...noticeForm, coto: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs bg-white"
                  >
                    <option value="natura-bosque-residencial">Natura Bosque Residencial</option>
                    <option value="los-robles">Los Robles</option>
                    <option value="bosque-primavera">Bosque de la Primavera</option>
                    <option value="el-fortin">El Fortín</option>
                    <option value="luna-bosque">Luna Bosque</option>
                    <option value="la-granja">La Granja</option>
                    <option value="puerta-del-bosque">Puerta del Bosque</option>
                    <option value="punta-de-otero">Punta de Otero</option>
                    <option value="monte-verde">Monte Verde</option>
                    <option value="mision-la-floresta">Misión la Floresta</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">Descripción Detallada *</label>
                <textarea
                  rows={3}
                  required
                  value={noticeForm.content}
                  onChange={(e) => setNoticeForm({ ...noticeForm, content: e.target.value })}
                  placeholder="Detalla señas particulares, fecha del suceso o información para que los vecinos te puedan ayudar..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">WhatsApp de Contacto Directo *</label>
                <input
                  type="tel"
                  required
                  value={noticeForm.phone}
                  onChange={(e) => setNoticeForm({ ...noticeForm, phone: e.target.value })}
                  placeholder="33 1234 5678"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                />
              </div>

              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-[11px] text-blue-950">
                🛡️ Tu aviso será publicado en el muro vecinal y estará disponible para contacto directo entre residentes.
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs shadow-md transition-all active:scale-95"
              >
                Publicar Aviso Comunitario
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
            <Link href="/cultura-natura" className="hover:text-white transition-colors">Cultura Natura</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
