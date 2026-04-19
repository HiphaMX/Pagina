#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║         HiphaMX — Agent Control Panel               ║
║         Ejecutar: python3 agents.py                  ║
║                                                      ║
║  Uso directo:                                        ║
║    python3 agents.py             → menú interactivo  ║
║    python3 agents.py kam         → ir a KAM          ║
║    python3 agents.py branding    → ir a BrandMind    ║
║    python3 agents.py design      → ir a DesignFlow   ║
║    python3 agents.py --list      → listar agentes    ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import textwrap

# ─── ANSI Colors ────────────────────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    @staticmethod
    def fg(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg(r, g, b):
        return f"\033[48;2;{r};{g};{b}m"


# Brand colors from HiphaMX branding.md
CYAN    = C.fg(6, 182, 212)
MAGENTA = C.fg(192, 38, 211)
BLUE    = C.fg(59, 130, 246)
MUTED   = C.fg(100, 116, 139)
WHITE   = C.fg(241, 245, 249)
BG_DARK = C.bg(5, 8, 16)

# ─── Agent Data ─────────────────────────────────────────────────────────────

AGENTS = [
    {
        "id": 1,
        "key": "kam",
        "name": "KAM",
        "icon": "🎯",
        "color": C.fg(6, 182, 212),       # Cyan — marca HiphaMX (agente principal)
        "role": "Key Account Manager · Director de Orquesta",
        "file": "AGENT_KAM.md",
        "badge": "★ HABLA CON ÉL PRIMERO",
        "tags": ["orquestador", "proyecto", "brief", "cliente", "plan", "coordinar", "inicio"],
        "when_to_use": [
            "Empezar cualquier proyecto nuevo — él define qué agentes activar",
            "No sabes qué agente usar o en qué orden",
            "Quieres un plan completo antes de ejecutar",
            "Necesitas un reporte o propuesta para presentar al cliente",
            "Tienes múltiples entregables y quieres que alguien los coordine",
        ],
        "activation": """Actúa como KAM, el agente orquestador de HiphaMX.

Tengo un nuevo proyecto:
- Cliente / Proyecto: [nombre]
- Objetivo: [qué quiero lograr]
- Materiales disponibles: [logo / fotos / web actual / ninguno]
- Deadline: [fecha o "sin prisa"]

Tu tarea:
1. Hacerme las preguntas de intake que necesites
2. Proponerme el plan con agentes, fases y entregables
3. Guiarme paso a paso en la activación de cada agente""",
    },
    {
        "id": 2,
        "key": "brandmind",
        "name": "BrandMind",
        "icon": "🧠",
        "color": C.fg(168, 85, 247),      # Purple — creatividad estratégica
        "role": "Brand Strategist · UX Architect · Copywriter · Visual Director",
        "file": "AGENT_BRANDMIND.md",
        "badge": "PREREQUISITO para DesignFlow",
        "tags": ["branding", "marca", "ux", "copy", "imagen", "foto", "prompt", "arquetipo",
                 "posicionamiento", "estrategia", "gemini", "campaña visual", "logo", "publicidad"],
        "when_to_use": [
            "Definir la identidad y posicionamiento de una marca",
            "Crear el brief estratégico antes de diseñar la web",
            "Escribir copy: H1, CTAs, secciones, emails, pitches",
            "Generar prompts para imágenes publicitarias (Gemini Imagen)",
            "Crear la voz de marca y guía de contenido para redes",
        ],
        "activation": """Actúa como BrandMind, agente maestro de estrategia de marca,
UX, copywriting y dirección de arte visual para HiphaMX.

Proyecto: [nombre del cliente o proyecto]

Contexto:
- Descripción del negocio: [...]
- Audiencia objetivo: [...]
- Objetivo: [web / campaña / branding / imagen publicitaria]
- Referencias de marca que admiran: [...]

Tarea: [Brand Brief / Wireframe Brief / Copy / Voice Brief / Prompt de imagen]

Entrega esperada: [especificar formato]""",
    },
    {
        "id": 3,
        "key": "designflow",
        "name": "DesignFlow",
        "icon": "🖌️",
        "color": C.fg(6, 182, 212),       # Cyan
        "role": "Senior UX/UI Designer & Webflow Specialist",
        "file": "AGENT_DESIGNFLOW.md",
        "badge": "Requiere brief de BrandMind",
        "tags": ["web", "diseño", "ui", "ux", "webflow", "css", "html", "componente",
                 "landing", "animación", "glassmorphism"],
        "when_to_use": [
            "Diseñar una sección o página web completa",
            "Crear un componente UI (card, nav, hero, footer)",
            "Generar código HTML/CSS listo para Webflow",
            "Definir el sistema de tokens de diseño de un proyecto",
            "Añadir micro-animaciones o efectos glassmorphism",
        ],
        "activation": """Actúa como DesignFlow, agente senior de UX/UI design y
especialista en Webflow para HiphaMX.

⚠️ REQUISITO: Adjunta el Brand Brief y Wireframe Brief de BrandMind antes de continuar.

[PEGAR BRAND BRIEF DE BRANDMIND AQUÍ]
[PEGAR WIREFRAME BRIEF DE BRANDMIND AQUÍ]

Tarea: [sección/página específica a diseñar]
Proyecto: [HiphaMX interno | nombre del cliente]
Estilo de referencia: [e.g., "premium dark como Linear.app"]

Entrega: HTML + CSS con variables, listo para Webflow Embed.""",
    },
    {
        "id": 4,
        "key": "launchbuzz",
        "name": "LaunchBuzz",
        "icon": "📣",
        "color": C.fg(251, 191, 36),      # Amber
        "role": "Digital Marketing Strategist & Content Creator",
        "file": "AGENT_LAUNCHBUZZ.md",
        "badge": None,
        "tags": ["marketing", "linkedin", "twitter", "email", "campaña", "contenido",
                 "redes sociales", "post", "lanzamiento"],
        "when_to_use": [
            "Crear posts de LinkedIn para anunciar algo",
            "Escribir un thread de Twitter/X",
            "Diseñar una campaña de email marketing",
            "Convertir una feature técnica en contenido de marketing",
            "Posicionar HiphaMX ante clientes o developers",
        ],
        "activation": """Actúa como LaunchBuzz, agente de marketing digital para HiphaMX.

Tarea: [describir qué crear]

[PEGAR VOICE BRIEF DE BRANDMIND SI EXISTE]

Audiencia objetivo: [developers / CMOs / fundadores / consumidores]
Canal: [LinkedIn / Twitter / Email / todos]
Activo técnico: [describir el producto/servicio a promocionar]
Objetivo: [awareness / leads / credibilidad / ventas]

Entrega: piezas de contenido listas para publicar con hashtags.""",
    },
    {
        "id": 5,
        "key": "docagent",
        "name": "DocAgent",
        "icon": "📄",
        "color": C.fg(34, 197, 94),       # Green
        "role": "Technical Documentation Engineer",
        "file": "AGENT_DOCAGENT.md",
        "badge": None,
        "tags": ["documentación", "readme", "guía", "endpoint", "api", "changelog", "docstring"],
        "when_to_use": [
            "Documentar un endpoint nuevo o existente",
            "Actualizar o generar el README.md",
            "Crear o actualizar el .env.example",
            "Escribir docstrings para funciones de FastAPI",
            "Generar o mantener el CHANGELOG",
        ],
        "activation": """Actúa como DocAgent, agente de documentación técnica para HiphaMX-fastapi.

Tarea: [describir qué documentar]

Contexto:
- Endpoints: /api/auth/register, /api/auth/login, /api/auth/me, /api/webflow/*
- Stack: FastAPI · SQLAlchemy · python-jose · passlib

Entrega: [sección de README / guía de endpoint / CHANGELOG listo para copiar]""",
    },
    {
        "id": 6,
        "key": "codeguardian",
        "name": "CodeGuardian",
        "icon": "🛡️",
        "color": C.fg(239, 68, 68),       # Red
        "role": "Senior Security Engineer & Code Quality Auditor",
        "file": "AGENT_CODEGUARDIAN.md",
        "badge": None,
        "tags": ["seguridad", "JWT", "SQL injection", "auditoría", "código", "bugs",
                 "vulnerabilidades", "pep8"],
        "when_to_use": [
            "Revisar seguridad de un endpoint o módulo",
            "Validar la implementación de JWT / Auth",
            "Detectar SQL injection u otras vulnerabilidades",
            "Auditar calidad y estilo del código (PEP 8)",
            "Verificar que los secretos (.env) están bien manejados",
        ],
        "activation": """Actúa como CodeGuardian, agente especializado en seguridad para HiphaMX-fastapi.

Tarea: [describir qué revisar]

Contexto:
- Framework: FastAPI + SQLAlchemy + SQLite
- Auth: JWT con python-jose, passwords con passlib/bcrypt

Entrega:
1. Hallazgos ordenados por nivel de riesgo
2. Fragmento de código vulnerable
3. Corrección segura recomendada""",
    },
    {
        "id": 7,
        "key": "viralgen",
        "name": "VIRALGEN",
        "icon": "🧬",
        "color": C.fg(16, 185, 129),      # Emerald
        "role": "Social Media Strategist · Psicólogo del Consumidor",
        "file": "AGENT_VIRALGEN.md",
        "badge": None,
        "tags": ["social", "viral", "tiktok", "instagram", "psicología", "hook", "engagement"],
        "when_to_use": [
            "Crear contenido B2C que genere viralidad",
            "Entender la psicografía de la audiencia",
            "Generar hooks que detienen el scroll",
            "Escribir guiones para Reels o TikToks",
        ],
        "activation": """Actúa como VIRALGEN, agente estratega de social media para HiphaMX.

BRIEFING:
- Marca / Producto: [nombre + descripción]
- Audiencia objetivo: [demografía + psicografía]
- Plataforma(s): [TikTok / IG / LinkedIn / Facebook]
- Objetivo: [viralización / conversión / comunidad]

ENTREGA ESPERADA:
- Diagnóstico psicográfico y concepto filosófico
- Piezas de contenido listas para publicar con hooks
- Prompts visuales para cada pieza""",
    },
    {
        "id": 8,
        "key": "imagenologo",
        "name": "IMAGENOLOGO",
        "icon": "🎨",
        "color": C.fg(236, 72, 153),      # Pink
        "role": "Prompt Engineer Senior — Fotografía Publicitaria",
        "file": "AGENT_IMAGENOLOGO.md",
        "badge": None,
        "tags": ["imagen", "prompt", "fotografía", "gemini", "nanobanana", "realismo", "8K"],
        "when_to_use": [
            "Generar super-prompts para imágenes hiperrealistas 8K",
            "Integrar un producto o logotipo en un prompt",
            "Generar fotografía gastronómica, lifestyle o e-commerce",
        ],
        "activation": """Actúa como IMAGENOLOGO, agente ingeniero de prompts hiperrealistas para HiphaMX.

Tarea: [describir la imagen que necesito]
Canal de distribución: [Instagram / web / impresión / billboard]
Estilo de referencia: [estilo / marca de referencia]
Paleta de colores: [hex codes o descripción]

Genera el prompt completo en inglés siguiendo la arquitectura de capas,
con todos los módulos de coherencia aplicables y parámetros técnicos 8K.""",
    },
    {
        "id": 9,
        "key": "curadordam",
        "name": "CuradorDAM",
        "icon": "🏺",
        "color": C.fg(245, 158, 11),      # Amber/Gold
        "role": "Curador Profesional · Arquitecto Constructor (DAM)",
        "file": "AGENT_CURADORDAM.md",
        "badge": "Específico para DAM",
        "tags": ["dam", "interiorismo", "azulejos", "pisos", "construcción", "curaduría"],
        "when_to_use": [
            "Encontrar equivalencias de materiales de catálogos DAM",
            "Analizar una imagen de inspiración arquitectónica",
            "Combinar formatos de pisos o recubrimientos",
        ],
        "activation": """Actúa como CuradorDAM, curador experto en interiores para DAM.

TAREA: Analizar esta inspiración y proponer equivalencias.
VIBRA DESEADA: [estilo / sensación]
RESTRICCIONES: 
- CERO alucinación de marcas (Solo Daltile, Urrea, Helvex, Total Shower).
- Si hay un piso obligatorio, céntrate en él.

ENTREGA ESPERADA:
- Diagnóstico de vibra
- Selección de productos reales
- Instrucciones para IMAGENOLOGO para generar el render.""",
    },
]

# ─── Helper functions ────────────────────────────────────────────────────────

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def width():
    try:
        return os.get_terminal_size().columns
    except:
        return 80

def hr(char="─", color=MUTED):
    print(f"{color}{char * width()}{C.RESET}")

def center(text, w=None):
    import re
    w = w or width()
    plain = re.sub(r'\033\[[0-9;]*m', '', text)
    pad = max(0, (w - len(plain)) // 2)
    print(" " * pad + text)

# ─── Screens ─────────────────────────────────────────────────────────────────

def print_header():
    clear()
    w = width()
    print(BG_DARK + " " * w + C.RESET)
    print()
    center(f"{CYAN}{C.BOLD}╔══════════════════════════════════════╗{C.RESET}")
    center(f"{CYAN}{C.BOLD}║   {MAGENTA}HiphaMX{CYAN}  —  Agent Control Panel   ║{C.RESET}")
    center(f"{CYAN}{C.BOLD}╚══════════════════════════════════════╝{C.RESET}")
    print()
    center(f"{MUTED}Tu equipo de agentes especializados — selecciona uno para activarlo{C.RESET}")
    print()

def print_agent_list():
    print_header()
    hr()
    print()

    for a in AGENTS:
        color = a["color"]
        tags_str = "  ".join(f"{MUTED}#{t}{C.RESET}" for t in a["tags"][:4])
        badge_str = f"  {C.fg(250,204,21)}⚡ {a['badge']}{C.RESET}" if a.get("badge") else ""
        print(f"  {color}{C.BOLD}[{a['id']}] {a['icon']}  {a['name']}{C.RESET}{badge_str}")
        print(f"      {WHITE}{a['role']}{C.RESET}")
        print(f"      {tags_str}")
        print()

    hr()
    print()
    print(f"  {CYAN}[10]{C.RESET} {WHITE}🔍  Ayúdame a elegir un agente{C.RESET}  {MUTED}(responde unas preguntas){C.RESET}")
    print(f"  {MUTED}[0]  Salir{C.RESET}")
    print()

def print_agent_detail(agent):
    clear()
    color = agent["color"]
    w = width()

    print()
    center(f"{color}{C.BOLD}{agent['icon']}  {agent['name']}{C.RESET}", w)
    center(f"{MUTED}{agent['role']}{C.RESET}", w)
    if agent.get("badge"):
        center(f"{C.fg(250,204,21)}{C.BOLD}⚡ {agent['badge']}{C.RESET}", w)
    print()
    hr("═", color)
    print()

    print(f"  {CYAN}{C.BOLD}¿Cuándo usarlo?{C.RESET}")
    print()
    for item in agent["when_to_use"]:
        print(f"  {color}▸{C.RESET}  {WHITE}{item}{C.RESET}")
    print()

    hr("─", MUTED)
    print()

    print(f"  {CYAN}{C.BOLD}📋  Script de Activación{C.RESET}")
    print(f"  {MUTED}Copia y pega esto al inicio de tu conversación:{C.RESET}")
    print()

    lines = agent["activation"].strip().split("\n")
    box_w = min(w - 4, 76)
    print(f"  {color}┌{'─' * (box_w - 2)}┐{C.RESET}")
    for line in lines:
        wrapped = textwrap.wrap(line, box_w - 4) if line else [""]
        for wline in wrapped:
            padding = box_w - 4 - len(wline)
            print(f"  {color}│{C.RESET}  {WHITE}{wline}{' ' * padding}{C.RESET}  {color}│{C.RESET}")
    print(f"  {color}└{'─' * (box_w - 2)}┘{C.RESET}")
    print()

    hr("─", MUTED)
    print()
    print(f"  {MUTED}📁  Manifiesto completo:{C.RESET}  {color}{agent['file']}{C.RESET}")
    print()

    input(f"  {CYAN}Presiona Enter para volver al menú principal...{C.RESET}")

def wizard():
    clear()
    print_header()
    print(f"  {CYAN}{C.BOLD}🔍  Asistente de selección de agente{C.RESET}")
    print()
    print(f"  {WHITE}¿Qué quieres hacer hoy? Elige la opción más cercana:{C.RESET}")
    print()

    questions = [
        ("Empezar un proyecto nuevo o no sé qué agente usar.",               ["kam"]),
        ("Necesito definir la marca, copy, imágenes o brief estratégico.",    ["brandmind"]),
        ("Quiero diseñar una web o componente para Webflow.",                 ["designflow"]),
        ("Necesito crear contenido B2B para LinkedIn, Twitter o email.",      ["launchbuzz"]),
        ("Necesito crear contenido viral B2C (TikTok, IG Reels) y hooks.",    ["viralgen"]),
        ("Necesito super-prompts 8K para fotografía publicitaria Gemini.",    ["imagenologo"]),
        ("Tengo un proyecto de interiorismo/arquitectura específico de DAM.", ["curadordam"]),
        ("Necesito documentar endpoints, README o el proyecto.",              ["docagent"]),
        ("Tengo un problema de seguridad o quiero auditar el código.",        ["codeguardian"]),
        ("No sé bien, muéstrame todos los agentes.",                          None),
    ]

    for i, (q, _) in enumerate(questions, 1):
        wrapped = textwrap.wrap(q, width() - 10)
        first = True
        for line in wrapped:
            prefix = f"  {CYAN}[{i}]{C.RESET}  " if first else "       "
            print(f"{prefix}{WHITE}{line}{C.RESET}")
            first = False
        print()

    hr()
    print()

    choice = input(f"  {CYAN}Tu elección (1-{len(questions)}): {C.RESET}").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(questions) - 1:
            _, agent_keys = questions[idx]
            if agent_keys:
                matched = [a for a in AGENTS if a["key"] in agent_keys]
                if matched:
                    return matched[0]
        return None
    except (ValueError, IndexError):
        return None

# ─── Argument matching ───────────────────────────────────────────────────────

def find_agent_by_query(q: str):
    q = q.lower()
    for a in AGENTS:
        if q in a["key"] or q in a["name"].lower():
            return a
    for a in AGENTS:
        if any(q in t for t in a["tags"]):
            return a
    return None

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--list" in args or "-l" in args:
        print(f"\n{C.BOLD}HiphaMX — Agentes disponibles:{C.RESET}\n")
        for a in AGENTS:
            badge = f"  ⚡ {a['badge']}" if a.get("badge") else ""
            print(f"  {a['icon']}  {C.BOLD}{a['name']:<14}{C.RESET} — {a['role']}{badge}")
            print(f"     Tags: {', '.join(a['tags'][:5])}")
            print()
        return

    if args:
        query = " ".join(args)
        matched = find_agent_by_query(query)
        if matched:
            if sys.stdout.isatty():
                print_agent_detail(matched)
            else:
                print(f"{matched['icon']} {matched['name']} — {matched['role']}")
                print()
                print(matched["activation"])
            return
        else:
            print(f"\n  ⚠️  No encontré un agente que coincida con '{query}'.")
            print(f"  Usa: python3 agents.py --list para ver todos los agentes.\n")
            sys.exit(1)

    if not sys.stdout.isatty():
        print("HiphaMX Agents:")
        for a in AGENTS:
            badge = f" ⚡ {a['badge']}" if a.get("badge") else ""
            print(f"  [{a['id']}] {a['name']} — {a['role']}{badge}")
        return

    while True:
        print_agent_list()

        choice = input(f"  {CYAN}Selecciona un agente {MUTED}[1-9, 10, 0]{CYAN}: {C.RESET}").strip()

        if choice == "0":
            clear()
            print()
            center(f"{CYAN}{C.BOLD}¡Hasta pronto! 🚀{C.RESET}")
            center(f"{MUTED}— HiphaMX Agent Control Panel —{C.RESET}")
            print()
            break

        elif choice == "10":
            result = wizard()
            if result:
                print_agent_detail(result)

        elif choice.isdigit() and 1 <= int(choice) <= len(AGENTS):
            agent = AGENTS[int(choice) - 1]
            print_agent_detail(agent)

        else:
            matched = find_agent_by_query(choice)
            if matched:
                print_agent_detail(matched)
            else:
                print()
                print(f"  {C.fg(239,68,68)}Opción no reconocida. Intenta de nuevo.{C.RESET}")
                import time; time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {MUTED}Saliendo...{C.RESET}\n")
