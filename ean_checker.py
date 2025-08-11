from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

MARKETPLACES = {
    'Amazon': 'https://www.amazon.es/s?k={ean}',
    'PCComponentes': 'https://www.pccomponentes.com/buscar/?query={ean}',
    'MediaMarkt': 'https://www.mediamarkt.es/es/search.html?query={ean}',
    'Carrefour': 'https://www.carrefour.es/search?query={ean}',
    'Pixmania': 'https://www.pixmania.com/search?query={ean}'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    ean = ''
    if request.method == 'POST':
        ean = request.form['ean']
        for name, url in MARKETPLACES.items():
            try:
                page = requests.get(
                    url.format(ean=ean),
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=5
                )
                soup = BeautifulSoup(page.text, "html.parser")
                results[name] = not ("no hay resultados" in soup.text.lower() or len(soup.text) < 1000)
            except Exception as e:
                results[name] = False
    return render_template('index.html', results=results, ean=ean)

if __name__ == '__main__':
    app.run(debug=True)
