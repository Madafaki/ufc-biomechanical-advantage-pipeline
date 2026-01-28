import pandas as pd
from sqlalchemy import create_engine, text
import glob
import os

# CONFIGURACIÓN DE BASE DE DATOS
DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"

def get_latest_csv():
    """Busca el archivo CSV más reciente que empiece con 'ufc_events_raw'"""
    # Busca todos los archivos que coincidan con el patrón
    files = glob.glob("ufc_events_raw_*.csv")
    if not files:
        return None
    # Ordena por fecha de modificación y devuelve el último
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def load_data_to_postgres():
    print("--- INICIANDO CARGA DE DATOS (ETL: Load Phase) ---")
    
    # 1. Encontrar el archivo
    csv_file = get_latest_csv()
    if not csv_file:
        print("❌ ERROR: No encontré ningún archivo CSV 'ufc_events_raw...'. Ejecuta primero el extractor.")
        return

    print(f">>> Archivo encontrado: {csv_file}")

    # 2. Leer el CSV con Pandas
    try:
        df = pd.read_csv(csv_file)
        print(f">>> Datos leídos: {len(df)} filas.")
    except Exception as e:
        print(f"❌ Error leyendo el CSV: {e}")
        return

    # 3. Conectar a la Base de Datos
    try:
        engine = create_engine(DB_STR)
        conn = engine.connect()
        print(">>> Conexión a Base de Datos: EXITOSA.")
    except Exception as e:
        print(f"❌ Error conectando a Postgres: {e}")
        return

    # 4. Guardar en SQL (La Magia)
    # 'if_exists="replace"' significa: Si la tabla ya existe, bórrala y crea una nueva.
    # index=False: No guardes el número de fila (0, 1, 2...) como columna.
    table_name = "raw_events"
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"✅ ¡ÉXITO! Se cargaron {len(df)} registros en la tabla '{table_name}'.")
    except Exception as e:
        print(f"❌ Error guardando en SQL: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    load_data_to_postgres()