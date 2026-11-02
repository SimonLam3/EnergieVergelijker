from flask import Flask, render_template, request
from EnergieVergelijker import vergelijk

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    resultaten = None

    if request.method == "POST":
        resultaten = vergelijk()

    return render_template(
        "index.html",
        resultaten=resultaten
    )

if __name__ == "__main__":
    app.run(debug=True)
