import requests
from bs4 import BeautifulSoup
import json  # <--- Importante: Nueva herramienta para leer datos estructurados

# URL de la Cerveza Corona
url = "https://www.disco.com.ar/cerveza-rubia-330ml-corona-2/p"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"Consultando: {url}")

try:
    respuesta = requests.get(url, headers=headers)

    if respuesta.status_code == 200:
        print("¡Conexión exitosa!")
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        titulo = soup.title.string.strip()
        print(f"Producto: {titulo}")

        # --- ESTRATEGIA NINJA: JSON Oculto ---
        print("\nBuscando datos ocultos (JSON-LD)...")
        
        # Buscamos scripts que tengan info para Google (Schema.org)
        scripts = soup.find_all("script", type="application/ld+json")
        
        encontrado = False
        
        for script in scripts:
            try:
                # Convertimos el texto del script a un diccionario de Python
                datos = json.loads(script.string)
                
                # A veces hay varios scripts, buscamos el que sea de tipo 'Product'
                if datos.get('@type') == 'Product':
                    print("¡Datos de producto encontrados!")
                    
                    # Navegamos dentro del diccionario para hallar el precio
                    # Usualmente está en 'offers' -> 'lowPrice' o 'price'
                    oferta = datos.get('offers', {})
                    precio = oferta.get('lowPrice') or oferta.get('price')
                    
                    if precio:
                        print(f"💰 PRECIO DETECTADO: ${precio}")
                        encontrado = True
                        break # Ya lo tenemos, dejamos de buscar
            except:
                continue # Si un script falla, probamos el siguiente

        if not encontrado:
            print("No se pudo extraer el precio del JSON. La estructura puede ser diferente.")
            
    else:
        print(f"Error: {respuesta.status_code}")

except Exception as e:
    print(f"Error: {e}")