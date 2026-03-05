import sqlite3

def inicializar_base_datos():
    # Se conecta al archivo (si no existe, lo crea automáticamente)
    conexion = sqlite3.connect('precios.db')
    cursor = conexion.cursor()

    # Tabla 1: Registra el evento de búsqueda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS busquedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termino TEXT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla 2: Registra los productos encontrados vinculados a la búsqueda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            busqueda_id INTEGER,
            supermercado TEXT NOT NULL,
            producto TEXT NOT NULL,
            precio REAL NOT NULL,
            link TEXT,
            FOREIGN KEY (busqueda_id) REFERENCES busquedas (id)
        )
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos y tablas creadas con éxito.")

if __name__ == '__main__':
    inicializar_base_datos()