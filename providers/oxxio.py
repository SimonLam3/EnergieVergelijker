import requests

def oxxio(
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
        "dxpweb/public/v3/nl/oxxio/products/offerproducts"
    )

    headers = {
        "ApiKey": "d86c181f8481446cb671c38f1bae52fd",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.oxxio.nl",
        "Referer": "https://www.oxxio.nl/"
    }

    payload = {
        "data": {
            "offerType": "NewEnergyContract",

            "address": {
                "postalCode": postcode,
                "houseNumber": int(huisnummer),
                "houseNumberSuffix": toevoeging
            },

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

    offertes = []

    for combinatie in data["data"]["productCombinations"]:

        contract_type = combinatie["discountType"]

        if contract_type == "dynamicPricing":
            contract = "Dynamisch"
            type_contract = "dynamisch"

        elif contract_type == "newEnergyHybrid1Year":
            contract = "1 jaar vast"
            type_contract = "1_jaar"

        elif contract_type == "newEnergyHybrid3Years":
            contract = "3 jaar vast"
            type_contract = "3_jaar"

        else:
            contract = contract_type
            type_contract = "onbekend"

        jaarprijs = None
        maandprijs = None

        for cost in combinatie["costDetails"]:

            if cost["type"] == "yearlyCosts":
                jaarprijs = cost["costs"]["vatIncluded"]

            elif cost["type"] == "monthlyCosts":
                maandprijs = cost["costs"]["vatIncluded"]

        if jaarprijs is None:
            continue

        offertes.append({
            "leverancier": "Oxxio",
            "contract": contract,
            "type": type_contract,
            "jaarprijs": jaarprijs,
            "maandprijs": maandprijs
        })

    return offertes

if __name__ == "__main__":

    resultaten = oxxio(
        postcode="7773AN",
        huisnummer=42,
        toevoeging="",
        stroom_verbruik=4000,
        stroom_verbruik_dal=4000,
        teruglevering=1500,
        teruglevering_dal=0,
        gas=500,
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
