import requests

def vattenfall(
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

    offertes = []

    summary_url = (
        "https://api.vattenfall.nl/"
        "vattenfallnlsalesflowproductselectorprd/"
        "api/v1/ProductsSelector/summary"
    )

    summary_headers = {
        "Ocp-Apim-Subscription-Key":
            "b4f5e85f588d482799203643fa2f23bf",
        "Accept": "application/json"
    }

    summary_params = {
        "CampaignName": "VattenfallNL Product Selector",
        "IncludeHeat": "false"
    }

    summary_response = requests.get(
        summary_url,
        params=summary_params,
        headers=summary_headers
    )

    summary_response.raise_for_status()

    summary_data = summary_response.json()

    offer_url = (
        "https://api.vattenfall.nl/"
        "api/aompublicapi/salesandcontracting/v1/offer"
    )

    offer_headers = {
        "Ocp-Apim-Subscription-Key":
            "de6788e52a77456286dbce7ea9439c0b",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    if slimme_meter:

        consumption_blocks = [
            {
                "number": 1,
                "volume": stroom_verbruik
            },
            {
                "number": 2,
                "volume": stroom_verbruik_dal
            }
        ]

        backdelivery_blocks = [
            {
                "number": 1,
                "volume": teruglevering
            },
            {
                "number": 2,
                "volume": teruglevering_dal
            }
        ]

    else:

        consumption_blocks = [
            {
                "number": 1,
                "volume": (
                    stroom_verbruik +
                    stroom_verbruik_dal
                )
            }
        ]

        backdelivery_blocks = [
            {
                "number": 1,
                "volume": (
                    teruglevering +
                    teruglevering_dal
                )
            }
        ]

    for proposition in summary_data["propositions"]:

        if not (
            proposition["hasElectricity"]
            and proposition["hasGas"]
        ):
            continue

        payload = {
            "addOnCode": "None",
            "campaignName": "VattenfallNL Product Selector",
            "channel": "online",

            "postalCode": postcode,
            "houseNumber": int(huisnummer),
            "houseNumberAddition": toevoeging,

            "isResidential": True,

            "propositionId": proposition["propositionId"],

            "electricity": {
                "profile": "T3",
                "gridCapacity": "3x25",

                "consumption": {
                    "blocks": consumption_blocks
                },

                "backDelivery": {
                    "blocks": backdelivery_blocks
                }
            },

            "gas": {
                "profile": "G1A",
                "gridCapacity": "G6",
                "consumption": gas
            },

            "preferredStartDate": None
        }

        offer_response = requests.post(
            offer_url,
            json=payload,
            headers=offer_headers
        )

        if offer_response.status_code != 200:
            continue

        offer_data = offer_response.json()

        try:

            jaarprijs = (
                offer_data["includingVat"]
                ["specs"]
                ["totalYearlyCost"]
            )

            maandprijs = (
                offer_data["includingVat"]
                ["specs"]
                ["termAmount"]
            )

            contract = proposition["name"]
            proposition_id = proposition["propositionId"]

            if contract == "FlexPrijsStroom + FlexPrijsGas":
                contract_type = "dynamisch"

            elif contract == "Groen uit Nederland + Gas":
                contract_type = "variabel"

            elif contract == "TijdPrijs Trend Vast + VastePrijsGas":
                contract_type = "1_jaar"

            elif contract == "Groen uit Nederland Vast + VastePrijsGas":

                if "CM-36" in proposition_id:
                    contract_type = "3_jaar"

                elif "CM-12" in proposition_id:
                    contract_type = "1_jaar"

                else:
                    contract_type = "onbekend"

            else:
                contract_type = "onbekend"

            offertes.append({
                "leverancier": "Vattenfall",
                "contract": contract,
                "type": contract_type,
                "jaarprijs": jaarprijs,
                "maandprijs": maandprijs
            })

        except KeyError:
            pass

    return offertes


if __name__ == "__main__":

    resultaten = vattenfall(
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
            f"{offerte['contract']}"
            f" - €{offerte['jaarprijs']:.2f}/jaar"
            f" - €{offerte['maandprijs']:.2f}/maand"
        )