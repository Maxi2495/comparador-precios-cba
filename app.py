from flask import Flask, request, render_template
# ¡AQUÍ ESTÁ LA MAGIA DE LA MODULARIZACIÓN! Importamos el chef a nuestro restaurante
from buscador import buscar_productos 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def inicio():
    palabra_ingresada = ""
    lista_resultados = [] # Arrancamos con una lista vacía
    
    if request.method == 'POST':
        palabra_ingresada = request.form.get('producto_buscado')
        print(f"La web está buscando: {palabra_ingresada}...")
        
        # Le pedimos al backend que haga el trabajo pesado
        lista_resultados = buscar_productos(palabra_ingresada)
        
    # Le pasamos la lista de resultados a nuestro diseño HTML
    return render_template('index.html', palabra_magica=palabra_ingresada, resultados=lista_resultados)

if __name__ == '__main__':
    app.run(debug=True)