import React from "react";
import { Trees, PlusCircle, Megaphone, Compass } from "lucide-react";

interface NavbarProps {
  currentTab: "commercial" | "cultural" | "civic";
  onTabChange: (tab: "commercial" | "cultural" | "civic") => void;
  onOpenRegisterModal: () => void;
  onOpenNoticeModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  onOpenRegisterModal,
  onOpenNoticeModal,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20 gap-4">
          {/* Logo & Identity */}
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-natura-700 to-emerald-800 text-white flex items-center justify-center shadow-md shadow-natura-800/20">
              <Trees className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-slate-900 tracking-tight">
                  Epicentro Natura
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-natura-100 text-natura-800 border border-natura-200">
                  <Compass className="w-3 h-3 text-natura-600" />
                  Hiperlocal
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Natura Bosque Residencial & Prol. Mariano Otero
              </p>
            </div>
          </div>

          {/* Navigation Tabs (Desktop) */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100/80 p-1.5 rounded-2xl border border-slate-200/60">
            <button
              onClick={() => onTabChange("commercial")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                currentTab === "commercial"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Directorio Comercial
            </button>
            <button
              onClick={() => onTabChange("civic")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                currentTab === "civic"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Tablero Cívico
            </button>
            <button
              onClick={() => onTabChange("cultural")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                currentTab === "cultural"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Casa de la Cultura
            </button>
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenNoticeModal}
              className="inline-flex items-center gap-1.5 px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all border border-slate-200"
            >
              <Megaphone className="w-3.5 h-3.5 text-slate-600" />
              <span className="hidden sm:inline">Aviso Comunitario</span>
              <span className="sm:hidden">Aviso</span>
            </button>
            <button
              onClick={onOpenRegisterModal}
              className="inline-flex items-center gap-1.5 px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl text-xs font-bold bg-natura-700 hover:bg-natura-800 text-white transition-all shadow-sm shadow-natura-800/20 active:scale-95"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Registrar Negocio</span>
              <span className="sm:hidden">Negocio</span>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Bar */}
        <div className="flex md:hidden items-center justify-around py-2 border-t border-slate-100 text-xs font-semibold">
          <button
            onClick={() => onTabChange("commercial")}
            className={`py-1.5 px-2 border-b-2 ${
              currentTab === "commercial"
                ? "border-natura-600 text-natura-800 font-bold"
                : "border-transparent text-slate-500"
            }`}
          >
            Comercios
          </button>
          <button
            onClick={() => onTabChange("civic")}
            className={`py-1.5 px-2 border-b-2 ${
              currentTab === "civic"
                ? "border-natura-600 text-natura-800 font-bold"
                : "border-transparent text-slate-500"
            }`}
          >
            Tablero Cívico
          </button>
          <button
            onClick={() => onTabChange("cultural")}
            className={`py-1.5 px-2 border-b-2 ${
              currentTab === "cultural"
                ? "border-natura-600 text-natura-800 font-bold"
                : "border-transparent text-slate-500"
            }`}
          >
            Casa de Cultura
          </button>
        </div>
      </div>
    </header>
  );
};
