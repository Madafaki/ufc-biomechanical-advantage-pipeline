import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from sqlalchemy import create_engine

# Conexión a base de datos (Puerto 5433)
DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"

def get_event_urls():
    """Lee las URLs de la base de datos"""
    print("--- Consultando base de datos para obtener links de eventos ---")
    engine = create_engine(DB_STR)
    
    # Leemos solo las URLs. 
    query = "SELECT \"URL\", \"Event Name\", \"Date\" FROM raw_events;" 
    
    df = pd.read_sql(query, engine)
    print(f">>> Se encontraron {len(df)} eventos para procesar.")
    return df

def extract_fights_from_event(event_row):
    """Entra a un link de evento y saca las peleas"""
    url = event_row['URL']
    event_name = event_row['Event Name']
    date = event_row['Date']
    
    print(f"Scrapeando evento: {event_name}...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
    except:
        print(f"Error conectando a {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar la tabla de peleas
    rows = soup.find_all('tr', class_='b-fight-details__table-row')
    
    fights = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2: continue
        
        # Los nombres de los peleadores están en la segunda columna (index 1)
        fighters_col = cols[1].find_all('a')
        if len(fighters_col) == 2:
            fighter_1 = fighters_col[0].text.strip()
            fighter_1_url = fighters_col[0]['href']
            
            fighter_2 = fighters_col[1].text.strip()
            fighter_2_url = fighters_col[1]['href']
            
            # Guardamos la info
            fights.append({
                'Event': event_name,
                'Date': date,
                'Fighter_1': fighter_1,
                'Fighter_1_URL': fighter_1_url, 
                'Fighter_2': fighter_2,
                'Fighter_2_URL': fighter_2_url  
            })
            
    return fights

def main():
    # 1. Obtener links de la DB
    df_events = get_event_urls()
    
    all_fights = []
    
    # 2. Iterar sobre cada evento
    for index, row in df_events.iterrows():
        fights = extract_fights_from_event(row)
        all_fights.extend(fights)
        
        # Pausa para no saturar el servidor
        time.sleep(1) 
        
    # 3. Guardar resultados
    if all_fights:
        df_fights = pd.DataFrame(all_fights)
        print(df_fights.head())
        df_fights.to_csv("ufc_fights_raw.csv", index=False)
        print(f"--- ¡ÉXITO! Se extrajeron {len(df_fights)} peleas. Guardado en ufc_fights_raw.csv ---")

if __name__ == "__main__":
    main()