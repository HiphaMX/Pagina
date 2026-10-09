# 🚀 REPLICA PROCESS: The "Ultrapro" Landing Page Playbook — Oncología Robótica

Este documento detalla el paso a paso metodológico para la landing page de Oncología Robótica en HiphaMX.

## 0. Prerrequisitos y Configuración del Proyecto
1. **Carpeta del Proyecto:** `projects/OncologiaRobotica/`
2. **Archivos Base:** `BRIEF_MEMORIA.md`, `PROJECT_INTAKE_FORM.md`, `BRAND_DNA_QUESTIONNAIRE.md`, `brand_brief.md`, `voice_brief.md`, `llms.txt`, `robots.txt`, `index.html`.
3. **El Intake:** Completado en `PROJECT_INTAKE_FORM.md`.

## 1. La Capa Estratégica (Agent: BrandMind)
- Brand Brief (`brand_brief.md`) y Voice Brief (`voice_brief.md`) configurados con enfoque oncológico y quirúrgico.
- Wireframe estructurado:
  - Hero Section con Da Vinci Xi y CTA de valoración rápida
  - Cirugías y Procedimientos Robóticos de Mínima Invasión
  - Ventajas Clínicas para el Paciente (preservación funcional, menor sangrado, recuperación en 24-48h)
  - Tecnología y Respaldo Quirúrgico
  - Formulario y Botón de WhatsApp Directo

## 2. La Capa de Diseño y Código (Agent: DesignFlow)
- **Tailwind CSS & Glassmorphism:** Elementos flotantes con `backdrop-blur-md` y bordes sutiles `border-white/10`.
- **Modo Oscuro Quirúrgico:** Fondo profundo `#040B14` y `#0A192F` con resplandores en degradado cian `#00F2FE`.
- **Tipografía:** *Outfit* e *Inter*.
- **Micro-animaciones:** Transiciones suaves, elevación de tarjetas y efecto hover interactivo.

## 3. Integración y Orquestación (Agent: KAM)
- Validación continua entre diseño, copy y backend.
- Pruebas finales y blindaje con **SiteSentinel** (SMTP fallback y anti-spam).

## 4. Despliegue (Producción)
- Enrutamiento configurado en `vercel.json` y fallback en `app/main.py`.
