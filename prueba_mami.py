import requests
from bs4 import BeautifulSoup
import re

url_mami = "https://www.supermami.com.ar/super/categoria?_dyncharset=utf-8&Dy=1&Nty=1&minAutoSuggestInputLength=3&autoSuggestServiceUrl=%2Fassembler%3FassemblerContentCollection%3D%2Fcontent%2FShared%2FAuto-Suggest+Panels%26format%3Djson&searchUrl=%2Fsuper&containerClass=search_rubricator&defaultImage=%2Fimages%2Fno_image_auto_suggest.png&rightNowEnabled=false&Ntt=cerveza"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔄 Conectando y analizando código...")
respuesta = requests.get(url_mami, headers=headers)

if respuesta.status_code == 200:
    # 1. BeautifulSoup convierte el texto plano en una estructura navegable
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    
    # 2. Aislamos todas las etiquetas <script>
    scripts = sopa.find_all('script')
    
    for script in scripts:
        # 3. Filtramos el script exacto que contiene las variables que viste en el F12
        if script.string and '"item_name"' in script.string and '"price"' in script.string:
            
            # 4. Aplicamos la Expresión Regular (nuestro patrón de búsqueda)
            # Busca "item_name": "ALGO", ignora el medio, y atrapa "price": NUMERO
            patron = r'"item_name":\s*"([^"]+)".*?"price":\s*([\d\.]+)'
            
            # re.findall nos devuelve una lista de tuplas con los pares (nombre, precio)
            productos_aislados = re.findall(patron, script.string, re.DOTALL)
            
            print(f"Procesamiento terminado. Se aislaron {len(productos_aislados)} productos.\n")
            
            # Imprimimos los primeros 5 para verificar los datos
            for nombre, precio in productos_aislados[:5]:
                print(f"Producto: {nombre}")
                print(f"Precio: ${precio}")
                print("-" * 40)
            break
else:
    print(f"Error de conexión. Código: {respuesta.status_code}")