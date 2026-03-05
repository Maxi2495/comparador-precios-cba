import sqlite3

# Conectamos a la base de datos
conexion = sqlite3.connect('precios.db')
cursor = conexion.cursor()

# 1. Consulta Relacional (JOIN)
print("--- HISTORIAL DE RESULTADOS ---")
cursor.execute('''
    SELECT b.fecha, b.termino, r.supermercado, r.producto, r.precio
    FROM busquedas b
    JOIN resultados r ON b.id = r.busqueda_id
    WHERE b.termino = 'Fernet'
    LIMIT 10
''')

# Imprimimos los primeros 10 resultados encontrados
for fila in cursor.fetchall():
    fecha, termino, supermercado, producto, precio = fila
    print(f"[{fecha}] {supermercado}: {producto} a ${precio}")

# 2. Consulta Estadística (Funciones de Agregación)
print("\n--- ANÁLISIS ESTADÍSTICO DE LA MUESTRA ---")
cursor.execute('''
    SELECT 
        COUNT(r.id),
        MIN(r.precio),
        MAX(r.precio),
        ROUND(AVG(r.precio), 2)
    FROM busquedas b
    JOIN resultados r ON b.id = r.busqueda_id
    WHERE b.termino = 'Fernet'
''')

stats = cursor.fetchone()
cantidad, minimo, maximo, promedio = stats

print(f"Tamaño de la muestra (n): {cantidad} productos")
print(f"Rango de precios: ${minimo} - ${maximo}")
print(f"Media aritmética (Promedio): ${promedio}")

conexion.close()