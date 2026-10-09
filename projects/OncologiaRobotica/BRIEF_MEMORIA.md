# 📋 BRIEF MEMORIA — Oncología Robótica

> *Este archivo es la memoria viva del proyecto. Se actualiza en cada fase. Todo el equipo de agentes (KAM, BrandMind, DesignFlow, SiteSentinel, GEOPilot) lo lee antes de ejecutar.*

**Proyecto ID:** `OncologiaRobotica-202610`  
**Fecha de inicio:** 2026-10-09  
**Última actualización:** 2026-10-09  
**Responsable KAM:** KAM v2.0  
**Estado:** `[x] Discovery` → `[ ] Estrategia (BrandMind)` → `[ ] Producción (DesignFlow)` → `[ ] QA (SiteSentinel)` → `[ ] Despliegue`  

---

## 🏢 DATOS DEL CLIENTE

| Campo | Detalle |
|---|---|
| **Nombre de la marca** | Oncología Robótica |
| **Industria / Nicho** | Cirugía Robótica de Alta Especialidad · Oncología Quirúrgica · Urología Oncológica |
| **Tecnología Principal** | Sistema Quirúrgico Da Vinci Xi |
| **Sitio web provisional** | `https://hipha.mx/oncologia-robotica` |
| **Dominio objetivo** | `oncologiarobotica.com.mx` (en proceso de confirmación) |
| **Canales de contacto** | WhatsApp de Atención Rápida / Formulario Web Seguro |
| **Contacto del proyecto** | Equipo Médico y Dirección Quirúrgica |

---

## 🎯 OBJETIVO DEL PROYECTO

> Posicionar a **Oncología Robótica** como el centro de referencia líder en cirugía robótica oncológica de mínima invasión con tecnología Da Vinci en México, destacando la máxima precisión milimétrica, preservación funcional de órganos, menor sangrado, recuperación postoperatoria acelerada y el abordaje oncológico más seguro para pacientes en tratamiento de cáncer.

---

## ❓ RESPUESTAS AL CUESTIONARIO DE ADN DE MARCA

> *Se actualizará con el retorno del BRAND_DNA_QUESTIONNAIRE.md por parte del cliente.*

**P1 — El momento fundacional:**
> La necesidad de ofrecer a los pacientes con diagnóstico de cáncer una alternativa quirúrgica que trascienda la cirugía abierta traumática, brindando una visión tridimensional magnificada en alta definición y una destreza instrumental que supera los límites de la mano humana.

**P2 — El enemigo de la marca:**
> El miedo y la desinformación ante una cirugía de cáncer, el trauma quirúrgico innecesario de las técnicas convencionales, y las secuelas funcionales que disminuyen la calidad de vida futura del paciente.

**P3 — La transformación del paciente:**
> De la incertidumbre, angustia y temor a secuelas graves tras un diagnóstico de tumor o cáncer, a la tranquilidad de ser tratado con la tecnología médica más avanzada del mundo por cirujanos con alta certificación internacional, logrando erradicar la enfermedad con rápida reintegración a su vida activa.

**P4 — La personalidad humana:**
> Autoridad médica intachable, tecnología vanguardista, profunda empatía humana, serenidad y transparencia.

**P5 — La audiencia en crisis:**
> Pacientes recién diagnosticados con cáncer o tumores (próstata, riñón, vejiga, digestivo, ginecológico) y sus familiares directos que buscan segundas opiniones y la mejor alternativa con menor riesgo de complicaciones.

**P6 — La idea filosófica:**
> La ciencia y la robótica no sustituyen al médico; potencian su criterio para cuidar lo más sagrado: la vida y la dignidad del ser humano.

**P7 — El territorio estético:**
> Dark Mode tecnológico y médico premium: azules quirúrgicos profundos (`#040B14`, `#0A192F`), acentos cian/turquesa de alta tecnología médica (`#00F2FE`, `#4FACFE`), acabados en cristal esmerilado (*glassmorphism*), tipografías limpias y legibles (*Outfit* e *Inter*).

**P8 — La promesa imposible de copiar:**
> El balance perfecto entre la mayor precisión quirúrgica robótica (sistema Da Vinci Xi) y un acompañamiento oncológico personalizado con enfoque de preservación funcional integral.

**P9 — El contenido que vive en la mente:**
> Demostraciones claras de cómo funciona el robot Da Vinci, comparativas honestas de recuperación vs. cirugía abierta, y testimonios de pacientes que retomaron su vida normal en días.

**P10 — El legado:**
> Transformar el estándar del tratamiento quirúrgico del cáncer en la región hacia un paradigma de mínima invasión y preservación de calidad de vida.

---

## 🧠 DIAGNÓSTICO BRANDMIND (Base Estratégica)

### Arquetipo de Marca
- **Primario:** El Sabio / El Mago (Maestría técnica, transformación mediante ciencia y tecnología de punta).
- **Secundario:** El Cuidador (Compasión, empatía ante la vulnerabilidad del paciente con cáncer).

### Promesa Central
> *"Máxima precisión robótica contra el cáncer. Mínima invasión para tu vida."*

### Paleta de Emociones
- **Queremos que sientan:** Seguridad absoluta, esperanza fundada, alivio al saber que están en manos de tecnología punta, claridad y respaldo.
- **NO queremos que sientan:** Frialdad maquinal, temor ante la palabra "robot", distanciamiento médico o sensacionalismo.

---

## 📦 ENTREGABLES DEL PROYECTO

| Entregable | Agente | Archivo | Estado |
|---|---|---|---|
| Brief Memoria | KAM | `BRIEF_MEMORIA.md` | ✅ Completado |
| Intake Form | KAM | `PROJECT_INTAKE_FORM.md` | ✅ Completado |
| Cuestionario ADN de Marca | BrandMind | `BRAND_DNA_QUESTIONNAIRE.md` | ✅ Completado |
| Brand Brief | BrandMind | `brand_brief.md` | 🔄 Pendiente de Discovery |
| Voice Brief | BrandMind | `voice_brief.md` | 🔄 Pendiente de Discovery |
| Web Agéntica (LLMs) | GEOPilot | `llms.txt` | ✅ Completado |
| Robots Directives | GEOPilot | `robots.txt` | ✅ Completado |
| Landing Page Prototipo | DesignFlow | `index.html` | ✅ Completado |
| Backend & SMTP Fallback | CodeGuardian | `app/api/projects/oncologia_robotica.py` | ✅ Completado |
| QA & Validación | SiteSentinel | Checklist QA | ⏳ En espera de ejecución |

---

## 📝 NOTAS Y DECISIONES

- **2026-10-09 (KAM):** Se apertura formalmente el proyecto. Se configuran variables de entorno con fallback automático al SMTP general de la agencia (`HIPHA`) para blindar el canal de correos frente a políticas SPF/DMARC mientras se aprovisionan las credenciales propias del cliente.
- **2026-10-09 (GEO):** Se crea `llms.txt` y `robots.txt` con permisos expresos para `Google-Extended`, `GPTBot`, `OAI-SearchBot`, `PerplexityBot` y `ClaudeBot` para asegurar el posicionamiento en motores de IA generativa.

---

*Generado por KAM v2.0 — HiphaMX Orchestration Layer*
