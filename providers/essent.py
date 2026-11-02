import requests


def essent(
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

    flow_id = "L-9f6d1578-7c89-48cc-b9ad-92621cc29d8e"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-request-origin": "client",
        "x-client-version": "4.508.10",
        "origin": "https://www.essent.nl",
        "referer": "https://www.essent.nl/"
    }

    # Sessie opbouwen
    session.get(
        "https://www.essent.nl/",
        headers=headers
    )

    # Zelfde calls als de browser uitvoert
    for endpoint in [
        "metadata/v1",
        "installationdetails/v2",
        "consumption/v2",
        "supplyaddress/v2"
    ]:
        response = session.get(
            f"https://www.essent.nl/api/public/commodityacquisition/{endpoint}",
            params={
                "flow_id": flow_id
            },
            headers=headers
        )

    # Verbruik opslaan
    consumption_payload = {
        "meta_data": {
            "flow_id": flow_id
        },
        "payload": [
            {
                "energy_type": "electricity",
                "standard_annual_usages": [
                    {
                        "direction_tariff": "supply_low",
                        "reading": stroom_verbruik_dal
                    },
                    {
                        "direction_tariff": "supply_normal",
                        "reading": stroom_verbruik
                    },
                    {
                        "direction_tariff": "return_supply_low",
                        "reading": teruglevering_dal
                    },
                    {
                        "direction_tariff": "return_supply_normal",
                        "reading": teruglevering
                    }
                ]
            },
            {
                "energy_type": "gas",
                "standard_annual_usages": [
                    {
                        "direction_tariff": "supply_normal",
                        "reading": gas
                    }
                ]
            }
        ]
    }

    response = session.put(
        "https://www.essent.nl/api/public/commodityacquisition/consumption/v2",
        json=consumption_payload,
        headers=headers
    )

    response.raise_for_status()

    # Offertes ophalen
    response = session.get(
        "https://www.essent.nl/api/public/cplusactivation/offers/v1",
        params={
            "flow_id": flow_id,
            "offer_set": "Basis Offerset Essent",
            "customer_segment": "household",
            "postcode": postcode,
            "house_number": huisnummer,
            "house_number_extension": toevoeging,
            "electricity": stroom_verbruik,
            "electricity_low": stroom_verbruik_dal,
            "electricity_return": (
                teruglevering +
                teruglevering_dal
            ),
            "gas": gas,
            "duration_filter": "all_durations"
        },
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    offertes = []

    for offer in data["offers"]:

        contract = offer["productTitle"]

        if contract == "Groene Stroom & Gas 1 jaar":
            contract_type = "1_jaar"

        elif contract == "Groene Stroom & Gas 3 jaar":
            contract_type = "3_jaar"

        elif contract == "Groene Stroom & Gas - Dynamisch":
            contract_type = "dynamisch"

        elif contract == "Groene Stroom & Gas variabel":
            contract_type = "variabel"

        else:
            contract_type = "onbekend"

        offertes.append({
            "leverancier": "Essent",
            "contract": contract,
            "type": contract_type,
            "jaarprijs": offer["beforeDiscountExpectedYearlyAmount"],
            "maandprijs": offer["beforeDiscountExpectedMonthlyAmount"],
            "cashback": offer.get(
                "discountPrice",
                0
            )
        })

    return offertes


if __name__ == "__main__":

    resultaten = essent(
        postcode="7773AN",
        huisnummer=42,
        toevoeging="",
        stroom_verbruik=9000,
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