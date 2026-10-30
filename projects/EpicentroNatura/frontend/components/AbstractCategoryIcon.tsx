import React from "react";

interface AbstractCategoryIconProps {
  id: string;
  className?: string;
}

export function AbstractCategoryIcon({ id, className = "w-6 h-6" }: AbstractCategoryIconProps) {
  switch (id) {
    case "atencion-medica":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M24 10v28" stroke="currentColor" strokeWidth="3" />
          <path d="M10 24h6.5l2.5-6 5 12 2.5-6h11.5" stroke="currentColor" strokeWidth="2.8" />
        </svg>
      );
    case "clases-particulares":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 32c6-4 14-4 14 0c0-4 8-4 14 0V16c-6-4-14-4-14 0c0-4-8-4-14 0v16z" stroke="currentColor" strokeWidth="2.6" />
          <line x1="24" y1="16" x2="24" y2="32" stroke="currentColor" strokeWidth="2.2" />
        </svg>
      );
    case "comida-delivery":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 33h28" stroke="currentColor" strokeWidth="3" />
          <path d="M13 33c0-6.6 4.9-12 11-12s11 5.4 11 12" stroke="currentColor" strokeWidth="2.8" />
          <circle cx="24" cy="16.5" r="2.5" fill="currentColor" />
        </svg>
      );
    case "escuelas":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M24 13l16 8-16 8-16-8z" stroke="currentColor" strokeWidth="2.8" />
          <path d="M15 25v6.5c0 3.5 4 6 9 6s9-2.5 9-6.5V25" stroke="currentColor" strokeWidth="2.4" />
          <path d="M38 22v10" stroke="currentColor" strokeWidth="2.4" />
          <circle cx="38" cy="33" r="1.8" fill="currentColor" />
        </svg>
      );
    case "farmacias":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="17" width="30" height="14" rx="7" stroke="currentColor" strokeWidth="2.8" />
          <line x1="24" y1="17" x2="24" y2="31" stroke="currentColor" strokeWidth="2.4" />
          <path d="M16.5 21v6M13.5 24h6" stroke="currentColor" strokeWidth="2.2" />
        </svg>
      );
    case "fitness":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <circle cx="14" cy="34" r="5.5" stroke="currentColor" strokeWidth="2.8" />
          <circle cx="34" cy="14" r="5.5" stroke="currentColor" strokeWidth="2.8" />
          <line x1="18" y1="30" x2="30" y2="18" stroke="currentColor" strokeWidth="3.2" />
        </svg>
      );
    case "hogar":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 24l14-11 14 11v13a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2.8" />
          <path d="M20 37v-9h8v9" stroke="currentColor" strokeWidth="2.6" />
        </svg>
      );
    case "mascotas":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <circle cx="15" cy="17" r="2.8" stroke="currentColor" strokeWidth="2.4" />
          <circle cx="24" cy="13" r="3.2" stroke="currentColor" strokeWidth="2.4" />
          <circle cx="33" cy="17" r="2.8" stroke="currentColor" strokeWidth="2.4" />
          <path d="M16 28c0-4.5 3.5-7.5 8-7.5s8 3 8 7.5c0 5-3.5 7.5-8 7.5s-8-2.5-8-7.5z" stroke="currentColor" strokeWidth="2.8" />
        </svg>
      );
    case "postres-cafe":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M11 20h22v5a11 11 0 0 1-22 0v-5z" stroke="currentColor" strokeWidth="2.8" />
          <path d="M33 22h3a3 3 0 0 1 3 3v0a3 3 0 0 1-3 3h-3" stroke="currentColor" strokeWidth="2.4" />
          <path d="M22 9c2 2.5-2 4.5 0 6.5" stroke="currentColor" strokeWidth="2.4" />
        </svg>
      );
    case "productos-artesanales":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 12h14" stroke="currentColor" strokeWidth="2.6" />
          <path d="M19 12v3c0 4-5 6-5 10a10 10 0 0 0 20 0c0-4-5-6-5-10v-3" stroke="currentColor" strokeWidth="2.8" />
          <circle cx="24" cy="26" r="2.5" fill="currentColor" />
        </svg>
      );
    case "servicios-hogar":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <line x1="14" y1="34" x2="26" y2="22" stroke="currentColor" strokeWidth="3.2" />
          <path d="M23 15a8 8 0 0 1 10 10l-4-4" stroke="currentColor" strokeWidth="2.8" />
          <circle cx="15" cy="33" r="1.5" fill="currentColor" />
        </svg>
      );
    case "veterinarias":
      return (
        <svg viewBox="0 0 48 48" fill="none" className={className} strokeLinecap="round" strokeLinejoin="round">
          <path d="M24 38s-13-8-13-17a8 8 0 0 1 13-6 8 8 0 0 1 13 6c0 9-13 17-13 17z" stroke="currentColor" strokeWidth="2.8" />
          <path d="M24 19v9M19.5 23.5h9" stroke="currentColor" strokeWidth="2.6" />
        </svg>
      );
    default:
      return null;
  }
}
