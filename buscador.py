import requests
import urllib.parse

# Configuramos los tres supermercados de la misma familia
SUPERMERCADOS = [
    {"nombre": "Disco", "url_base": "https://www.disco.com.ar"},
    {"nombre": "Vea",   "url_base": "https://www.vea.com.ar"},
    {"nombre": "Jumbo", "url_base": "https://www.jumbo.com.ar"}
]

def buscar_productos(termino_busqueda):
    termino_safe = urllib.parse.quote(termino_busqueda)
    resultados_totales = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    for superm in SUPERMERCADOS:
        nombre_super = superm['nombre']
        url_api = f"{superm['url_base']}/api/catalog_system/pub/products/search?ft={termino_safe}"
        
        try:
            # Agregamos un timeout de 5 segundos para que la web no se quede colgada si un super no responde
            respuesta = requests.get(url_api, headers=headers, timeout=5)
            
            if respuesta.status_code in [200, 206]:
                datos = respuesta.json()
                
                for prod in datos:
                    try:
                        titulo = prod.get('productName', 'Sin nombre')
                        link = prod.get('link', '#')
                        items = prod.get('items', [])
                        
                        if items:
                            precio = items[0]['sellers'][0]['commertialOffer']['Price']
                            stock = items[0]['sellers'][0]['commertialOffer']['AvailableQuantity']
                            
                            if stock > 0 and precio > 0:
                                # Guardamos los datos empaquetados en un diccionario
                                resultados_totales.append({
                                    "supermercado": nombre_super,
                                    "producto": titulo,
                                    "precio": precio,
                                    "link": link
                                })
                    except:
                        continue
        except Exception:
            pass # Si hay error con un súper, lo ignoramos y seguimos con el otro

    # Ordenamos la lista final del más barato al más caro
    resultados_ordenados = sorted(resultados_totales, key=lambda x: x['precio'])
    return resultados_ordenados