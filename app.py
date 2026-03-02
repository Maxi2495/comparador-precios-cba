# Importamos Flask, request y render_template (ya no usamos _string)
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def inicio():
    palabra_ingresada = ""
    
    if request.method == 'POST':
        palabra_ingresada = request.form.get('producto_buscado')
        print(f"El usuario buscó: {palabra_ingresada}")
        
    # Magia de Flask: Va a la carpeta 'templates', agarra 'index.html' y le inyecta la palabra
    return render_template('index.html', palabra_magica=palabra_ingresada)

if __name__ == '__main__':
    app.run(debug=True)