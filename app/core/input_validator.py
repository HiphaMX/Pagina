import re
import unicodedata
from typing import List, Tuple, Optional


class SecurityViolationException(Exception):
    """Excepción lanzada cuando se detecta un patrón o metacarácter restringido en la entrada."""
    def __init__(self, message: str, violations: List[str]):
        super().__init__(message)
        self.violations = violations


class InputSecurityValidator:
    """
    Validador de Seguridad Avanzado para entradas y ejecución de procesos en agentes autónomos.
    Implementa mitigaciones contra inyecciones de comandos, SQL e infraestructura según
    el reporte de seguridad (Antigravity 2.0).
    """

    # 1. Metacaracteres y operadores peligrosos en Shell (Regex)
    SHELL_METACHA_REGEX = re.compile(
        r"(?:[;&|<>`\n\r]|\$\(|\$\{|[\\])"
    )

    # 2. Palabras clave prohibidas en Shell (con límites de palabra para evitar falsos positivos)
    SHELL_KEYWORDS = [
        (r"\brm\s+-[rfRF]+\b", "Borrado recursivo forzado (rm -rf)"),
        (r"\bmkfs\b", "Formateo de sistemas de archivos (mkfs)"),
        (r"\bdd\s+if=\b", "Copia destructiva a bajo nivel (dd)"),
        (r"\bshutdown\b", "Apagado del sistema"),
        (r"\breboot\b", "Reinicio del sistema"),
        (r"\binit\s+[06]\b", "Cambio de nivel de ejecución (init 0/6)"),
        (r"\bchmod\s+777\b", "Asignación de permisos máximos inseguros (chmod 777)"),
        (r"\bchown\b", "Modificación de propietario de archivos (chown)"),
        (r"\bpkill\b", "Terminación masiva de procesos (pkill)"),
        (r"\bkill\s+-9\b", "Terminación forzada de procesos (kill -9)"),
        (r"\b(?:nc|netcat|ncat)\s+-[e]\b", "Creación de shell reverso (netcat -e)"),
        (r"/dev/(?:sd[a-z]|hd[a-z]|vd[a-z]|null|zero)\b", "Acceso directo a dispositivos del sistema (/dev)"),
        (r"/etc/(?:passwd|shadow|hosts|group)\b", "Lectura de archivos críticos del sistema (/etc/*)"),
    ]

    # 3. Comandos SQL peligrosos
    SQL_KEYWORDS = [
        (r"\bdrop\s+(?:database|table|view|procedure)\b", "Destrucción estructural SQL (DROP)"),
        (r"\btruncate\s+table\b", "Vaciado definitivo de tabla SQL (TRUNCATE)"),
        (r"\bdelete\s+from\b", "Eliminación masiva potencial de registros (DELETE FROM)"),
        (r"\balter\s+table\s+.*\s+drop\b", "Eliminación de columnas en tabla SQL"),
        (r"\bgrant\s+all\b", "Concesión de privilegios máximos SQL (GRANT ALL)"),
        (r"\bxp_cmdshell\b", "Ejecución de comandos de SO desde SQL Server"),
        (r"\bunion\s+select\b", "Técnica de extracción de datos SQL (UNION SELECT)"),
    ]

    # 4. Comandos de control de versiones e infraestructura DevOps peligrosos
    DEVOPS_KEYWORDS = [
        (r"\bgit\s+push\s+.*--force\b", "Sobrescritura forzada de repositorio remoto (git push --force)"),
        (r"\bgit\s+push\s+.*-f\b", "Sobrescritura forzada de repositorio remoto abreviada (git push -f)"),
        (r"\bgit\s+push\s+origin\s+\+", "Sobrescritura forzada de repositorio remoto con sintaxis de más (+)"),
        (r"\bgit\s+branch\s+-D\b", "Eliminación forzada de ramas locales (git branch -D)"),
        (r"\bvercel\s+(?:destroy|down)\b", "Destrucción o apagado de servicios en la nube de Vercel"),
        (r"\bkubectl\s+delete\s+(?:namespace|all|pod)\b", "Destrucción masiva en Kubernetes (kubectl delete)"),
    ]

    def __init__(self):
        # Compilar todas las regex de palabras clave prohibidas
        self._compiled_rules = []
        for pattern, description in self.SHELL_KEYWORDS + self.SQL_KEYWORDS + self.DEVOPS_KEYWORDS:
            self._compiled_rules.append((re.compile(pattern, re.IGNORECASE), description))

    def normalize_text(self, text: str) -> str:
        """
        Normaliza el texto a formato Unicode NFKC para evitar evasiones basadas en
        caracteres homóglifos u otros trucos de representación de caracteres.
        """
        if not text:
            return ""
        return unicodedata.normalize("NFKC", text)

    def check_security(self, input_text: str) -> Optional[List[str]]:
        """
        Analiza el texto de entrada. Retorna una lista con las descripciones de las
        infracciones de seguridad encontradas, o None si el texto está limpio.
        """
        if not input_text:
            return None

        # 1. Normalizar entrada
        normalized = self.normalize_text(input_text)
        violations = []

        # 2. Buscar metacaracteres peligrosos de inyección de comandos
        detected_metachars = self.SHELL_METACHA_REGEX.findall(normalized)
        if detected_metachars:
            violations.append(
                f"Metacaracteres de inyección detectados: {', '.join(repr(c) for c in set(detected_metachars))}"
            )

        # 3. Buscar patrones de palabras clave restringidas
        for regex, description in self._compiled_rules:
            if regex.search(normalized):
                violations.append(f"Patrón prohibido detectado: {description}")

        return violations if violations else None

    def validate_or_raise(self, input_text: str) -> str:
        """
        Valida la entrada de texto. Si encuentra alguna infracción, levanta una excepción
        SecurityViolationException detallando los problemas de seguridad encontrados.
        En caso contrario, retorna el texto normalizado y seguro.
        """
        violations = self.check_security(input_text)
        if violations:
            raise SecurityViolationException(
                "Entrada bloqueada por infracciones de seguridad de la lista negra.",
                violations
            )
        return self.normalize_text(input_text)
