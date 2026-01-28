import psycopg2

print("--- DIAGNÓSTICO DE CONEXIÓN ---")

try:
    # Intentamos conectar directo, sin SQLAlchemy de por medio
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="ufc_data",
        user="postgres",    # <--- EL ESTÁNDAR
        password="ufc123",
        port="5433"
    )
    print("✅ ¡CONEXIÓN EXITOSA! El usuario y contraseña son correctos.")
    conn.close()

except Exception as e:
    print("\n❌ FALLÓ LA CONEXIÓN.")
    print("Aquí está el error real (sin que Python se queje de los acentos):")
    # Esto nos mostrará el error "crudo" para saber qué pasa
    print(repr(e))