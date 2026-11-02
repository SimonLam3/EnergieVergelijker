from flask import Flask, render_template, request

from EnergieVergelijker import vergelijk

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    resultaten = None

    if request.method == "POST":

        gegevens = {
            "postcode": request.form["postcode"],
            "huisnummer": int(request.form["huisnummer"]),
            "toevoeging": request.form["toevoeging"],
            "stroom_verbruik": int(request.form["stroom_verbruik"]),
            "stroom_verbruik_dal": int(request.form["stroom_verbruik_dal"]),
            "teruglevering": int(request.form["teruglevering"]),
            "teruglevering_dal": int(
                request.form["teruglevering_dal"]
            ),
            "gas": int(request.form["gas"]),
            "slimme_meter": (
                request.form.get("slimme_meter")
                == "on"
            )
        }

        resultaten = vergelijk(**gegevens)

    return render_template(
        "index.html",
        resultaten=resultaten
    )

if __name__ == "__main__":
    app.run(debug=True)
