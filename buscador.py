import requests
import urllib.parse

# Nuestro diccionario de supermercados disponibles
SUPERMERCADOS = {
    "1": {"nombre": "Disco", "url": "https://www.disco.com.ar"},
    "2": {"nombre": "Vea",   "url": "https://www.vea.com.ar"},
    "3": {"nombre": "Jumbo", "url": "https://www.jumbo.com.ar"}
}

def buscar_en_supermercado(termino_busqueda, url_base, nombre_super):
    termino_safe = urllib.parse.quote(termino_busqueda)
    
    # Armamos la URL dinámica usando el dominio que elegiste
    url_api = f"{url_base}/api/catalog_system/pub/products/search?ft={termino_safe}"
    
    print(f"\n🔄 Buscando '{termino_busqueda}' en {nombre_super}...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        
        respuesta = requests.get(url_api, headers=headers)
        
        if respuesta.status_code not in [200, 206]:
            print(f"❌ Error de conexión con {nombre_super}. Código: {respuesta.status_code}")
            return

        productos = respuesta.json()
        
        if len(productos) == 0:
            print("❌ La búsqueda no arrojó resultados.")
            return

        print(f"✅ ¡Encontramos {len(productos)} productos!")
        print("(Mostrando los primeros 10)")
        print("="*60)

        for prod in productos[:10]:
            nombre = prod.get('productName', 'Sin nombre')
            link_producto = prod.get('link', '#')
            
            precio = 0.0
            try:
                precio = prod['items'][0]['sellers'][0]['commertialOffer']['Price']
            except:
                precio = 0.0
            
            print(f"🛒 Supermercado: {nombre_super}")
            print(f"🍺 Producto: {nombre}")
            print(f"📊 Precio Base: ${precio}")
            print(f"🔗 Link: {link_producto}")
            print("-" * 60)

    except Exception as e:
        print(f"💥 Error inesperado: {e}")

# --- LOOP PRINCIPAL CON MENÚ ---
while True:
    print("\n" + "*"*40)
    print("      EL GRAN COMPARADOR DE PRECIOS")
    print("*"*40)
    print("Elige un supermercado:")
    print("1. Disco")
    print("2. Vea")
    print("3. Jumbo")
    print("4. Salir")
    
    opcion = input("👉 Ingresa el número de tu opción: ")
    
    if opcion == "4":
        print("¡Nos vemos! 👋")
        break
        
    if opcion in SUPERMERCADOS:
        super_elegido = SUPERMERCADOS[opcion]
        busqueda = input(f"🔍 ¿Qué quieres buscar en {super_elegido['nombre']}?: ")
        
        # Le pasamos a la función qué buscar, la URL de ese super, y su nombre
        buscar_en_supermercado(busqueda, super_elegido['url'], super_elegido['nombre'])
    else:
        print("❌ Opción no válida. Por favor, elige 1, 2, 3 o 4.")