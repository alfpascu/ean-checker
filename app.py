import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EAN Checker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        input[type=text] { width: 300px; padding: 8px; }
        input[type=submit] { padding: 8px 16px; }
        table { border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Verificador de EAN</h1>
    <form method="post">
        <label for="ean">Introduce el EAN:</label>
        <input type="text" name="ean" required>
        <input type="submit" value="Verificar">
    </form>
    {% if results %}
    <table>
        <tr><th>Tienda</th><th>Disponible</th><th>Enlace</th></tr>
        {% for tienda, estado, enlace in results %}
        <tr>
            <td>{{ tienda }}</td>
            <td>{{ estado }}</td>
            <td><a href="{{ enlace }}" target="_blank">Ver</a></td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

TIENDAS = {
    "Amazon": "https://www.amazon.es/s?k={ean}",
    "PcComponentes": "https://www.pccomponentes.com/buscar/?query={ean}",
    "MediaMarkt": "https://www.mediamarkt.es/es/search.html?query={ean}",
    "Carrefour": "https://www.carrefour.es/search?text={ean}",
    "Pixmania": "https://www.pixmania.com/search?q={ean}"
}

def verificar_ean(ean):
    resultados = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for tienda, url_template in TIENDAS.items():
        url = url_template.format(ean=ean)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            disponible = "✅ Sí" if ean in response.text else "❌ No"
        except Exception:
            disponible = "⚠️ Error"
        resultados.append((tienda, disponible, url))
    return resultados

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    if request.method == "POST":
        ean = request.form["ean"]
        resultados = verificar_ean(ean)
    return render_template_string(HTML_TEMPLATE, results=resultados)

if __name__ == "__main__":
    app.run(debug=True)
