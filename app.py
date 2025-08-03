from flask import Flask, render_template, request
import webbrowser

app = Flask(__name__)

def generate_links(ean):
    return {
        "Amazon": f"https://www.amazon.es/s?k={ean}",
        "PcComponentes": f"https://www.pccomponentes.com/buscar/?query={ean}",
        "MediaMarkt": f"https://www.mediamarkt.es/es/search.html?query={ean}",
        "Carrefour": f"https://www.carrefour.es/search-results/?q={ean}",
        "Pixmania": f"https://www.pixmania.com/search?query={ean}"
    }

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    ean = ""
    if request.method == "POST":
        ean = request.form["ean"]
        results = generate_links(ean)
    return render_template("index.html", results=results, ean=ean)

if __name__ == "__main__":
    app.run(debug=True)
