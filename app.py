from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

STORES = {
    "Amazon": "site:amazon.es",
    "PcComponentes": "site:pccomponentes.com",
    "MediaMarkt": "site:mediamarkt.es",
    "Carrefour": "site:carrefour.es",
    "Pixmania": "site:pixmania.com"
}

def search_bing(ean, store_filter):
    query = f'"{ean}" {store_filter}'
    url = f"https://www.bing.com/search?q={requests.utils.quote(query)}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.select("li.b_algo h2 a"):
        href = a.get("href")
        if href and store_filter.split(":")[1] in href:
            links.append(href)
    return links

def verify_ean_in_page(url, ean):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if ean in response.text:
            return True
    except Exception:
        pass
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    result_table = ""
    if request.method == "POST":
        ean = request.form.get("ean", "").strip()
        results = []
        for store, filter_query in STORES.items():
            links = search_bing(ean, filter_query)
            found = False
            for link in links:
                if verify_ean_in_page(link, ean):
                    results.append((store, "✅ Disponible", link))
                    found = True
                    break
            if not found:
                results.append((store, "❌ No disponible", links[0] if links else "—"))
        result_table = "<table border='1'><tr><th>Tienda</th><th>Estado</th><th>Enlace</th></tr>"
        for store, status, link in results:
            result_table += f"<tr><td>{store}</td><td>{status}</td><td><a href='{link}' target='_blank'>Ver</a></td></tr>"
        result_table += "</table>"

    return render_template_string("""
        <html>
        <head><title>Verificador de EAN</title></head>
        <body>
            <h2>Introduce un EAN para verificar disponibilidad</h2>
            <form method="post">
                <input type="text" name="ean" required>
                <input type="submit" value="Verificar">
            </form>
            <br>
            {{ result_table|safe }}
        </body>
        </html>
    """, result_table=result_table)

if __name__ == "__main__":
    app.run(debug=True)