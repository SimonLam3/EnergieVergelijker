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
            "resellerId": (
                "b393573d-1396-4b94-e177-08dc12b65bff"
            ),
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

    offers = data["salesChannels"][0]["offers"]

    for offer in offers:

        contract = (
            offer["proposition"]["externalName"]
        )

        mapping = {
            "Budget Energie Dynamisch":
                "dynamisch",

            "Budget Energie Variabel":
                "variabel",

            "Budget Energie 1 jaar vast":
                "1_jaar",

            "Budget Energie 3 jaar vast":
                "3_jaar"
        }

        contract_type = mapping.get(
            contract,
            "onbekend"
        )

        jaarprijs = (
            offer.get(
                "yearlyAmountTotal",
                {}
            ).get(
                "amountGross"
            )
        )

        maandprijs = None

        # Budget gebruikt niet altijd hetzelfde veld
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

        if maandprijs is None:
            print(
                f"Geen maandprijs gevonden voor: "
                f"{contract}"
            )
            print(
                offer.keys()
            )

        offertes.append({
            "leverancier": "Budget Energie",
            "contract": contract,
            "type": contract_type,
            "jaarprijs": jaarprijs,
            "maandprijs": maandprijs,
            "cashback": (
                offer.get(
                    "cashback",
                    {}
                ).get(
                    "amountGross",
                    0
                )
            )
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

        print(offerte["contract"])

        print(
            "Jaarprijs:",
            offerte["jaarprijs"]
        )

        print(
            "maandprijs:",
            offerte["maandprijs"]
        )

        print("-" * 40)