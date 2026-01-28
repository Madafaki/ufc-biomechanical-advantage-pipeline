import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

URL = "http://ufcstats.com/statistics/events/completed"

def extract_ufc_events():
    print(f"--- Intentando conectar a: {URL} ---")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"!!! Error de conexión: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='b-statistics__table-events')
    
    if table is None:
        print("!!! ERROR: No se encontró la tabla.")
        return None

    rows = table.find_all('tr')
    print(f">>> Se encontraron {len(rows)} filas crudas.")

    events_data = []

    for i, row in enumerate(rows):
            # Saltamos la fila de encabezado
        if i < 1: 
            continue
            
        cols = row.find_all('td')
        
        # Aceptamos filas con 2 columnas 
        if len(cols) >= 2:
            # --- COLUMNA 1 (Índice 0): Tiene el Nombre, el Link y la Fecha ---
            link_tag = cols[0].find('a')
            if link_tag:
                event_name = link_tag.text.strip()
                event_url = link_tag['href']
            else:
                continue 

            date_span = cols[0].find('span')
            if date_span:
                date_text = date_span.text.strip()
            else:
                
                date_text = cols[0].text.replace(event_name, "").strip()

            # --- COLUMNA 2 (Índice 1): Tiene la Ubicación ---
            location = cols[1].text.strip()

            events_data.append({
                'Event Name': event_name,
                'Date': date_text,
                'Location': location,
                'URL': event_url
            })

    df = pd.DataFrame(events_data)
    print(f"--- Extracción finalizada. Eventos válidos: {len(df)} ---")
    return df

if __name__ == "__main__":
    df_events = extract_ufc_events()
    
    if df_events is not None and not df_events.empty:
        print(df_events.head()) # Muestra las primeras 5 en consola
        filename = f"ufc_events_raw_{datetime.date.today()}.csv"
        df_events.to_csv(filename, index=False)
        print(f"¡ÉXITO! Archivo guardado: {filename}")
    else:
        print("No se generaron datos.")