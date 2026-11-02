from providers.budget import budget
from providers.essent import essent
from providers.oxxio import oxxio
from providers.vattenfall import vattenfall
from providers.eneco import eneco
from providers.greenchoice import greenchoice

import matplotlib.pyplot as plt
import os

# --------------------------------------------------
# Mappen instellen
# --------------------------------------------------

SCRIPT_MAP = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(SCRIPT_MAP, "grafieken")

os.makedirs(MAP, exist_ok=True)

# --------------------------------------------------
# Grafiek maken
# --------------------------------------------------

def toon_grafiek(offertes, titel, bestandsnaam):

    if not offertes:
        print(f"Geen offertes gevonden voor {titel}")
        return

    offertes.sort(key=lambda x: x["jaarprijs"])

    goedkoopste = offertes[0]["jaarprijs"]

    namen = [
        f"{o['leverancier']} - {o['type']}"
        for o in offertes
    ]

    prijzen = [
        offerte["jaarprijs"]
        for offerte in offertes
    ]

    kleuren = [
        "green" if prijs == goedkoopste else "tomato"
        for prijs in prijzen
    ]

    plt.figure(figsize=(14, 6))
    plt.xlim(0, max(prijzen) * 1.15)

    bars = plt.barh(
        namen,
        prijzen,
        color=kleuren
    )

    plt.title(
        f"Energievergelijker - {titel}",
        fontsize=20
    )

    plt.suptitle(
        "Prijzen gebaseerd op nieuwe klantaanbiedingen. "
        "Controleer je verlengaanbod als bestaande klant.",
        fontsize=10,
        fontstyle="italic",
        y=0.98
    )

    plt.subplots_adjust(top=0.85)
    plt.tight_layout()

    plt.xlabel("Jaarprijs (€)")

    for bar, offerte in zip(bars, offertes):

        verschil = offerte["jaarprijs"] - goedkoopste

        plt.text(
            bar.get_width() + 10,
            bar.get_y() + bar.get_height() / 2,
            f"€{offerte['jaarprijs']:.0f} (+€{verschil:.0f})",
            va="center"
        )

    plt.gca().invert_yaxis()

    plt.tight_layout()

    plt.savefig(
        f"{MAP}/{bestandsnaam}",
        dpi=600,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Opgeslagen: {bestandsnaam}")


# --------------------------------------------------
# Vergelijking uitvoeren
# --------------------------------------------------

def vergelijk(
    postcode,
    huisnummer,
    toevoeging,
    stroom_verbruik,
    stroom_verbruik_dal,
    teruglevering,
    teruglevering_dal,
    gas,
    slimme_meter
):

    alle_offertes = []

    providers = [
    budget,
    essent,
    oxxio,
    vattenfall,
    eneco,
    greenchoice
]

    for provider in providers:

        try:

            offertes = provider(
                postcode,
                huisnummer,
                toevoeging,
                stroom_verbruik,
                stroom_verbruik_dal,
                teruglevering,
                teruglevering_dal,
                gas,
                slimme_meter
            )

            alle_offertes.extend(offertes)

            print(
                f"{provider.__name__}: "
                f"{len(offertes)} offertes"
            )

        except Exception as e:

            print(
                f"Fout bij {provider.__name__}: {e}"
            )

    een_jaar = [
        o for o in alle_offertes
        if o["type"] == "1_jaar"
    ]

    drie_jaar = [
        o for o in alle_offertes
        if o["type"] == "3_jaar"
    ]

    dynamisch = [
        o for o in alle_offertes
        if o["type"] == "dynamisch"
    ]

    variabel = [
        o for o in alle_offertes
        if o["type"] == "variabel"
    ]

    een_jaar.sort(key=lambda x: x["jaarprijs"])
    drie_jaar.sort(key=lambda x: x["jaarprijs"])
    dynamisch.sort(key=lambda x: x["jaarprijs"])
    variabel.sort(key=lambda x: x["jaarprijs"])

    return {
        "1_jaar": een_jaar,
        "3_jaar": drie_jaar,
        "dynamisch": dynamisch,
        "variabel": variabel
    }


# --------------------------------------------------
# Testmodus
# --------------------------------------------------

if __name__ == "__main__":

    gegevens = {
        "postcode": "7773AN",
        "huisnummer": 42,
        "toevoeging": "",
        "stroom_verbruik": 4000,
        "stroom_verbruik_dal": 4000,
        "teruglevering": 1500,
        "teruglevering_dal": 0,
        "gas": 500,
        "slimme_meter": True
    }

    resultaten = vergelijk(**gegevens)

    toon_grafiek(
        resultaten["1_jaar"],
        "1 Jaar Vast",
        "1_jaar_vast.png"
    )

    toon_grafiek(
        resultaten["3_jaar"],
        "3 Jaar Vast",
        "3_jaar_vast.png"
    )

    toon_grafiek(
        resultaten["dynamisch"],
        "Dynamisch",
        "dynamisch.png"
    )

    toon_grafiek(
        resultaten["variabel"],
        "Variabel",
        "variabel.png"
    )
