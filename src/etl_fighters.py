import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Conexión a DB
DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"

def clean_height(height_str):
    """Convierte '5' 11"' a centímetros (float)"""
    if pd.isna(height_str) or height_str == '--':
        return None
    try:
        # Limpiamos comillas y espacios
        clean = height_str.replace('"', '').split("'")
        feet = int(clean[0])
        inches = int(clean[1])
        # Conversión a CM
        return (feet * 30.48) + (inches * 2.54)
    except:
        return None

def clean_weight(weight_str):
    """Convierte '155 lbs.' a Kilogramos (float)"""
    if pd.isna(weight_str) or weight_str == '--':
        return None
    try:
        # Quitamos " lbs." y convertimos
        lbs = float(weight_str.replace(' lbs.', '').strip())
        return lbs * 0.453592
    except:
        return None

def clean_reach(reach_str):
    """Convierte '70.0"' a centímetros"""
    if pd.isna(reach_str) or reach_str == '--':
        return None
    try:
        inches = float(reach_str.replace('"', '').strip())
        return inches * 2.54
    except:
        return None

def run_etl():
    print("--- INICIANDO TRANSFORMACIÓN DE DATOS BIOMÉDICOS ---")
    
    # 1. Cargar CSV crudo
    try:
        df = pd.read_csv("ufc_fighters_biometrics.csv")
        print(f">>> Datos crudos cargados: {len(df)} registros.")
    except FileNotFoundError:
        print("❌ No encuentro el CSV de biometría.")
        return

    # 2. Aplicar transformaciones (Limpieza)
    # Creamos columnas nuevas métricas
    print("... Convirtiendo unidades (Imperial -> Métrico) ...")
    
    df['Height_cms'] = df['Height'].apply(clean_height)
    df['Weight_kgs'] = df['Weight'].apply(clean_weight)
    df['Reach_cms'] = df['Reach'].apply(clean_reach)
    
    # Rellenamos nulos con 0 o NaN de numpy para que SQL no se queje
    df = df.replace({np.nan: None})

    # 3. Seleccionar columnas finales limpias
    final_df = df[['URL', 'Name', 'Height_cms', 'Weight_kgs', 'Reach_cms', 'Stance', 'DOB']]
    
    print(final_df.head())

    # 4. Guardar en SQL en una tabla NUEVA llamada 'clean_fighters'
    engine = create_engine(DB_STR)
    try:
        final_df.to_sql('clean_fighters', engine, if_exists='replace', index=False)
        print(f"✅ ¡ÉXITO! Tabla 'clean_fighters' creada en la Base de Datos.")
        print("   Ahora tienes datos numéricos listos para análisis.")
    except Exception as e:
        print(f"❌ Error al guardar en SQL: {e}")

if __name__ == "__main__":
    run_etl()