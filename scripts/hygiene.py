#!/usr/bin/env python3
import os
import sys
import shutil
import math

# Colores ANSI para formatear la salida en terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_directory_size(path):
    """Calcula el tamaño total de un directorio en bytes."""
    total_size = 0
    if not os.path.exists(path):
        return 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Evitar enlaces simbólicos rotos
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(size_bytes):
    """Formatea bytes a KB, MB o GB."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.log(size_bytes) / math.log(1024)) if size_bytes > 0 else 0
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_size_math(size_bytes):
    """Regresa formato en MB para comparaciones."""
    return size_bytes / (1024 * 1024)

def run_hygiene_check():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"\n{BLUE}{BOLD}=== INICIANDO EXAMEN DE HIGIENE Y OPTIMIZACIÓN DE ESPACIO ==={RESET}\n")
    print(f"Directorio Raíz: {root_dir}\n")

    # 1. Analizar pesos de directorios clave
    directories = {
        "Historial de Git (.git)": os.path.join(root_dir, ".git"),
        "Subproyectos Locales (Hipha Projects)": os.path.join(root_dir, "Hipha Projects"),
        "Entorno Virtual (venv)": os.path.join(root_dir, "venv"),
        "Entorno PDF (venv_pdf)": os.path.join(root_dir, "venv_pdf"),
        "Producción Estática (projects)": os.path.join(root_dir, "projects"),
        "Backend Core (app)": os.path.join(root_dir, "app"),
    }

    print(f"{BOLD}1. Peso de Carpetas:{RESET}")
    total_size = 0
    for name, path in directories.items():
        if os.path.exists(path):
            size = get_directory_size(path)
            total_size += size
            color = GREEN
            if get_size_math(size) > 300:
                color = RED
            elif get_size_math(size) > 100:
                color = YELLOW
            print(f"  • {name}: {color}{BOLD}{format_size(size)}{RESET}")
        else:
            print(f"  • {name}: {YELLOW}No presente{RESET}")
    
    print(f"\n  Tamaño Total Detectado: {BLUE}{BOLD}{format_size(total_size)}{RESET}")
    print("-" * 60)

    # 2. Detectar carpetas node_modules o .next mal ubicadas (fuera de Hipha Projects)
    print(f"\n{BOLD}2. Escaneo de Dependencias Fuera de la Zona Segura:{RESET}")
    danger_folders = []
    for root, dirs, files in os.walk(root_dir):
        # Evitar buscar dentro de carpetas ya ignoradas
        if "Hipha Projects" in root or "venv" in root or ".git" in root:
            continue
        for d in dirs:
            if d in ["node_modules", ".next"]:
                full_path = os.path.join(root, d)
                danger_folders.append(full_path)
    
    if danger_folders:
        print(f"  {RED}{BOLD}⚠️ ¡Alerta! Se encontraron carpetas pesadas fuera de 'Hipha Projects':{RESET}")
        for folder in danger_folders:
            print(f"    - {folder}")
        print(f"  {YELLOW}Recomendación: El despliegue de Vercel fallará si estas carpetas no se eliminan.{RESET}")
    else:
        print(f"  {GREEN}✓ Excelente: No hay dependencias pesadas ni cachés en zonas de producción.{RESET}")
    
    print("-" * 60)

    # 3. Escanear archivos individuales gigantes (> 10MB)
    print(f"\n{BOLD}3. Archivos Gigantes (> 10 MB):{RESET}")
    large_files = []
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "venv" in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                size = os.path.getsize(fp)
                if get_size_math(size) > 10:
                    large_files.append((fp, size))
    
    if large_files:
        print(f"  {YELLOW}⚠️ Archivos detectados que podrían sobrepasar los límites de Git y Vercel:{RESET}")
        for fp, size in large_files:
            print(f"    - {os.path.basename(fp)} ({format_size(size)}) en: {fp}")
    else:
        print(f"  {GREEN}✓ Excelente: No se detectaron archivos individuales gigantes.{RESET}")

    print("-" * 60)

    # 4. Ofrecer limpieza de basura automática
    print(f"\n{BOLD}4. Limpieza Automática de Archivos Basura (.DS_Store / Logs):{RESET}")
    garbage_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f == ".DS_Store" or f in ["stderr.txt", "stdout.txt"] and os.path.getsize(os.path.join(root, f)) == 0:
                garbage_files.append(os.path.join(root, f))
    
    if garbage_files:
        print(f"  Se encontraron {len(garbage_files)} archivos basura listos para ser eliminados.")
        for g in garbage_files:
            try:
                os.remove(g)
            except Exception as e:
                pass
        print(f"  {GREEN}✓ Saneado: Todos los archivos temporales de sistema (.DS_Store) y logs vacíos han sido eliminados.{RESET}")
    else:
        print(f"  {GREEN}✓ Limpio: No hay archivos basura de sistema en el directorio.{RESET}")
        
    print(f"\n{BLUE}{BOLD}=== EXAMEN DE HIGIENE CONCLUIDO ==={RESET}\n")

if __name__ == "__main__":
    run_hygiene_check()
