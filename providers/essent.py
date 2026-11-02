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

    url = (
        "https://www.essent.nl/api/public/cplusactivation/offers/v1"
    )

    params = {
        "flow_id": "L-9f6d1578-7c89-48cc-b9ad-92621cc29d8e",

        "offer_set": "Basis Offerset Essent",
        "customer_segment": "household",

        "postcode": postcode,
        "house_number": huisnummer,
        "house_number_extension": toevoeging,

        "electricity": stroom_verbruik + stroom_verbruik_dal,
        "electricity_low": stroom_verbruik_dal,

        "electricity_return": teruglevering + teruglevering_dal,

        "gas": gas,

        "duration_filter": "all_durations",

        "electricity_connection_ean": "871694840007274450",
        "electricity_captar_code": "8742010102115",
        "electricity_grid_ean": "8716948000003",

        "gas_connection_ean": "871691600001581632",
        "gas_captar_code": "8742090202118",
        "gas_net_area_ean": "871718518003003228"
    }

    response = requests.get(
        url,
        params=params
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
                "jaarprijs": offer["expectedYearlyAmount"],
                "maandprijs": offer["expectedMonthlyAmount"]
           })

    return offertes


if __name__ == "__main__":

    resultaten = essent(
        postcode="7773AN",
        huisnummer=42,
        toevoeging="",
        stroom_verbruik=5000,
        stroom_verbruik_dal=4000,
        teruglevering=0,
        teruglevering_dal=0,
        gas=550,
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
            "12 x maandprijs:",
            offerte["maandprijs"] * 12
        )

        print("-" * 40)