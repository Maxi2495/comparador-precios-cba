import requests
import urllib.parse

def buscar_en_disco(termino_busqueda):
    termino_safe = urllib.parse.quote(termino_busqueda)
    # Pedimos de la 0 a la 19 (20 productos) usando _from y _to si fuera necesario, 
    # pero el buscador por defecto ya pagina.
    url_api = f"https://www.disco.com.ar/api/catalog_system/pub/products/search?ft={termino_safe}"
    
    print(f"🔄 Buscando '{termino_busqueda}'...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        
        respuesta = requests.get(url_api, headers=headers)
        
        # --- CORRECCIÓN AQUÍ ---
        # Aceptamos 200 (OK) y 206 (Contenido Parcial) como válidos
        if respuesta.status_code not in [200, 206]:
            print(f"❌ Error real de conexión. Código: {respuesta.status_code}")
            return

        productos = respuesta.json()
        
        if len(productos) == 0:
            print("❌ La búsqueda no arrojó resultados (Lista vacía).")
            return

        print(f"\n✅ ¡Encontramos {len(productos)} productos!")
        print("(Mostrando los primeros 10)")
        print("="*60)

        for prod in productos[:10]:
            nombre = prod.get('productName', 'Sin nombre')
            link_producto = prod.get('link', '#')
            
            # Buscamos el precio con cuidado
            precio = 0.0
            try:
                # Navegamos el JSON del producto
                precio = prod['items'][0]['sellers'][0]['commertialOffer']['Price']
            except:
                precio = 0.0
            
            print(f"🍺 Producto: {nombre}")
            print(f"📊 Precio Base: ${precio}")
            print(f"🔗 Link: {link_producto}")
            print("-" * 60)

    except Exception as e:
        print(f"💥 Error inesperado: {e}")

# --- LOOP PRINCIPAL ---
while True:
    print("\n" + "*"*30)
    busqueda = input("🔍 ¿Qué buscas? (o 'salir'): ")
    if busqueda.lower() == 'salir':
        print("¡Éxitos con el estudio! 👋")
        break
    buscar_en_disco(busqueda)