import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

SUPERMERCADOS = [
    {"nombre": "Disco", "url_base": "https://www.disco.com.ar"},
    {"nombre": "Vea",   "url_base": "https://www.vea.com.ar"},
    {"nombre": "Jumbo", "url_base": "https://www.jumbo.com.ar"}
]

def buscar_productos(termino_busqueda, supers_elegidos, orden):
    termino_safe = urllib.parse.quote(termino_busqueda)
    resultados_totales = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    # --- BLOQUE 1: CENCOSUD (Disco, Vea, Jumbo) ---
    for superm in SUPERMERCADOS:
        if supers_elegidos and superm['nombre'] not in supers_elegidos:
            continue
            
        nombre_super = superm['nombre']
        url_api = f"{superm['url_base']}/api/catalog_system/pub/products/search?ft={termino_safe}"
        
        try:
            respuesta = requests.get(url_api, headers=headers, timeout=5)
            
            if respuesta.status_code in [200, 206]:
                for prod in respuesta.json():
                    try:
                        titulo = prod.get('productName', 'Sin nombre')
                        link = prod.get('link', '#')
                        items = prod.get('items', [])
                        
                        if items:
                            precio = items[0]['sellers'][0]['commertialOffer']['Price']
                            stock = items[0]['sellers'][0]['commertialOffer']['AvailableQuantity']
                            
                            if stock > 0 and precio > 0:
                                resultados_totales.append({
                                    "supermercado": nombre_super,
                                    "producto": titulo,
                                    "precio": float(precio),
                                    "link": link
                                })
                    except:
                        continue
        except Exception:
            pass

    # --- BLOQUE 2: SUPER MAMI ---
    if supers_elegidos and "Super Mami" in supers_elegidos:
        # Usamos una versión limpia de la URL inyectando el término de búsqueda
        url_mami = f"https://www.supermami.com.ar/super/categoria?Ntt={termino_safe}"
        
        try:
            resp_mami = requests.get(url_mami, headers=headers, timeout=5)
            if resp_mami.status_code == 200:
                sopa = BeautifulSoup(resp_mami.text, 'html.parser')
                scripts = sopa.find_all('script')
                
                for script in scripts:
                    if script.string and '"item_name"' in script.string and '"price"' in script.string:
                        patron = r'"item_name":\s*"([^"]+)".*?"price":\s*([\d\.]+)'
                        productos_mami = re.findall(patron, script.string, re.DOTALL)
                        
                        for nombre, precio in productos_mami:
                            # Super Mami no incluye el link directo en este JSON, generamos uno de búsqueda
                            link_mami = f"https://www.supermami.com.ar/super/categoria?Ntt={urllib.parse.quote(nombre)}"
                            
                            resultados_totales.append({
                                "supermercado": "Super Mami",
                                "producto": nombre,
                                # Convertimos el precio a float para que el ordenamiento matemático funcione
                                "precio": float(precio), 
                                "link": link_mami
                            })
                        break # Salimos del loop una vez que encontramos el script correcto
        except Exception:
            pass

    # --- ORDENAMIENTO FINAL ---
    if orden == "mayor":
        resultados_ordenados = sorted(resultados_totales, key=lambda x: x['precio'], reverse=True)
    else:
        resultados_ordenados = sorted(resultados_totales, key=lambda x: x['precio'])
        
    return resultados_ordenados