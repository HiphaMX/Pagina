from datetime import datetime, time, timezone, timedelta
from typing import Dict, Any, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("America/Mexico_City")
except Exception:
    # Fallback para entornos sin zoneinfo o tzdata
    LOCAL_TZ = timezone(timedelta(hours=-6))

DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_NAMES_ES = {
    "mon": "lunes",
    "tue": "martes",
    "wed": "miércoles",
    "thu": "jueves",
    "fri": "viernes",
    "sat": "sábado",
    "sun": "domingo"
}


def parse_time_str(t_str: str) -> Optional[time]:
    """Convierte un string 'HH:MM' en objeto time."""
    if not t_str:
        return None
    try:
        parts = t_str.strip().split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def check_is_open_now(
    opening_hours: Optional[Dict[str, Any]],
    current_dt: Optional[datetime] = None
) -> Tuple[bool, str]:
    """
    Evalúa si un comercio se encuentra abierto en este momento.
    
    Args:
        opening_hours: Diccionario con llaves ['mon', 'tue', ..., 'sun']
                       y valores {"open": "09:00", "close": "18:00"} o null.
        current_dt: Momento de evaluación (por defecto: ahora en zona horaria Zapopan/CDMX).
        
    Returns:
        Tuple: (is_open: bool, status_message: str)
    """
    if not opening_hours or not isinstance(opening_hours, dict):
        return False, "Horario no especificado"

    if current_dt is None:
        now_local = datetime.now(LOCAL_TZ)
    else:
        if current_dt.tzinfo is None:
            now_local = current_dt.replace(tzinfo=LOCAL_TZ)
        else:
            now_local = current_dt.astimezone(LOCAL_TZ)

    # weekday(): 0 es lunes, 6 es domingo
    day_idx = now_local.weekday()
    day_key = DAY_KEYS[day_idx]
    today_schedule = opening_hours.get(day_key)

    if not today_schedule:
        return False, "Cerrado hoy"

    open_time_str = today_schedule.get("open")
    close_time_str = today_schedule.get("close")
    
    t_open = parse_time_str(open_time_str)
    t_close = parse_time_str(close_time_str)

    if not t_open or not t_close:
        return False, "Cerrado hoy"

    current_time = now_local.time()

    # Caso 1: Horario continuo el mismo día (ej. 09:00 a 18:00)
    if t_open <= t_close:
        if t_open <= current_time <= t_close:
            return True, f"Abierto ahora · Cierra a las {close_time_str}"
        elif current_time < t_open:
            return False, f"Cerrado · Abre hoy a las {open_time_str}"
        else:
            return False, f"Cerrado hoy a las {close_time_str}"
    # Caso 2: Horario que cruza medianoche (ej. 19:00 a 02:00)
    else:
        if current_time >= t_open or current_time <= t_close:
            return True, f"Abierto ahora · Cierra a las {close_time_str}"
        else:
            return False, f"Cerrado · Abre hoy a las {open_time_str}"
