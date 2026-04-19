# 🎯 FLUJO DE ORQUESTACIÓN SOCIAL MEDIA — KAM v2.0

> **"Cada solicitud de redes sociales sigue exactamente este protocolo. Sin excepciones. Sin atajos."**

---

## 🗺️ VISTA GENERAL DEL FLUJO

```
USUARIO
  │
  ▼
┌─────────────────────────────────────────────┐
│  KAM — Recibe la solicitud                  │
│  Hace intake · Clasifica · Orquesta         │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  ¿Hay ADN de marca  │
         │  documentado?       │
         └────┬──────────┬─────┘
              │ NO       │ SÍ
              ▼          ▼
         CUESTIONARIO  CARGAR
         ADN DE MARCA  BRIEF_MEMORIA
              │          │
              └────┬─────┘
                   │
                   ▼
            ┌─────────────┐
            │  BRANDMIND  │ ← Brand Brief + Voice Brief
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │  VIRALGEN   │ ← Diagnóstico psicográfico +
            │             │   Concepto filosófico +
            │             │   Contenido completo +
            └──────┬──────┘   Prompts visuales
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
  ┌─────────────┐      ┌─────────────┐
  │ IMAGENOLOGO │      │  LAUNCHBUZZ │
  │ (imágenes   │      │  (B2B/email │
  │  ads hiper- │      │   LinkedIn) │
  │  realistas) │      │  si aplica  │
  └──────┬──────┘      └──────┬──────┘
         │                    │
         └─────────┬──────────┘
                   │
                   ▼
            ┌─────────────┐
            │     KAM     │ ← Consolida todos los entregables
            │  Entrega    │   Actualiza BRIEF_MEMORIA.md
            │  al usuario │   Archiva en projects/[CLIENTE]/
            └─────────────┘
```

---

## 📁 ARQUITECTURA DE CARPETAS POR PROYECTO

Cada cliente tiene su propia carpeta. Se crea al iniciar el proyecto.

```
projects/
├── _template/                       ← Plantillas base (no modificar)
│   ├── BRIEF_MEMORIA.md             ← Memoria viva del proyecto
│   ├── BRAND_DNA_QUESTIONNAIRE.md   ← 10 preguntas de ADN de marca
│   ├── brand_brief.md               ← Output de BrandMind
│   └── voice_brief.md               ← Voz de marca para VIRALGEN + LaunchBuzz
│
└── [NOMBRE_CLIENTE]/                ← Una carpeta por cliente
    ├── BRIEF_MEMORIA.md             ← Memoria del proyecto (copia del template)
    ├── brand_brief.md               ← Brand Brief completado
    ├── voice_brief.md               ← Voice Brief completado
    ├── contenido/
    │   ├── semana_01.md             ← Copy de cada semana de contenido
    │   ├── semana_02.md
    │   └── calendario.md            ← Calendario mensual completo
    ├── prompts_visuales/
    │   ├── prompts_s01.md           ← Prompts de imagen para semana 1
    │   └── prompts_s02.md
    └── assets/                      ← Imágenes generadas, logos, referencias
```

**Comando de creación de proyecto nuevo:**
```
KAM crea la carpeta: projects/[NOMBRE_CLIENTE]/
Copia todos los archivos de projects/_template/ a la nueva carpeta
Actualiza BRIEF_MEMORIA.md con los datos del cliente
```

---

## 🔢 FLUJO PASO A PASO — PROTOCOLO COMPLETO

---

### FASE 0 — INTAKE (KAM)

**Responsable:** KAM
**Tiempo estimado:** 5-10 min
**Output:** Clasificación del tipo de solicitud

KAM recibe la solicitud del usuario y responde con estas preguntas si faltan datos:

```
INTAKE SOCIAL MEDIA — KAM

1. ¿Es cliente nuevo o ya tiene ADN de marca documentado?
   → Nuevo: activar cuestionario BRAND_DNA_QUESTIONNAIRE.md
   → Existente: cargar BRIEF_MEMORIA.md de projects/[CLIENTE]/

2. ¿Cuál es el objetivo de la campaña?
   → Viralización / Awareness masivo → VIRALGEN modo viral
   → Generación de leads / B2B → LaunchBuzz modo estratégico
   → Lanzamiento de producto → Flujo completo (VIRALGEN + IMAGENOLOGO + LaunchBuzz)
   → Contenido orgánico mensual → VIRALGEN modo calendario

3. ¿En qué plataformas?
   → TikTok / Instagram / Facebook / Pinterest → VIRALGEN (B2C Cultural)
   → LinkedIn / Twitter / Email → LaunchBuzz (B2B Estratégico)
   → Todas → Ambos agentes en paralelo

4. ¿Hay materiales existentes?
   → Logos, fotos de producto, paleta de colores, copy previo

5. ¿Cuál es el deadline?
   → Urgente (<48h): una semana de contenido + prompts prioritarios
   → Normal (1 semana): calendario mensual completo
   → Sin prisa: campaña trimestral con variantes A/B
```

