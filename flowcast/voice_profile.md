# 🎙️ Voice Profile — Cadencia y Dicción (El Wero Silvestre)

> **PROPÓSITO:** Estandarizar el ritmo, entonación, pausas y energía vocal para sincronización en Google Flow.

---

## 🧬 Identidad Vocal

| Parámetro | Configuración |
|---|---|
| **Tono & Registro** | Barítono cálido, conversacional y reflexivo |
| **Acento / Región** | Español de México (neutro-natural, auténtico, sin acento forzado) |
| **Tempo / Velocidad** | Medio-pausado (~120-130 palabras por minuto) |
| **Nivel de Energía** | Íntimo, magnético, cercano (estilo *The Diary of a CEO* o charla entre amigos) |

---

## 🎼 Marcadores Prosódicos para el Guion

Para forzar al modelo a respetar pausas y énfasis:
- **`...` (Pausa reflexiva de 1s):** Para separar ideas y tomar aire.
- **`--` (Quiebre de ritmo):** Para enfatizar un contraste.
- **MAYÚSCULAS o *Cursiva*:** Para palabras con mayor proyección y brillo vocal.

### Ejemplo de Marcación:
> *"Hola... soy el Wero Silvestre. Poco a poco... descubriremos juntos los beneficios de la microdosificación."*

---

## 🚀 Estrategias de Ejecución en Google Flow

### Ruta A: Pipeline Audio-Driven (Recomendada)
1. Graba las líneas con tu celular o Shure SM7B (clips limpios de 6-8s).
2. Sube el audio a la línea de tiempo de Google Flow.
3. Veo 3.1 anima el avatar directamente sobre tu dicción, aire y ritmo real.

### Ruta B: Directiva Prosódica en Prompt (Veo 3.1)
```text
Audio & Delivery: Natural warm male voice, Mexican conversational Spanish, relaxed thoughtful pacing, clear articulation, slight vocal fry, deliberate natural breathing pauses.
```
