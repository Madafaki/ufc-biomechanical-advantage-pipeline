import pandas as pd
from sqlalchemy import create_engine

# Conexión a tu DB (Puerto 5433)
DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"

def load_fights():
    print("--- Cargando PELEAS a PostgreSQL ---")
    
    # 1. Leer el CSV generado
    try:
        df = pd.read_csv("ufc_fights_raw.csv")
        print(f">>> CSV leído con éxito: {len(df)} registros.")
    except FileNotFoundError:
        print("❌ Error: No encuentro 'ufc_fights_raw.csv'.")
        return

    # 2. Conectar a la DB
    engine = create_engine(DB_STR)
    
    # 3. Guardar en SQL
    # Nombre de la tabla: raw_fights
    try:
        df.to_sql('raw_fights', engine, if_exists='replace', index=False)
        print(f"✅ ¡ÉXITO! Tabla 'raw_fights' creada con {len(df)} filas.")
    except Exception as e:
        print(f"❌ Error escribiendo en SQL: {e}")

if __name__ == "__main__":
    load_fights()