---

### FASE 1 — DISCOVERY DE MARCA (BrandMind)

**Responsable:** BrandMind
**Se activa cuando:** Cliente nuevo **o** actualización de posicionamiento
**Input:** Respuestas al BRAND_DNA_QUESTIONNAIRE.md
**Output:** `brand_brief.md` + `voice_brief.md`
**Se guarda en:** `projects/[CLIENTE]/`

```
BRIEF PARA BRANDMIND:

Actúa como BrandMind para el proyecto [CLIENTE].

Input disponible:
→ Respuestas al cuestionario ADN: [pegar respuestas]
→ Materiales existentes: [logo / colores / web / ninguno]

Tareas:
1. Diagnosticar arquetipo de marca + posicionamiento
2. Definir promesa central y diferenciador no replicable
3. Construir Brand Brief completo (formato brand_brief.md)
4. Construir Voice Brief para VIRALGEN + LaunchBuzz (formato voice_brief.md)

Entregar ambos documentos en formato Markdown listo para guardar.
```

> ⚠️ **REGLA DE ORO:** VIRALGEN y LaunchBuzz NO arrancan sin el Brand Brief de BrandMind.

---

### FASE 2 — ESTRATEGIA VIRAL (VIRALGEN)

**Responsable:** VIRALGEN
**Se activa:** Siempre que haya contenido B2C / viral / plataformas sociales
**Input:** `brand_brief.md` + `voice_brief.md`
**Output:** Diagnóstico psicográfico + Calendario de contenido + Copy completo + Prompts visuales
**Se guarda en:** `projects/[CLIENTE]/contenido/` + `projects/[CLIENTE]/prompts_visuales/`

```
BRIEF PARA VIRALGEN:

Actúa como VIRALGEN para [CLIENTE].

[PEGAR brand_brief.md AQUÍ]
[PEGAR voice_brief.md AQUÍ]

Plataformas: [TikTok / IG / Facebook / todas]
Objetivo: [viralización / awareness / lanzamiento / comunidad]
Semanas de contenido: [X semanas]
Piezas por semana: [X piezas]

Entrega en este orden:
1. Diagnóstico psicográfico de la audiencia (2 párrafos)
2. Concepto filosófico central de la campaña (1 párrafo)
3. Contenido completo semana 1: [piezas listos para publicar con copy, hashtags,
   nota de producción y predicción de viralidad]
4. Prompts visuales para cada pieza (formato IMAGENOLOGO)
5. Calendario mensual completo
```

---

### FASE 3 — PRODUCCIÓN VISUAL (IMAGENOLOGO)

**Responsable:** IMAGENOLOGO
**Se activa:** Cuando VIRALGEN entrega prompts visuales **o** cuando se necesitan imágenes ads de alta fidelidad
**Input:** Prompts entregados por VIRALGEN + `brand_brief.md` (paleta, estética)
**Output:** Prompts refinados listos para ejecutar en Gemini Imagen / Nanobanana
**Se guarda en:** `projects/[CLIENTE]/prompts_visuales/`

```
BRIEF PARA IMAGENOLOGO:

Actúa como IMAGENOLOGO para [CLIENTE].

Input:
→ Prompts base generados por VIRALGEN: [pegar]
→ Paleta de colores de la marca: [hex codes del brand_brief]
→ Estética de referencia: [del brand_brief]
→ Canal de distribución: [Instagram Reel / TikTok / Feed / Ad / OOH]

Tarea:
Refinar cada prompt con la arquitectura de capas completa,
módulos de coherencia de marca y parámetros técnicos 8K.
Entregar prompts listos para ejecutar, uno por pieza visual.
```

---

### FASE 3B — CONTENIDO B2B (LaunchBuzz) [Si aplica]

**Responsable:** LaunchBuzz
**Se activa:** Cuando el cliente tiene audiencia B2B (LinkedIn / Email / Twitter)
**Input:** `voice_brief.md` + copy estratégico de BrandMind
**Output:** Posts LinkedIn + threads Twitter + emails de nurturing
**Se guarda en:** `projects/[CLIENTE]/contenido/`

