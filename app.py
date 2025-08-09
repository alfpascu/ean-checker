from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>EAN Checker v9</title>
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

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIENDAS = {
    "Amazon": "site:amazon.es",
    "PcComponentes": "site:pccomponentes.com",
    "MediaMarkt": "site:mediamarkt.es",
    "Carrefour": "site:carrefour.es",
    "Pixmania": "site:pixmania.com"
}

def buscar_en_google(ean, tienda_query):
    query = f'"{ean}" {tienda_query}'
    url = f"https://www.google.com/search?q={query}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        enlaces = []
        for g in soup.select("div.g"):
            link_tag = g.find("a")
            if link_tag and ean in g.text:
                enlaces.append(link_tag["href"])
        return enlaces
    except Exception:
        return []

def verificar_ean_enlace(ean, enlace):
    try:
        response = requests.get(enlace, headers=HEADERS, timeout=10)
        return ean in response.text
    except Exception:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    ean = ""
    if request.method == "POST":
        ean = request.form["ean"]
        for tienda, query in TIENDAS.items():
            enlaces = buscar_en_google(ean, query)
            disponible = False
            enlace_final = enlaces[0] if enlaces else "#"
            if enlaces:
                disponible = verificar_ean_enlace(ean, enlace_final)
            estado = "✅ Sí" if disponible else "❌ No"
            results.append((tienda, estado, enlace_final))
    return render_template_string(TEMPLATE, results=results, ean=ean)

if __name__ == "__main__":
    app.run(debug=True)
