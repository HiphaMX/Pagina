#!/usr/bin/env python3
"""
HiphaMX FlowCast — Conversor de Audio para Google Flow
Convierte grabaciones de celular (.m4a, .aac, .mp3, etc.) a formato WAV broadcast (16-bit, 48kHz, Mono)
optimizado para sincronización labial (lip-sync) en Veo 3.1.
"""

import os
import sys
import subprocess

def convert_to_flow_wav(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"❌ Error: El archivo no existe: {input_path}")
        return False
        
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    if output_path is None:
        target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flowcast", "audio")
        os.makedirs(target_dir, exist_ok=True)
        output_path = os.path.join(target_dir, f"{base_name}_flow.wav")

    # Comando nativo de macOS afconvert (16-bit Little-Endian PCM @ 48kHz, Mono)
    cmd = [
        "afconvert",
        "-f", "WAVE",
        "-d", "LEI16@48000",
        "-c", "1",
        input_path,
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Audio convertido con éxito:")
        print(f"  Entrada: {input_path}")
        print(f"  Salida (Google Flow Ready): {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al convertir audio: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/convert_audio.py <archivo_de_audio>")
        sys.exit(1)
    convert_to_flow_wav(sys.argv[1])