```
BRIEF PARA LAUNCHBUZZ:

Actúa como LaunchBuzz para [CLIENTE].

[PEGAR voice_brief.md AQUÍ]
[PEGAR copy estratégico de BrandMind si existe]

Canal: [LinkedIn / Twitter / Email]
Objetivo: [awareness B2B / leads / lanzamiento / credibilidad]
Piezas: [X posts LinkedIn + Y tweets + Z emails]
```

> 📌 **Diferencia clave:**
> - **VIRALGEN** = B2C, cultural, viral, emocional (TikTok · IG · Facebook)
> - **LaunchBuzz** = B2B, estratégico, técnico, autoridad (LinkedIn · Twitter · Email)
> - En proyectos mixtos, ambos trabajan en paralelo con el mismo Voice Brief.

---

### FASE 4 — CONSOLIDACIÓN Y ENTREGA (KAM)

**Responsable:** KAM
**Siempre última fase**
**Input:** Todos los outputs de los agentes anteriores
**Output:** Paquete de entrega organizado + BRIEF_MEMORIA.md actualizado

```
CHECKLIST FINAL KAM:

□ brand_brief.md guardado en projects/[CLIENTE]/
□ voice_brief.md guardado en projects/[CLIENTE]/
□ Contenido completo guardado en projects/[CLIENTE]/contenido/semana_XX.md
□ Prompts visuales guardados en projects/[CLIENTE]/prompts_visuales/
□ Calendario mensual en projects/[CLIENTE]/contenido/calendario.md
□ BRIEF_MEMORIA.md actualizado con estado "Entregado" y fecha
□ Notas de iteración y decisiones registradas en BRIEF_MEMORIA.md

REPORTE EJECUTIVO AL USUARIO:
→ ¿Qué se entregó?
→ ¿Listos para publicar? ¿Qué queda pendiente?
→ ¿Qué necesita el cliente aprobar antes de lanzar?
→ ¿Cuál es la siguiente acción recomendada?
```

---

## ⏱️ TIEMPOS ESTIMADOS POR FASE

| Fase | Agente | Tiempo estimado |
|---|---|---|
| Intake + Clasificación | KAM | 5-10 min |
| Cuestionario ADN (cliente llena) | Usuario | 20-40 min |
| Brand Brief + Voice Brief | BrandMind | 10-15 min |
| Estrategia Viral + Contenido 1 semana | VIRALGEN | 15-20 min |
| Refinamiento de prompts visuales | IMAGENOLOGO | 10 min |
| Contenido B2B (si aplica) | LaunchBuzz | 10 min |
| Consolidación + archivo | KAM | 5 min |
| **TOTAL flujo completo** | **Todo el equipo** | **~60-90 min** |

---

## 🔄 REGLAS DE ORQUESTACIÓN KAM

1. **BrandMind siempre va primero** en clientes nuevos. Sin ADN de marca, ningún agente creativo arranca.
2. **VIRALGEN es el núcleo** del flujo social media. Genera la estrategia, el contenido Y los prompts visuales.
3. **IMAGENOLOGO refina** los prompts que VIRALGEN genera — no los crea desde cero para campañas sociales.
4. **LaunchBuzz es paralelo** a VIRALGEN en proyectos mixtos, nunca secuencial.
5. **Todo se guarda** en `projects/[CLIENTE]/` antes de entregar al usuario.
6. **BRIEF_MEMORIA.md se actualiza** al cierre de cada fase, no al final del proyecto.
7. **El usuario no necesita saber** qué agente ejecuta qué — solo necesita ver los entregables y el estado.

---

## 🆘 PROTOCOLOS DE EXCEPCIÓN

```
SI no hay cuestionario completo → KAM hace las preguntas mínimas del intake
   y BrandMind trabaja con lo disponible (brief provisional)

SI el cliente tiene ADN documentado → saltar Fase 1 y arrancar directamente en Fase 2
   (cargar brand_brief.md existente)

SI el deadline es < 24h → producir solo:
   → 3 piezas prioritarias (no el calendario completo)
   → Prompts visuales solo de las 3 piezas
   → Flag en BRIEF_MEMORIA.md: "Brief provisional — completar en siguiente iteración"

SI el cliente rechaza el concepto → volver a VIRALGEN con el feedback específico
   KAM documenta el rechazo y la razón en BRIEF_MEMORIA.md
   VIRALGEN propone concepto alternativo con diferente detonador psicológico
```

---

*SOCIAL_MEDIA_FLOW v1.0 — KAM · HiphaMX Orchestration Layer*
*Agentes involucrados: BrandMind · VIRALGEN · IMAGENOLOGO · LaunchBuzz*
*Almacenamiento: projects/[CLIENTE]/ · Memoria: BRIEF_MEMORIA.md*
