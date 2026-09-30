from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Flask buscará automáticamente el archivo index.html dentro de la carpeta 'templates'
    return render_template('index.html')

if __name__ == '__main__':
    # Ejecuta el servidor en modo de desarrollo
    app.run(debug=True, port=5000)
