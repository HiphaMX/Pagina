# 📝 PROJECT INTAKE FORM — Dr. Jairo Domínguez Arroyo

## 1. INFORMACIÓN DE LA CUENTA Y CONTACTO
- **Nombre Comercial:** Especialista en Urología | Dr. Jairo Domínguez
- **Especialista:** Dr. Jairo Domínguez Arroyo
- **Giro:** Salud · Urología General, Urología Oncológica y Cirugía Robótica de Mínima Invasión
- **Dirección Sede Ángeles:** Torre B consultorio 409, Av. Montaña Monarca No. 331, Centro, C.P. 58350, Morelia, Michoacán.
- **Dirección Sede La Luz:** Gral. Nicolás Bravo No. 50, Col. Chapultepec Norte, C.P. 58260, Morelia, Michoacán.
- **Teléfonos de Consultorio:** 443 725 5650 / 331 661 2086
- **WhatsApp Oficial:** +52 331 661 2086
- **Email de Contacto y Notificaciones:** r2urodominguez@hotmail.com
- **Dominio Actual:** `https://www.jairodominguez-urologo.com`

---

## 2. ANTECEDENTES Y MOTIVO DE MIGRACIÓN
- **Plataforma Anterior:** Webflow (Sitio cautivo dependiente de suscripciones y CDN de terceros).
- **Necesidad Primaria:**
  - Clonación 100% de la arquitectura visual, informativa y funcional preexistente.
  - Migración al stack unificado de HiphaMX en FastAPI y Vercel.
  - Alojamiento de todos los assets en infraestructura propia (sin riesgos de enlaces rotos o cobros excesivos por tráfico).
  - Integración de notificaciones de prospectos vía API FastAPI con protección anti-spam.
  - Adecuación a los estándares obligatorios de HiphaMX para clientes en firme: Web Agéntica (`llms.txt`), GEO SEO (`robots.txt`), y fallback seguro de correo.

---

## 3. AUDIENCIAS OBJETIVO (BUYER PERSONAS)
1. **Varones Mayores de 45 Años:**
   - Preocupados por la salud prostática (crecimiento prostático, flujo urinario disminuido, levantarse por la noche a orinar).
   - Interesados en alternativas quirúrgicas avanzadas como el láser HoLEP para evitar cirugías abiertas y sondas prolongadas.
2. **Pacientes con Diagnóstico o Sospecha Oncológica:**
   - Pacientes con elevación del Antígeno Prostático Específico (APE), nódulos testiculares, hematuria (sangre en orina) o masas renales.
   - Buscan un cirujano con certificación en Cirugía Robótica Da Vinci y enfoque oncológico estricto.
3. **Pacientes con Litiasis Renal (Piedras en Riñón o Vías Urinarias):**
   - Personas con dolor agudo cólico o diagnóstico de cálculos que buscan pulverizarlos mediante endourología láser sin incisiones dolorosas.
4. **Hombres en Planificación Familiar (Paternidad Satisfecha):**
   - Hombres jóvenes/adultos que buscan vasectomía rápida, segura y ambulatoria.

---

## 4. INVENTARIO DE CONTENIDOS Y PÁGINAS MÍMICAS
- Portada (`index.html`): Hero de bienvenida, sliders clínicos, resumen de técnicas, ubicaciones con Google Maps embebido, convenios de aseguradoras y formulario.
- Diagnóstico (`diagnostico.html`): Procedimientos de detección, análisis clínicos y consultas de prevención.
- Tipos de Cirugía (`cirugias.html`): Comparativa entre cirugía abierta tradicional, laparoscopia, endourología y cirugía robótica.
- Blog (`blog.html`): Concentrador de guías para pacientes.
- 15 Artículos Especializados (`post/*.html`): Cobertura profunda de cálculos, cánceres urológicos, vasectomía y cuidados postoperatorios.
- Preguntas Frecuentes (`preguntas-frecuentes.html`): Dudas de consulta, formas de pago y preparación.
- Trayectoria Profesional (`trayectoria-profesional.html`): Currículum médico y enlace a CV en PDF descargable.
- Aviso de Privacidad (`aviso-de-privacidad.html`): Cumplimiento normativo LFPDPPP.
- Confirmación (`gracias-por-contactarnos.html`): Página de éxito tras solicitar cita.
- Página 404 (`404.html`): Manejo de enlaces no encontrados.

---

## 5. REQUERIMIENTOS TÉCNICOS ESPECÍFICOS
- [x] Sin dependencias de CDN externas de Webflow.
- [x] Manejo de URLs limpias en servidor (`cleanUrls: true`).
- [x] Certificados SSL / HTTPS activos en dominio propio.
- [x] Respaldo de formularios con fallback SMTP corporativo.
- [x] Subfooter institucional con enlace y firma de diseño Hipha.
