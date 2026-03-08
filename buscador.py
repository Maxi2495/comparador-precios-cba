import requests
import urllib.parse
import re
from bs4 import BeautifulSoup
import sqlite3

SUPERMERCADOS = [
    {"nombre": "Disco", "url_base": "https://www.disco.com.ar"},
    {"nombre": "Vea",   "url_base": "https://www.vea.com.ar"},
    {"nombre": "Jumbo", "url_base": "https://www.jumbo.com.ar"},
    {"nombre": "Cordiez", "url_base": "https://www.cordiez.com.ar"}    
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
        
        # --- BLOQUE 3: CARREFOUR (VTEX IO / Intelligent Search) ---
    if supers_elegidos and "Carrefour" in supers_elegidos:
        url_carrefour = f"https://www.carrefour.com.ar/api/io/_v/api/intelligent-search/product_search/?query={termino_safe}"
        
        try:
            resp_carrefour = requests.get(url_carrefour, headers=headers, timeout=15)
            if resp_carrefour.status_code == 200:
                data_carrefour = resp_carrefour.json()
                
                productos_vtex_io = data_carrefour.get('products', []) if isinstance(data_carrefour, dict) else data_carrefour
                
                for prod in productos_vtex_io:
                    try:
                        titulo = prod.get('productName', 'Sin nombre')
                        link_parcial = prod.get('linkText', '')
                        link = f"https://www.carrefour.com.ar/{link_parcial}/p" if link_parcial else "#"
                        
                        items = prod.get('items', [])
                        if items:
                            precio = items[0]['sellers'][0]['commertialOffer']['Price']
                            stock = items[0]['sellers'][0]['commertialOffer']['AvailableQuantity']
                            
                            if stock > 0 and precio > 0:
                                resultados_totales.append({
                                    "supermercado": "Carrefour",
                                    "producto": titulo,
                                    "precio": float(precio),
                                    "link": link
                                })
                    except:
                        continue
        except Exception:
            pass

    # --- ORDENAMIENTO FINAL ---
    if orden == "mayor":
        resultados_ordenados = sorted(resultados_totales, key=lambda x: x['precio'], reverse=True)
    else:
        resultados_ordenados = sorted(resultados_totales, key=lambda x: x['precio'])
        
    # --- NUEVO: GUARDAR EN BASE DE DATOS SQLITE ---
    if resultados_ordenados: # Solo guardamos si realmente encontramos productos
        try:
            conexion = sqlite3.connect('precios.db')
            cursor = conexion.cursor()

            # 1. Registramos el evento de búsqueda en la tabla principal
            # Usamos (?) para evitar inyecciones SQL, una práctica de seguridad fundamental
            cursor.execute('INSERT INTO busquedas (termino) VALUES (?)', (termino_busqueda,))
            
            # Recuperamos el ID que SQLite le asignó automáticamente a esta búsqueda (Primary Key)
            busqueda_id = cursor.lastrowid 

            # 2. Insertamos cada producto enlazado a ese ID (Foreign Key)
            for item in resultados_ordenados:
                cursor.execute('''
                    INSERT INTO resultados (busqueda_id, supermercado, producto, precio, link)
                    VALUES (?, ?, ?, ?, ?)
                ''', (busqueda_id, item['supermercado'], item['producto'], item['precio'], item['link']))

            conexion.commit() # Confirmamos la transacción
            conexion.close()
        except Exception as e:
            print(f"Error de SQL: {e}")

    return resultados_ordenados