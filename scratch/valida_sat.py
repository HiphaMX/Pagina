import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Agregar raíz al path
sys.path.append(str(PROJECT_ROOT))

from app.services.sat_service import get_fiel_for_rfc
from cfdiclient import Autenticacion

def validate():
    rfcs = ["DEGF851127TK1", "MEHA850118Q96"]
    print("==================================================")
    print("      VALIDACIÓN DE CREDENCIALES SAT (FIEL)       ")
    print("==================================================")
    
    for rfc in rfcs:
        print(f"\nProbando RFC: {rfc}")
        try:
            # 1. Cargar FIEL
            fiel = get_fiel_for_rfc(rfc)
            print("  ✓ [PASO 1] Archivos .cer y .key cargados con éxito.")
            
            # 2. Autenticar
            print("  Conectando al Web Service de Autenticación del SAT...")
            auth = Autenticacion(fiel)
            token = auth.obtener_token()
            print("  ✓ [PASO 2] Conexión establecida. Token SOAP generado exitosamente.")
            print(f"  Token obtenido (truncado): {token[:40]}...")
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            
    print("\n==================================================")

if __name__ == "__main__":
    validate()
