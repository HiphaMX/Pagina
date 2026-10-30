import React from "react";
import { MessageCircle } from "lucide-react";

interface WhatsAppButtonProps {
  url?: string;
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const WhatsAppButton: React.FC<WhatsAppButtonProps> = ({
  url,
  label = "WhatsApp",
  size = "md",
  className = "",
}) => {
  if (!url) return null;

  const sizeClasses = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2 font-medium",
    lg: "px-6 py-3 text-base gap-2.5 font-semibold",
  };

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center justify-center rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 active:scale-95 transition-all shadow-sm shadow-emerald-600/20 ${sizeClasses[size]} ${className}`}
    >
      <MessageCircle className={size === "sm" ? "w-3.5 h-3.5" : "w-4 h-4"} />
      <span>{label}</span>
    </a>
  );
};
