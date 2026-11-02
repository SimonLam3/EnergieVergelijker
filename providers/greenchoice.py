import requests

def greenchoice(
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
    
    url = (
        "https://www.greenchoice.nl/"
        "api/n/consumerEnergyPropositionOffers"
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.greenchoice.nl",
        "referer": "https://www.greenchoice.nl/aanmelden-v2/?stap=aanbod",
        "user-agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/155.0.0.0 "
            "Safari/537.36 "
            "Edg/155.0.0.0"
        )
    }

    payload = {
        "address": {
            "postalCode": postcode,
            "houseNumber": int(huisnummer),
            "houseNumberAddition": toevoeging
        },
        "homeOrWorkAddress": True,
        "hasDoubleMeter": slimme_meter,
        "usage": {
            "afnameGas": gas,
            "afnameStroomNormaal": stroom_verbruik,
            "afnameStroomDal": stroom_verbruik_dal,
            "invoedingStroomNormaal": teruglevering,
            "invoedingStroomDal": teruglevering_dal
        },
        "pageId": "9901755e-3c9c-4b7e-ae34-c09868b1ed97"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    offertes = []

    for offer in data["offers"]:

        naam = offer["proposition"]["weergaveNaam"]

        jaarprijs = offer["prognosis"]["totaalInclBtw"]

        maandprijs = offer["prognosis"]["termijnbedrag"]

        looptijd = offer["proposition"].get(
            "looptijdInMaanden",
            0
        )

        if looptijd == 12:
            contract_type = "1_jaar"

        elif looptijd == 24:
            contract_type = "2_jaar"

        elif looptijd == 36:
            contract_type = "3_jaar"

        elif offer.get("durationType") == "Ongoing":
            contract_type = "variabel"

        else:
            contract_type = "onbekend"

        offertes.append({
            "leverancier": "Greenchoice",
            "contract": naam,
            "type": contract_type,
            "jaarprijs": round(jaarprijs, 2),
            "maandprijs": round(maandprijs, 2)
        })

    dynamic = data.get("dynamicOffer")

    if dynamic:

        offertes.append({
            "leverancier": "Greenchoice",
            "contract": dynamic["name"],
            "type": "dynamisch",
            "jaarprijs": round(
                dynamic["calculation"]["gasEnStroom"]
                ["totaalPerJaar"]["inclBtw"],
                2
            ),
            "maandprijs": round(
                dynamic["calculation"]["gasEnStroom"]
                ["totaalPerMaand"]["inclBtw"],
                2
            )
        })

    return offertes


if __name__ == "__main__":

    resultaten = greenchoice(
        postcode="7773AN",
        huisnummer=42,
        toevoeging="",
        stroom_verbruik=5000,
        stroom_verbruik_dal=5000,
        teruglevering=1500,
        teruglevering_dal=1500,
        gas=1200,
        slimme_meter=True
    )

    resultaten.sort(
        key=lambda x: x["jaarprijs"]
    )

    for offerte in resultaten:

        print(
            f"{offerte['contract']} "
            f"- €{offerte['jaarprijs']:.2f}/jaar "
            f"- €{offerte['maandprijs']:.2f}/maand"
        )