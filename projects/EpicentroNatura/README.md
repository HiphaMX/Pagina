# 🌲 Epicentro Natura — Plataforma Hiperlocal Comunitaria

Ecosistema digital comunitario hiperlocal desarrollado para **Natura Bosque Residencial** (Prolongación Mariano Otero, Zapopan, Jalisco) y fraccionamientos vecinos (El Fortín, Santa Ana Tepetitlán).

---

## 🏛️ Arquitectura del Sistema

```
projects/EpicentroNatura/
├── backend/
│   ├── app/
│   │   ├── database.py             # Configuración dual SQLAlchemy (SQLite / PostgreSQL)
│   │   ├── main.py                 # Instancia principal de FastAPI con CORS y Lifespan
│   │   ├── models/
│   │   │   └── models.py           # Community, BusinessCategory, Business, CulturalEvent, CivicNotice
│   │   ├── schemas/
│   │   │   └── schemas.py          # Esquemas Pydantic v2 con validadores E.164 y Zod mirror
│   │   ├── api/
│   │   │   ├── businesses.py       # Commercial Engine (/api/v1/businesses)
│   │   │   ├── events.py           # Cultural Engine con RSVP atómico (/api/v1/events)
│   │   │   ├── notices.py          # Civic Engine con prioridad alerta_zona (/api/v1/notices)
│   │   │   ├── admin.py            # Publicación protegida por token (/api/v1/admin)
│   │   │   └── common.py           # Metadatos (/api/v1/communities, /api/v1/categories)
│   │   ├── tasks/
│   │   │   └── auto_expiry.py      # Job de expiración automática de avisos cívicos
│   │   ├── utils/
│   │   │   ├── whatsapp.py         # WhatsApp Deep Link Builder
│   │   │   ├── opening_hours.py    # Evaluador de estatus de apertura en vivo
│   │   │   └── slug.py             # Generador de slugs seguros
│   │   └── fixtures/
│   │       ├── seed_data.json      # Fixtures con cotos, comercios y eventos de Parque Central
│   │       └── seeder.py           # Script para poblar la base de datos
│   ├── tests/
│   │   └── test_api.py             # Suite de 9 pruebas automatizadas con Pytest
│   ├── requirements.txt
│   └── run.py                      # Ejecutor del servidor FastAPI (Uvicorn)
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── page.tsx                # Dashboard Home interactivo
│   ├── components/
│   │   ├── AlertBanner.tsx         # Banner de alertas críticas de zona
│   │   ├── BusinessCard.tsx        # Ficha comercial con semáforo y WhatsApp link
│   │   ├── CulturalWidget.tsx      # Widget Fin de Semana en Casa de la Cultura
│   │   ├── NoticeCard.tsx          # Card con vigencia restante y categoría
│   │   ├── QuickAccessNav.tsx      # Filtros rápidos (Comer en Casa, Urgencias, Cotos)
│   │   ├── WhatsAppButton.tsx      # Botón de enlace directo
│   │   ├── RegisterBusinessModal.tsx # Modal con validación Zod
│   │   └── SubmitNoticeModal.tsx   # Modal de reporte vecinal
│   ├── lib/
│   │   ├── schemas.ts              # Esquemas Zod para formularios
│   │   └── utils.ts
│   └── types/
│       └── index.ts                # Tipos TypeScript
└── PROJECT_INTAKE_FORM.md
```

---

## ⚡ Guía de Ejecución Rápida

### 1. Backend (FastAPI)

```bash
# 1. Poblar la base de datos con cotos, comercios y eventos de prueba
./venv/bin/python projects/EpicentroNatura/backend/app/fixtures/seeder.py

# 2. Correr la suite de pruebas unitarias y de integración
./venv/bin/pytest projects/EpicentroNatura/backend/tests/test_api.py -v

# 3. Iniciar el servidor API en http://localhost:8000
./venv/bin/python projects/EpicentroNatura/backend/run.py
```

- Documentación interactiva Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Verificación de salud: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Tarea Programada de Auto-Expiración

Para ejecutar la verificación manual o mediante Cron job del sistema:

```bash
# Ejecución puntual:
./venv/bin/python projects/EpicentroNatura/backend/app/tasks/auto_expiry.py

# Ejecución continua (daemon cada 1 hora):
./venv/bin/python projects/EpicentroNatura/backend/app/tasks/auto_expiry.py --daemon --interval 3600
```

### 3. Frontend (Next.js)

```bash
cd projects/EpicentroNatura/frontend
npm install
npm run dev
```

El dashboard interactivo estará disponible en [http://localhost:3000](http://localhost:3000).

---

## 🔒 Contratos y Características Clave

1. **Concurrencia Atómica en RSVP:** El endpoint `POST /api/v1/events/{id}/rsvp` utiliza una instrucción SQL `UPDATE` condicionada directamente en base de datos para impedir sobrecupo incluso bajo múltiples peticiones concurrentes.
2. **Prioridad en Tablero Cívico:** Las alertas críticas de zona (`alerta_zona`) se ordenan de forma prioritaria en primer lugar antes de los comunicados oficiales y avisos de mascotas o empleo.
3. **Semáforo en Tiempo Real:** El evaluador de horarios procesa la zona horaria `America/Mexico_City` e indica si el local está abierto ahora y a qué hora cierra.
4. **Validación Dual:** Pydantic v2 en backend y Zod en cliente garantizan número de WhatsApp válido (estándar internacional E.164) y sanitización estricta.
