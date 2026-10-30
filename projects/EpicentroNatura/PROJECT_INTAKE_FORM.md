# PROJECT INTAKE FORM — Epicentro Natura

## 1. Información General del Proyecto
- **Nombre del Proyecto:** Epicentro Natura (Plataforma Hiperlocal Natura Bosque)
- **Ubicación Geográfica:** Prolongación Mariano Otero, Zapopan, Jalisco (Natura Bosque Residencial, cotos interiores y fraccionamientos vecinos).
- **Tipo de Proyecto:** Ecosistema digital comunitario hiperlocal (Directorio comercial, tablero cívico, oferta cultural y microemprendimientos en coto).
- **Rol Director / Orquestador:** KAM (Key Account Manager)
- **Agentes Asignados:**
  - **BrandMind:** Arquitectura de información, tono cívico y contextualización geográfica de cotos.
  - **CodeGuardian:** Arquitectura FastAPI, modelos SQLAlchemy 2.0, concurrencia atómica de RSVP y seguridad.
  - **DesignFlow:** Interfaz Next.js (App Router), Tailwind CSS y componentes responsivos.
  - **SiteSentinel:** Test suite en Pytest, verificación de endpoints y tareas cron.

## 2. Pilares del Ecosistema
1. **Oferta Cultural:** Cartelera de la Casa de la Cultura (Parque Central Natura) con control atómico de cupos (RSVP).
2. **Directorio Comercial Local:** Comercios a pie de calle sobre Prolongación Mariano Otero y cotos aledaños.
3. **Microemprendimientos en Casa:** Distintivo "En Coto" para emprendedores vecinales (repostería, clases, servicios).
4. **Tablero Cívico Vecinal:** Alertas de zona (urgencias/obras hidráulicas), comunicados oficiales verificados, mascotas extraviadas y vacantes de empleo.

## 3. Estado Técnico
- Backend: FastAPI + SQLAlchemy 2.0 + Pydantic v2
- Base de datos: SQLite portable / PostgreSQL producción con tipos GUID y JSON nativos.
- Tareas en segundo plano: Script de auto-expiración de avisos con soporte CLI y daemon (`tasks/auto_expiry.py`).
- Frontend: Next.js (App Router), Tailwind CSS, Lucide Icons, validaciones Zod.
- Tests: 9 tests automatizados en Pytest pasando al 100%.
