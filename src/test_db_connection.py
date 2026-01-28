from sqlalchemy import create_engine, text

# CONFIGURACIÓN DE CONEXIÓN
# Formato: postgresql://usuario:password@host:puerto/nombre_db
DB_CONNECTION_STR = "postgresql://Mafaki:ufc123@localhost:5432/ufc_data"
def test_connection():
    print("--- Probando conexión a la Base de Datos Dockerizada ---")
    
    try:
        # 1. Crear el motor de conexión
        engine = create_engine(DB_CONNECTION_STR)
        
        # 2. Intentar conectarse y ejecutar una consulta simple
        with engine.connect() as connection:
            result = connection.execute(text("SELECT '¡Hola desde Postgres!'"))
            print(f">>> ÉXITO: La base de datos respondió: {result.fetchone()[0]}")
            
    except Exception as e:
        print(f"!!! Error al conectar: {e}")
        print("Tip: Revisa que tu contenedor de Docker esté corriendo con 'docker ps'")

if __name__ == "__main__":
    test_connection()