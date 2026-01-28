import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from sqlalchemy import create_engine

DB_STR = "postgresql://postgres:ufc123@127.0.0.1:5433/ufc_data"

def get_unique_fighters():
    """Obtiene una lista de URLs únicas de peleadores desde la tabla de peleas"""
    engine = create_engine(DB_STR)
    
    # Unimos las dos columnas de URLs en una sola lista
    query = """
    SELECT "Fighter_1_URL" as url FROM raw_fights
    UNION
    SELECT "Fighter_2_URL" as url FROM raw_fights
    """
    df = pd.read_sql(query, engine)
    
    # Filtramos URLs vacías o nulas
    urls = df['url'].dropna().unique().tolist()
    print(f">>> Se encontraron {len(urls)} peleadores únicos para analizar.")
    return urls

def scrape_fighter_profile(url):
    """Extrae datos biométricos de un peleador"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
    except:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Diccionario base
    fighter_data = {'URL': url, 'Name': 'Unknown', 'Height': None, 'Weight': None, 'Reach': None, 'Stance': None, 'DOB': None}
    
    # 1. Nombre
    name_tag = soup.find('span', class_='b-content__title-highlight')
    if name_tag:
        fighter_data['Name'] = name_tag.text.strip()
        
    # 2. Datos Físicos (Están en una lista tipo 'b-list__box-list')
    # Buscamos los items de la lista y limpiamos el texto
    box = soup.find('div', class_='b-list__info-box_style_small-width')
    if box:
        items = box.find_all('li')
        for item in items:
            text = item.text.replace('\n', '').replace(' ', '')
            
            if 'Height:' in text:
                fighter_data['Height'] = item.text.replace('Height:', '').strip()
            elif 'Weight:' in text:
                fighter_data['Weight'] = item.text.replace('Weight:', '').strip()
            elif 'Reach:' in text:
                fighter_data['Reach'] = item.text.replace('Reach:', '').strip()
            elif 'STANCE:' in text: # A veces viene en mayúsculas
                fighter_data['Stance'] = item.text.replace('STANCE:', '').strip()
            elif 'DOB:' in text:
                fighter_data['DOB'] = item.text.replace('DOB:', '').strip()
                
    return fighter_data

def main():
    # 1. Obtener lista de peleadores
    fighter_urls = get_unique_fighters()
    
    # LIMITAMOS A 10 PARA PRUEBA RÁPIDA (Si funciona, quitas el [:10])
    print("--- Iniciando scraping de peleadores (Modo Prueba: 10 primeros) ---")
    fighter_urls_subset = fighter_urls 
    
    data = []
    for i, url in enumerate(fighter_urls_subset):
        print(f"[{i+1}/{len(fighter_urls_subset)}] Analizando: {url}")
        info = scrape_fighter_profile(url)
        if info:
            data.append(info)
        time.sleep(1) # Respetamos al servidor
        
    # Guardar
    if data:
        df = pd.DataFrame(data)
        print(df.head())
        df.to_csv("ufc_fighters_biometrics.csv", index=False)
        print("✅ ¡Datos Biomédicos extraídos!")

if __name__ == "__main__":
    main()