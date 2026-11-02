import requests


def budget(
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

    response = requests.post(
        "https://api.budgetthuis.nl/energy/v1/online-offers",
        json={
            "resellerId": "b393573d-1396-4b94-e177-08dc12b65bff",
            "hasSmartMeter": slimme_meter,
            "address": {
                "postalCode": postcode,
                "houseNumber": huisnummer,
                "extension": toevoeging
            },
            "usage": {
                "eacPeak": stroom_verbruik,
                "eacOffPeak": stroom_verbruik_dal,
                "eapPeak": teruglevering,
                "eapOffPeak": teruglevering_dal,
                "gas": gas
            }
        }
    )

    response.raise_for_status()

    data = response.json()

    offertes = []

    for offer in data["salesChannels"][0]["offers"]:

        contract = offer["proposition"]["externalName"]

        if contract == "Budget Energie 1 jaar vast":
            contract_type = "1_jaar"

        elif contract == "Budget Energie 3 jaar vast":
            contract_type = "3_jaar"

        elif contract == "Budget Energie Variabel":
            contract_type = "variabel"

        elif contract == "Budget Energie Dynamisch":
            contract_type = "dynamisch"

        else:
            contract_type = "onbekend"

        jaarprijs = None

        for veld in [
            "yearlyAmountTotal",
            "yearlyAmountRawTotal",
            "yearlyAmount"
        ]:
            if veld in offer:
                jaarprijs = (
                    offer[veld]
                    .get("amountGross")
                )
                break

        maandprijs = None

        for veld in [
            "monthlyAmountTotal",
            "monthlyAmountRawTotal",
            "monthlyAmount"
        ]:
            if veld in offer:
                maandprijs = (
                    offer[veld]
                    .get("amountGross")
                )
                break

        if jaarprijs is None:
            print(
                f"Geen jaarprijs gevonden voor: "
                f"{contract}"
            )
            print(offer.keys())
            continue

        if maandprijs is None:
            print(
                f"Geen maandprijs gevonden voor: "
                f"{contract}"
            )
            print(offer.keys())
            continue

        offertes.append({
            "leverancier": "Budget Energie",
            "contract": contract,
            "type": contract_type,
            "jaarprijs": jaarprijs,
            "maandprijs": maandprijs
        })

    return offertes


if __name__ == "__main__":

    resultaten = budget(
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

    resultaten.sort(
        key=lambda x: x["jaarprijs"]
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
            "Jaarprijs:",
            offerte["jaarprijs"]
        )

        print(
            "Maandprijs:",
            offerte["maandprijs"]
        )

        print("-" * 40)