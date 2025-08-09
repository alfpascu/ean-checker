from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Verificador de EAN</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        table { border-collapse: collapse; width: 100%%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        input[type=text] { width: 300px; padding: 8px; }
        input[type=submit] { padding: 8px 16px; }
    </style>
</head>
<body>
    <h1>Verificador de EAN</h1>
    <form method="post">
        <label>Introduce el EAN:</label>
        <input type="text" name="ean" required>
        <input type="submit" value="Verificar">
    </form>
    {% if results %}
    <h2>Resultados para EAN {{ ean }}</h2>
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

def buscar_en_bing(ean, tienda):
    query = f"{ean} site:{tienda}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    params = {
        "q": query,
        "count": 10
    }
    try:
        response = requests.get("https://www.bing.com/search", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            html = response.text.lower()
            if ean in html:
                return "✅ Sí", f"https://www.bing.com/search?q={ean}+site:{tienda}"
            else:
                return "❌ No", f"https://www.bing.com/search?q={ean}+site:{tienda}"
        else:
            return "⚠️ Error", f"https://www.bing.com/search?q={ean}+site:{tienda}"
    except Exception:
        return "⚠️ Error", f"https://www.bing.com/search?q={ean}+site:{tienda}"

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
        for nombre, dominio in tiendas.items():
            estado, enlace = buscar_en_bing(ean, dominio)
            results.append((nombre, estado, enlace))
    return render_template_string(HTML_TEMPLATE, results=results, ean=ean)

if __name__ == "__main__":
    app.run(debug=True)
