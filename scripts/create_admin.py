#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Insertar el path raíz al sys.path para poder importar app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import get_password_hash
from app.models.user import User
from app.core.database import Base

def create_admin_in_db(db_uri, email, password):
    print(f"Conectando a base de datos: {db_uri}")
    engine = create_engine(db_uri, connect_args={"check_same_thread": False})
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Buscar si el usuario ya existe
        user = db.query(User).filter(User.email == email).first()
        hashed_password = get_password_hash(password)
        
        if user:
            print(f"El usuario {email} ya existe. Actualizando contraseña...")
            user.hashed_password = hashed_password
            user.is_active = True
            db.commit()
            print("✓ Contraseña actualizada con éxito.")
        else:
            print(f"El usuario {email} no existe. Creándolo...")
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                full_name="Administrador Hipha",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            print("✓ Usuario administrador creado con éxito.")
    except Exception as e:
        print(f"❌ Error al procesar base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    # Cargar credenciales de forma segura desde argumentos o variables de entorno
    email = os.environ.get("ADMIN_EMAIL", "hola@hipha.mx")
    password = os.environ.get("ADMIN_PASSWORD")
    
    if not password:
        if len(sys.argv) > 1:
            password = sys.argv[1]
        else:
            print(f"❌ Error: Se requiere la contraseña como argumento o en la variable de entorno ADMIN_PASSWORD.")
            print("Uso: ./venv/bin/python scripts/create_admin.py <contraseña>")
            sys.exit(1)
    
    # Aplicar a base de datos de producción
    prod_uri = "sqlite:///./database.db"
    create_admin_in_db(prod_uri, email, password)
    
    print("-" * 50)
    
    # Aplicar a base de datos de pruebas
    test_uri = "sqlite:///./test.db"
    create_admin_in_db(test_uri, email, password)
    
    print("\n🎉 Proceso de configuración de Administrador completado.")

if __name__ == "__main__":
    main()
