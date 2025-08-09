from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Verificador de EAN</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        table { border-collapse: collapse; width: 100%%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
        input[type=text] { width: 300px; padding: 8px; }
        input[type=submit] { padding: 8px 16px; }
    </style>
</head>
<body>
    <h2>Verificador de EAN</h2>
    <form method="post">
        <label>Introduce el EAN:</label>
        <input type="text" name="ean" required>
        <input type="submit" value="Verificar">
    </form>
    {% if results %}
    <h3>Resultados para EAN {{ ean }}</h3>
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

def buscar_en_bing(ean, tienda, dominio):
    query = f"{ean} site:{dominio}"
    url = f"https://www.bing.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if "No results found" in response.text or "no se han encontrado resultados" in response.text.lower():
            return "❌ No", url
        elif "result" in response.text.lower():
            return "✅ Sí", url
        else:
            return "❌ No", url
    except Exception:
        return "⚠️ Error", url

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    ean = ""
    if request.method == "POST":
        ean = request.form["ean"]
        tiendas = {
            "Amazon": "amazon.es",
            "PcComponentes": "pccomponentes.com",
            "MediaMarkt": "mediamarkt.es",
            "Carrefour": "carrefour.es",
            "Pixmania": "pixmania.com"
        }
        for tienda, dominio in tiendas.items():
            estado, enlace = buscar_en_bing(ean, tienda, dominio)
            results.append((tienda, estado, enlace))
    return render_template_string(TEMPLATE, results=results, ean=ean)

if __name__ == "__main__":
    app.run(debug=True)
