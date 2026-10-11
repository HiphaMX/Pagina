#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════╗
║                HiphaMX — FlowCast Director CLI                     ║
║     Generador de Shotlists y Prompts para Google Flow (Veo 3.1)    ║
║                                                                    ║
║  Uso:                                                              ║
║    python3 scripts/flowcast_director.py                            ║
║    python3 scripts/flowcast_director.py --script "Tu guion aquí"   ║
║    python3 scripts/flowcast_director.py --file ruta/al/guion.txt   ║
╚════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOWCAST_DIR = os.path.join(BASE_DIR, "flowcast")
EPISODES_DIR = os.path.join(FLOWCAST_DIR, "episodes")

def load_profile(filename):
    path = os.path.join(FLOWCAST_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def split_into_beats(text, target_words_per_beat=16):
    """
    Divide un texto en segmentos (beats) de aproximadamente 14-18 palabras,
    adecuado para 5 a 8 segundos de dicción hablada.
    """
    # Limpiar saltos de línea excesivos
    clean_text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.?!;:])\s+', clean_text)
    
    beats = []
    current_beat = []
    current_count = 0
    
    for s in sentences:
        words = s.split()
        if not words:
            continue
        
        if current_count + len(words) <= target_words_per_beat + 6:
            current_beat.append(s)
            current_count += len(words)
        else:
            if current_beat:
                beats.append(" ".join(current_beat))
            current_beat = [s]
            current_count = len(words)
            
    if current_beat:
        beats.append(" ".join(current_beat))
        
    return beats if beats else [text]

def generate_shotlist(script_text, episode_title="Episodio Sin Título"):
    beats = split_into_beats(script_text)
    
    # Configuraciones de cámara alternantes
    # Los 3 Ángulos Canónicos Oficiales ("Mi Casa" Setup)
    camera_setups = [
        {
            "name": "Camera 1 — Frontal Directa (Apertura / Conexión)",
            "lens": "Straight-on medium close-up shot, eye-level, static camera, 50mm lens, direct eye contact with lens",
            "action": "Looking directly into the camera lens with confident warm expression, speaking naturally with subtle head tilts, Shure SM7B mic anchored in lower left foreground.",
            "movement": "Static framing, perfectly centered eye-level perspective."
        },
        {
            "name": "Camera 2 — Tres Cuartos 45° (Conversacional Natural)",
            "lens": "45-degree conversational angle shot, medium close-up, 50mm lens, shallow depth of field, Pink Floyd poster and Soul Shine sign visible in background",
            "action": "Speaking naturally in 3/4 angle toward the microphone, relaxed conversational cadence, authentic eye blinks and subtle gestures.",
            "movement": "Subtle slow micro-dolly in toward the host."
        },
        {
            "name": "Camera 3 — Perfil Cerrado 60°-70° (Énfasis e Intimidad)",
            "lens": "Tight side profile close-up shot, 65-degree lateral angle, 85mm portrait lens with creamy background bokeh, crisp focus on facial profile and beard texture",
            "action": "Articulating key insight with focused expression, side profile highlighting salt-and-pepper beard, leaning slightly forward with authority.",
            "movement": "Slow intimate push-in emphasizing dialogue significance."
        }
    ]
    
    out = []
    out.append(f"# 🎬 Shotlist Google Flow (Veo 3.1) — {episode_title}\n")
    out.append(f"> **Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    out.append(f"> **Total de Tomas:** {len(beats)} clips (estimados en {len(beats)*7}s aprox.)")
    out.append("> **Ingredientes:** `[AVATAR_HOST]` (Avatar Cloned Profile) | `[STUDIO_SET]` (Studio Anchor Profile)\n")
    out.append("---\n")
    
    current_time = 0
    
    for i, beat in enumerate(beats):
        setup = camera_setups[i % len(camera_setups)]
        duration = max(5, min(8, int(len(beat.split()) / 2.2)))
        start_t = f"{current_time//60:02d}:{current_time%60:02d}"
        end_t = f"{(current_time+duration)//60:02d}:{(current_time+duration)%60:02d}"
        current_time += duration
        
        out.append(f"### 🎥 SHOT {i+1} ({start_t} - {end_t}) — {setup['name']}")
        out.append(f"- **Guion / Audio:** *\"{beat}\"*")
        out.append(f"- **Tipo de Plano:** {setup['name']}")
        out.append(f"- **Movimiento:** {setup['movement']}\n")
        
        prompt_text = (
            f"Cinematography: {setup['lens']}.\n"
            f"Subject: Consistent host [AVATAR_HOST], Hispanic male late 30s, short dark curly textured hair, "
            f"thick full beard with distinctive salt-and-pepper gray hair on chin, wearing solid matte black crewneck t-shirt, "
            f"sitting in black leather chair behind matte black podcast desk.\n"
            f"Action: {setup['action']}\n"
            f"Context: In [STUDIO_SET] 'Soul Shine' podcast studio, dark gallery wall with framed 2001 A Space Odyssey and Pink Floyd posters, "
            f"acrylic 'Soul Shine' wall sign, Shure SM7B dynamic microphone on articulated boom arm in sharp foreground, atmospheric ambient smoke.\n"
            f"Lighting & Style: Hidden low-angle floor uplighting softly illuminating atmospheric smoke in ethereal dual-tone purple and emerald green, "
            f"soft warm key light on host face, subtle edge rim light, rich dark shadows, pristine 4K film texture, high dynamic range.\n"
            f"Negative: no harsh overhead spotlight, no top down beam of light, no visible lamps on floor, no face warping, no distorted hands, no floating microphone, no lip sync drift, no extra fingers, no camera jitter, no morphing, no uncanny valley artifacts."
        )
        
        out.append("```text")
        out.append(prompt_text)
        out.append("```\n")
        out.append("---\n")
        
    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser(description="HiphaMX FlowCast Director CLI")
    parser.add_argument("--script", type=str, help="Texto o guion del episodio")
    parser.add_argument("--file", type=str, help="Ruta a archivo de texto con el guion")
    parser.add_argument("--title", type=str, default="Episodio_Podcast", help="Título del episodio")
    parser.add_argument("--save", action="store_true", help="Guardar la shotlist en flowcast/episodes/")
    args = parser.parse_args()
    
    script_content = ""
    if args.script:
        script_content = args.script
    elif args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            script_content = f.read()
    else:
        print("\033[1;36m=== 🎙️ HiphaMX FlowCast Director CLI ===\033[0m")
        print("Introduce el guion o las ideas de tu podcast (presiona Enter y luego Ctrl+D cuando termines):\n")
        try:
            script_content = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nCancelado.")
            return

    if not script_content.strip():
        print("❌ Error: No se proporcionó ningún guion.")
        return

    shotlist = generate_shotlist(script_content, args.title)
    print("\n" + shotlist)
    
    if args.save or not (args.script or args.file):
        os.makedirs(EPISODES_DIR, exist_ok=True)
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', args.title.lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"shotlist_{safe_title}_{timestamp}.md"
        filepath = os.path.join(EPISODES_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(shotlist)
        print(f"\n\033[1;32m✓ Shotlist guardada exitosamente en:\033[0m {filepath}")

if __name__ == "__main__":
    main()
