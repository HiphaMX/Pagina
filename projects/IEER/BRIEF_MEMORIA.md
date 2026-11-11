# 📋 BRIEF MEMORIA — IEER (Ingeniería Especializada en Energías Renovables)

> *Este archivo es la memoria viva del proyecto. Se actualiza en cada fase. Todo el equipo de agentes (KAM, BrandMind, DesignFlow, SiteSentinel, GEOPilot) lo lee antes de ejecutar.*

**Proyecto ID:** `IEER-202611`  
**Fecha de inicio:** Noviembre 2026  
**Última actualización:** 2026-11-09  
**Responsable KAM:** KAM v2.0  
**Estado:** `[x] Discovery` → `[x] Estrategia (BrandMind)` → `[x] Producción Web (DesignFlow)` → `[x] Modo Demo Desactivado` → `[x] Alta como Cliente en Firme` → `[ ] Validación DNS Dominio Propio`  

---

## 🏢 DATOS DEL CLIENTE

| Campo | Detalle |
|---|---|
| **Nombre de la marca** | IEER (Ingeniería Especializada en Energías Renovables) |
| **Industria / Nicho** | Alta Ingeniería Solar · Micro-Redes · Almacenamiento Industrial en Litio LFP · Sistemas Off-Grid de Lujo |
| **Dominio oficial** | `ieer.com.mx` (y `www.ieer.com.mx`) |
| **URL provisional / preview** | `https://hipha.mx/ieer/` |
| **Canales de contacto** | WhatsApp: [+52 33 3302 5665](https://wa.me/523333025665) · Correo: `lcid@ieer.com.mx` |
| **Titular / Contacto** | Ing. Luis Cid |
| **Cobertura Operativa** | Todo el territorio de la República Mexicana |

---

## 🎯 OBJETIVO DEL PROYECTO

> Consolidar a **IEER** como el referente nacional de ingeniería en micro-redes de alta capacidad y sistemas de almacenamiento inteligente en litio, resolviendo la vulnerabilidad de industrias, el bombeo continuo en el campo agropecuario y la total independencia en residencias de descanso y arquitectura de lujo sin depender de las fluctuaciones o ausencias de CFE.

---

## 🎨 DIRECCIÓN DE ARTE & ESTÉTICA
- **Concepto:** *Organic Nature & Luxury Tech* (Fusión de texturas naturales minerales y precisión de ingeniería).
- **Paleta de Colores:**
  - `Fondo Principal:` `#141a1c` (Deep Slate Pine / Gris carbón forestal oscuro)
  - `Cards & Paneles:` `rgba(20, 27, 28, 0.55)`
  - `Acento de Lujo (Energía):` `#a98567` (Warm Bronze / Bronce tierra)
  - `Acento de Luz (Texto):` `#e3ddd5` (Alabaster Cream)
  - `Bordes sutiles:` `rgba(169, 133, 103, 0.12)`
- **Tipografías:**
  - `Display / Títulos:` *Outfit* (pesos ultra-ligeros para elegancia minimalista)
  - `Tech / Badges:` *Space Grotesk* y *Syncopate*
  - `Acento Signature:` *Google Sans Flex* (Semibold 600)

---

## 🏗️ ARQUITECTURA TÉCNICA DEL SITIO
1. **Landing Principal (`index.html`):**
   - Hero interactivo con simulación de inversor y curva solar en tiempo real (Canvas).
   - Módulo de sectores (Industrial, Agropecuario, Residencial Premium, Cargas Críticas).
   - Radar concéntrico de cobertura nacional (estilo Zerocircle).
   - Formulario de consulta técnica conectado a `/api/contact/ieer`.
   - Botón directo de WhatsApp flotante hacia `+52 33 3302 5665`.
2. **IEER Journal (Artículos Técnicos Especializados):**
   - `articulo-autonomia.html`: La Nueva Era de la Autonomía Energética Industrial.
   - `articulo-calidad-energia.html`: Calidad de Energía y Código de Red.
   - `articulo-offgrid.html`: Integración de Sistemas Off-Grid en Arquitectura Luxury.
3. **Web Agéntica & GEO:**
   - `llms.txt`: Resumen semántico para modelos de lenguaje (Gemini, ChatGPT, Perplexity).
   - `robots.txt`: Permisos explícitos para buscadores y motores de grounding IA.

---

## 🔐 HISTORIAL DE CAMBIOS Y PROTOCOLOS
- **2026-11-09:** Aprobación de la transición de Prospecto a **Cliente en Firme**.
- **2026-11-09:** Desactivación y retiro definitivo del script modular `hipha-demo-guard.js`.
- **2026-11-09:** Configuración de enrutamiento por host `^(www\.)?ieer\.com\.mx$` en `vercel.json`.
- **2026-11-09:** Implementación de endpoint de backend `/api/contact/ieer` y funciones SMTP de fallback seguro en `mailer.py`.
- **2026-11-09:** Incorporación a `AgencyClient` en base de datos y al monitoreo continuo de `WebGuardian`.
- **2026-11-10:** Integración de la sección de Comprobación de Experiencia y Certeza Operativa debajo del Hero1 (estilo Design Flow, bento grid de 3 pilares: tiempo de respuesta ≤ 24h, ciclo integral de 4 etapas, y alcances de 5 kW a +100 kW en laboratorios, fábricas, clínicas, spa y hotelería). Despliegue en producción verificado.
