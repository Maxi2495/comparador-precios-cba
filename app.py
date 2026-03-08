from flask import Flask, request, render_template
from buscador import buscar_productos 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def inicio():
    palabra_ingresada = ""
    lista_resultados = []
    
    if request.method == 'POST':
        # 1. Atrapamos el texto
        palabra_ingresada = request.form.get('producto_buscado')
        
        # 2. Atrapamos la lista de supermercados tildados (Ej: ['Disco', 'Vea'])
        supers_elegidos = request.form.getlist('supermercados')
        
        # 3. Atrapamos el orden ('menor' o 'mayor')
        orden_elegido = request.form.get('orden')
        
        print(f"Buscando: {palabra_ingresada} en {supers_elegidos} ordenado de {orden_elegido} a mayor...")
        
        # Le enviamos los 3 datos al backend
        lista_resultados = buscar_productos(palabra_ingresada, supers_elegidos, orden_elegido)
        
    return render_template('index.html', palabra_magica=palabra_ingresada, resultados=lista_resultados)

if __name__ == '__main__':
    app.run(debug=True)