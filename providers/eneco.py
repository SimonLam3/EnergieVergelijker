from flask import json
import requests

def eneco(
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
        "https://api-digital.enecogroup.com/"
        "dxpweb/public/v3/nl/eneco/products/offerproducts"
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "apikey": "673b639d7383463e8d7958387590acca",
        "origin": "https://www.eneco.nl",
        "referer": (
            "https://www.eneco.nl/"
            "duurzame-energie/bestellen2/productkeuze/looptijd/"
        )
    }

    payload = {
        "data": {
            "offerType": "NewEnergyContract",
            "allowDynamicOrHybridOnly": False,
            "includeRentalProducts": False,
            "isMkb": False,
            "isResidence": True,
            "movingCustomer": False,
            "urgent": False,
            "products": [
                "electricity",
                "gas"
            ],
            "address": {
                "postalCode": postcode,
                "houseNumber": int(huisnummer),
                "houseNumberSuffix": toevoeging
            },
            "usages": {
            "electricityNormal": stroom_verbruik,
            "electricityLow": stroom_verbruik_dal,
            "electricityRedeliveryNormal": teruglevering,
            "electricityRedeliveryLow": teruglevering_dal,
            "gas": gas,
            "warmthElectricity": 0,
            "warmthWater": 0
            }
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    producten = data["data"]["products"]

    stroom_producten = {}
    gas_producten = {}

    for product in producten:

        naam = product["description"]

        jaarprijs = None
        maandprijs = None

        for cost in product["costDetails"]:

            if cost["type"] == "yearlyCosts":
                jaarprijs = cost["costs"]["vatIncluded"]

            elif cost["type"] == "monthlyCosts":
                maandprijs = cost["costs"]["vatIncluded"]

        if jaarprijs is None:
            continue

        if product["productType"] == "electricity":

            stroom_producten[naam] = {
                "jaarprijs": jaarprijs,
                "maandprijs": maandprijs
            }

        elif product["productType"] == "gas":

            gas_producten[naam] = {
                "jaarprijs": jaarprijs,
                "maandprijs": maandprijs
            }

    offertes = []

    for naam, stroom in stroom_producten.items():

        gas_naam = None
        contract_type = "onbekend"

        if "Dynamisch" in naam:

            gas_naam = "Eneco Dynamisch Gas"
            contract_type = "dynamisch"

        elif "3 jaar" in naam:

            gas_naam = "Eneco Gas 3 jaar"
            contract_type = "3_jaar"

        elif "VariabelePrijs" in naam:

            gas_naam = "Eneco Gas VariabelePrijs"
            contract_type = "variabel"

        elif "1 jaar" in naam:

            gas_naam = "Eneco Gas 1 jaar"
            contract_type = "1_jaar"

        if gas_naam not in gas_producten:
            continue

        gas = gas_producten[gas_naam]

        jaarprijs = (
            stroom["jaarprijs"]
            + gas["jaarprijs"]
        )

        maandprijs = (
            stroom["maandprijs"]
            + gas["maandprijs"]
        )

        offertes.append({
            "leverancier": "Eneco",
            "contract": naam,
            "type": contract_type,
            "jaarprijs": round(jaarprijs, 2),
            "maandprijs": round(maandprijs, 2)
        })

    return offertes


if __name__ == "__main__":

    resultaten = eneco(
        postcode="7773AN",
        huisnummer=42,
        toevoeging="",
        stroom_verbruik=5000,
        stroom_verbruik_dal=4000,
        teruglevering=0,
        teruglevering_dal=0,
        gas=500,
        slimme_meter=True
    )

    for offerte in resultaten:

        print(
            offerte["leverancier"],
            offerte["type"]
        )

        print(
            offerte["contract"]
        )

        print(
            offerte["jaarprijs"]
        )

        print("-" * 40)