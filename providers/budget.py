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

    url = "https://api.budgetthuis.nl/energy/v1/online-offers"

    payload = {
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

    response = requests.post(
        url,
        json=payload
    )

    response.raise_for_status()

    data = response.json()

    offertes = []

    for offer in data["salesChannels"][0]["offers"]:

        contract = offer["proposition"]["externalName"]

        if contract == "Budget Energie Dynamisch":
            contract_type = "dynamisch"

        elif contract == "Budget Energie Variabel":
            contract_type = "variabel"

        elif contract == "Budget Energie 1 jaar vast":
            contract_type = "1_jaar"

        elif contract == "Budget Energie 3 jaar vast":
            contract_type = "3_jaar"

        else:
            contract_type = "onbekend"

        offertes.append({
            "leverancier": "Budget Energie",
            "contract": contract,
            "type": contract_type,
            "jaarprijs": offer[
                "yearlyAmountIncludingCashback"
            ]["amountGross"],
            "maandprijs": offer[
                "monthlyAmountIncludingCashback"
            ]["amountGross"]
        })

    return offertes