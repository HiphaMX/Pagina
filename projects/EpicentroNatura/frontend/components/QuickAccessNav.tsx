import React from "react";
import { Utensils, AlertCircle, Home, Bike, LayoutGrid } from "lucide-react";

export type QuickFilterKey = "all" | "food" | "urgencies" | "coto" | "delivery";

interface QuickAccessNavProps {
  activeFilter: QuickFilterKey;
  onSelectFilter: (key: QuickFilterKey) => void;
}

export const QuickAccessNav: React.FC<QuickAccessNavProps> = ({
  activeFilter,
  onSelectFilter,
}) => {
  const options = [
    {
      key: "all" as QuickFilterKey,
      label: "Todos los Comercios",
      icon: LayoutGrid,
    },
    {
      key: "food" as QuickFilterKey,
      label: "Comer en Casa",
      icon: Utensils,
    },
    {
      key: "urgencies" as QuickFilterKey,
      label: "Urgencias y Salud",
      icon: AlertCircle,
    },
    {
      key: "coto" as QuickFilterKey,
      label: "Emprendimientos en Coto",
      icon: Home,
    },
    {
      key: "delivery" as QuickFilterKey,
      label: "Con Delivery a Cotos",
      icon: Bike,
    },
  ];

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      {options.map((opt) => {
        const Icon = opt.icon;
        const isActive = activeFilter === opt.key;

        return (
          <button
            key={opt.key}
            onClick={() => onSelectFilter(opt.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
              isActive
                ? "bg-natura-700 text-white shadow-md shadow-natura-700/20"
                : "bg-white text-slate-700 border border-slate-200/80 hover:bg-slate-50"
            }`}
          >
            <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-500"}`} />
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};
