# 🎙️ Studio Profile — Set Canónico "Soul Shine" (Mi Casa)

> **PROPÓSITO:** Establecer el estudio "Soul Shine" como el set base e invariable de todas las producciones ("Mi Casa"), garantizando la misma naturalidad, iluminación y los 3 ángulos de cámara preferidos.

---

## 📌 Configuración en Google Flow

| Parámetro | Valor |
|---|---|
| **Identificador en Flow** | `[INGREDIENT: STUDIO_SET]` |
| **Referencia de Set (Master)** | `flowcast/assets/studio_reference.jpg` |
| **Estética Visual** | "Soul Shine" Podcast Studio — Dark Cinematic Rock & Cinema Gallery |
| **Regla de Continuidad** | Set invariable: misma naturalidad, cuadros, haz de luz cenital y micrófono. |

---

## 🎥 Los 3 Ángulos Canónicos de Cámara

### 1. Cámara A — Frontal Directa (Conexión y Apertura)
- **Referencia Visual:** `flowcast/assets/angle_frontal.png`
- **Encuadre:** Plano medio corto frontal (*straight-on medium close-up*), lente 50mm, a la altura de los ojos.
- **Composición:** Mirada directa al lente/audiencia, micrófono Shure SM7B en el tercio inferior izquierdo, fondo equilibrado.
- **Función:** Bienvenida, hooks de apertura, conclusiones y llamadas a la acción.
- **Prompt:** `Cinematography: Straight-on medium close-up shot, eye-level, static camera, 50mm lens, direct eye contact with lens.`

### 2. Cámara B — Tres Cuartos 45° (Conversacional Natural)
- **Referencia Visual:** `flowcast/assets/angle_45deg.png`
- **Encuadre:** Plano a 45 grados (*three-quarter conversational angle*), lente 50mm o 85mm, profundidad de campo suave.
- **Composición:** Rostro en ángulo de 3/4 mirando hacia el micrófono/espacio de conversación, visible póster de Pink Floyd y letrero Soul Shine al fondo.
- **Función:** Explicaciones continuas, anécdotas, storytelling y desarrollo del tema.
- **Prompt:** `Cinematography: 45-degree conversational angle shot, medium close-up, shallow depth of field, natural speaking posture toward microphone.`

### 3. Cámara C — Perfil Cerrado 60°-70° (Énfasis e Intimidad)
- **Referencia Visual:** `flowcast/assets/angle_profile.png`
- **Encuadre:** Primer plano cerrado de perfil lateral (*tight side profile close-up*), lente 85mm con bokeh cremoso.
- **Composición:** Enfoque nítido en el perfil facial, textura de la barba y dicción, micrófono Shure SM7B en primer plano bajo, luz de recorte dramática.
- **Función:** Datos reveladores, frases de alto impacto, reflexión profunda o conceptos científicos clave.
- **Prompt:** `Cinematography: Tight side profile close-up shot, 60-degree lateral angle, 85mm portrait lens, crisp focus on facial profile and beard.`

---

## 🏛️ Elementos Invariables del Set ("Mi Casa")

- **Gallery Wall:** Muro carbón mate con pósters enmarcados:
  - *"STANLEY KUBRICK 2001: a space odyssey"* (estación espacial).
  - *"PINK FLOYD - The Dark Side of the Moon"* (prisma y espectro).
  - Fotos clásicas en blanco y negro de Stanley Kubrick.
  - Letrero acrílico/neón en relieve: *"Soul Shine"* con isotipo floral circular.
- **Mesa & Micrófono:** Mesa negra mate con micrófono **Shure SM7B** en brazo articulado siempre anclado en primer plano bajo.
- **Iluminación de Autor (Atmósfera Mística & Orgánica):**
  - **Sin haz cenital superior.** Luz principal suave y difusa sobre el rostro del host (key light cálida natural).
  - **Humo Iluminado desde el Piso:** Neblina baja y humo atmosférico sutil iluminado desde el suelo por luces ocultas (*hidden floor uplighting*) que proyectan un gradiente etéreo en tonos **púrpura y verde esmeralda** (*dual-tone purple and emerald green glowing through the smoke*), sin mostrar los focos ni fuentes directas.
  - Sombras profundas en el fondo para resaltar la textura de los pósters y el letrero "Soul Shine".

---

## 📝 Prompt Anchor del Set para Veo 3.1

```text
Context: In [STUDIO_SET] "Soul Shine" podcast studio ("Mi Casa"), dark gallery wall with framed 2001 A Space Odyssey and Pink Floyd posters, acrylic "Soul Shine" wall sign, Shure SM7B dynamic microphone on articulated boom arm in sharp foreground, atmospheric ambient haze.
Lighting & Style: Hidden floor uplighting subtly illuminating the rising smoke in ethereal dual-tone purple and emerald green, soft warm key light on host, gentle edge rim light, moody dark contrast, 4K film texture.
Negative: no harsh overhead spotlight, no top down beam of light, no direct light fixtures on floor.
```
