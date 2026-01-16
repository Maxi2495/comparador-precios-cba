import requests
from bs4 import BeautifulSoup
import json

# Función auxiliar para limpiar precios (quitar $, puntos y comas)
def limpiar_precio(texto_precio):
    try:
        # Quitamos el símbolo $ y espacios
        texto = texto_precio.replace('$', '').replace(' ', '').strip()
        # En Argentina se usa punto para miles y coma para decimales.
        # Python usa punto para decimales.
        # Truco: Quitamos el punto de los miles y reemplazamos la coma por punto.
        texto = texto.replace('.', '').replace(',', '.')
        return float(texto)
    except:
        return 0.0

def analizar_producto(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"🔎 Analizando: {url}")
    
    try:
        # 1. OBTENER HTML (PRECIO FINAL)
        respuesta = requests.get(url, headers=headers)
        if respuesta.status_code != 200:
            return "Error de conexión"
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        titulo = soup.title.string.strip()
        print(f"📦 Producto: {titulo}")
        
        # Buscamos el precio visual (Lo que paga el cliente)
        # Usamos el ID que descubriste tú
        etiqueta_precio_final = soup.find("div", id="priceContainer")
        
        precio_final = 0.0
        if etiqueta_precio_final:
            texto = etiqueta_precio_final.get_text()
            precio_final = limpiar_precio(texto)
            print(f"💲 Precio en Góndola (HTML): ${precio_final}")
        else:
            print("❌ No se encontró el precio visual (HTML).")

        # 2. OBTENER API (PRECIO BASE)
        # Buscamos el SKU primero
        scripts = soup.find_all("script", type="application/ld+json")
        sku_id = None
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Product':
                    sku_id = data.get('sku')
                    break
            except:
                continue
        
        precio_base = 0.0
        if sku_id:
            url_api = f"https://www.disco.com.ar/api/catalog_system/pub/products/search?fq=skuId:{sku_id}"
            resp_api = requests.get(url_api)
            data_api = resp_api.json()
            
            try:
                # Vamos a buscar el precio "Price" que vimos en el JSON (el de 3942)
                precio_base = data_api[0]['items'][0]['sellers'][0]['commertialOffer']['Price']
                print(f"📊 Precio Base en Sistema (API): ${precio_base}")
            except:
                print("⚠️ No se pudo leer el precio base de la API.")
        
        # 3. EL VEREDICTO (COMPARACIÓN)
        print("-" * 30)
        
        if precio_final > 0 and precio_base > 0:
            # Si el precio final es MENOR al base, hay descuento real
            if precio_final < precio_base:
                ahorro = precio_base - precio_final
                porcentaje = (ahorro / precio_base) * 100
                print(f"🔥 ¡OFERTA DETECTADA!")
                print(f"   Antes: ${precio_base}")
                print(f"   Ahora: ${precio_final}")
                print(f"   Ahorras: {porcentaje:.1f}% (${ahorro:.2f})")
            elif precio_final == precio_base:
                print("ℹ️ Precio normal (Sin descuento detectado).")
            else:
                # Caso raro: El HTML es más caro que la API (¿Error de actualización?)
                print("⚠️ Curioso: El precio en web es mayor que en sistema.")
        else:
            print("❌ No se pudieron comparar los precios.")
            
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

# --- LISTA DE PRUEBA ---
productos = [
    "https://www.disco.com.ar/cerveza-rubia-330ml-corona-2/p", # La que tiene descuento
    "https://www.disco.com.ar/cerveza-quilmes-clasica-lata-473-cc/p" # Una normal para probar
]

for link in productos:
    analizar_producto(link)