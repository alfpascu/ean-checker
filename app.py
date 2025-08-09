from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>EAN Checker v5</title>
<h2>Verificador de EAN en Marketplaces</h2>
<form method=post>
  <input type=text name=ean placeholder="Introduce el EAN" required>
  <input type=submit value=Verificar>
</form>
{% if results %}
  <h3>Resultados para EAN {{ ean }}:</h3>
  <table border=1 cellpadding=5>
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
"""

def buscar_en_bing(ean, tienda):
    query = f"{ean} site:{tienda}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.bing.com/search?q={query}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        resultados = soup.select("li.b_algo")
        for r in resultados:
            titulo = r.select_one("h2")
            desc = r.select_one(".b_caption p")
            enlace = titulo.a["href"] if titulo and titulo.a else ""
            texto = (titulo.text if titulo else "") + " " + (desc.text if desc else "")
            if ean in texto or ean in enlace:
                return "✅ Sí", enlace
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
            "Amazon": "amazon.com",
            "PcComponentes": "pccomponentes.com",
            "MediaMarkt": "mediamarkt.es",
            "Carrefour": "carrefour.es",
            "Pixmania": "pixmania.com"
        }
        for nombre, dominio in tiendas.items():
            estado, enlace = buscar_en_bing(ean, dominio)
            results.append((nombre, estado, enlace))
    return render_template_string(TEMPLATE, results=results, ean=ean)

if __name__ == "__main__":
    app.run(debug=True)
