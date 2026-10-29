# 📋 BRIEF MEMORIA — Dr. Jairo Domínguez Arroyo (Cirugía Urológica y Robótica)

> *Este archivo es la memoria viva institucional y técnica del proyecto de Dr. Jairo Domínguez Arroyo en HiphaMX. Documenta la identidad clínica, el stack técnico, las decisiones estratégicas de migración y la arquitectura de conversión para el consultorio.*

**Proyecto ID:** `DrJairoDominguez-202610`  
**Fecha de Onboarding / Migración:** 2026-10-28  
**Origen:** Migración 100% de Webflow a HiphaMX FastAPI / Vercel  
**Responsable KAM:** KAM HiphaMX  
**Estado:** `[x] Discovery` → `[x] Clonación 100%` → `[x] Independencia de Assets` → `[x] Backend & SMTP` → `[x] Producción`

---

## 🏢 DATOS GENERALES DEL CLIENTE

| Campo | Detalle |
|---|---|
| **Especialista Titular** | Dr. Jairo Domínguez Arroyo |
| **Especialidad Médica** | Cirujano Urólogo · Alta Especialidad en Urología Oncológica y Cirugía Robótica |
| **Formación Académica** | Médico Cirujano y Partero por la Universidad Michoacana de San Nicolás de Hidalgo (UMSNH). Especialidad en Urología por la Universidad de Guadalajara (UdeG). |
| **Certificaciones** | Urólogo Certificado por el Consejo Nacional Mexicano de Urología (CONAMEU). Certificación Oficial en Cirugía Robótica Da Vinci. |
| **Sede 1** | **Hospital Ángeles Morelia**: Torre B, Consultorio 409, Av. Montaña Monarca No. 331, Centro, C.P. 58350, Morelia, Michoacán. |
| **Sede 2** | **Sanatorio La Luz**: Gral. Nicolás Bravo No. 50, Col. Chapultepec Norte, C.P. 58260, Morelia, Michoacán. |
| **Teléfonos de Citas** | 443 725 5650 y 331 661 2086 |
| **WhatsApp Directo** | +52 331 661 2086 |
| **Correo Electrónico** | r2urodominguez@hotmail.com |
| **Dominio Canónico** | `https://www.jairodominguez-urologo.com` |
| **Ruta en Hipha** | `projects/Dr. Jairo Dominguez/` (`hipha.mx/jairo-dominguez`) |

---

## 🎯 OBJETIVO DEL PROYECTO Y MIGRACIÓN

> Consolidar la presencia digital del **Dr. Jairo Domínguez Arroyo** como el cirujano urólogo de referencia en Morelia y el estado de Michoacán para tratamientos de mínima invasión (Cirugía Robótica Da Vinci, láser HoLEP para próstata, endourología para piedras/litiasis y laparoscopia avanzada), liberando el activo digital de la dependencia de Webflow, optimizando los tiempos de carga al alojar el 100% de assets localmente, habilitando captura de leads con notificación por correo y preparando el sitio para recomendación en motores de IA (GEO y Web Agéntica).

---

## 🩺 PILARES CLÍNICOS Y PROPUESTA DE VALOR

1. **Cirugía Robótica de Mínima Invasión:**
   - Asistida por robot Da Vinci: máxima destreza quirúrgica tridimensional, reducción del sangrado, menor dolor y preservación funcional (continencia y erección).
2. **Enucleación Prostática con Láser de Holmio (HoLEP):**
   - La técnica más moderna para hiperplasia prostática benigna sin heridas en la piel, ideal para próstatas de gran tamaño con recuperación casi inmediata.
3. **Urología Oncológica:**
   - Manejo integral y quirúrgico de cáncer urológico (próstata, riñón, vejiga, testículo y pene).
4. **Endourología y Litiasis Renal:**
   - Pulverización de piedras y cálculos en riñón, uréter y vejiga con láser y procedimientos endoscópicos ambulatorios.
5. **Calidez Humana y Ética:**
   - Diagnósticos claros, sin sobretratamientos, explicando al paciente con franqueza y cercanía las alternativas reales a su alcance.

---

## 🛡️ CONVENIOS CON ASEGURADORAS (SGMM)

El consultorio del Dr. Jairo Domínguez trabaja de forma constante con las principales aseguradoras:
- **GNP Seguros**
- **MetLife**
- **Axa Seguros**
- **Seguros Monterrey New York Life**
- Cobertura directa o apoyo integral en trámite de reembolso médico.

---

## 💻 STACK TÉCNICO Y ARQUITECTURA DIGITAL HIPHAMX

| Componente | Implementación |
|---|---|
| **Frontend** | HTML5 semántico higienizado, CSS encapsulado de Webflow desvinculado de CDN, componentes de interacción nativos. |
| **Assets Locales** | 89 archivos (imágenes, favicons, fuentes, SVG, PDF curricular de 2.6MB) alojados en `/assets/` sin enlaces externos a Webflow. |
| **Formularios de Contacto** | Script `contact-form.js` conectado asíncronamente con validación de inputs y Honeypot anti-spam. |
| **Backend API** | FastAPI: `POST /api/projects/jairo-dominguez` en `app/api/projects/jairo_dominguez.py`. |
| **Emails Transaccionales** | `app/core/mailer.py` con `_prepare_project_email` (garantía SPF/DMARC y fallback automático al SMTP de Hipha). |
| **Web Agéntica & GEO** | `/llms.txt` estructurado y `/robots.txt` con permisos explícitos para agentes de IA (Google Gemini, GPTBot, PerplexityBot, ClaudeBot). |
| **Enrutamiento** | Reglas dedicadas en `vercel.json` tanto para el dominio en firme `jairodominguez-urologo.com` como para el subpath de agencia `hipha.mx/jairo-dominguez/`. |
