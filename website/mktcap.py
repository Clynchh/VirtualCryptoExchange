import requests
import json

from requests.api import get

def get_mkt_cap():
    circulation_url = "https://www.binance.com/exchange-api/v2/public/asset-service/product/get-products"
    price_url = "https://api.binance.com/api/v3/avgPrice"

    circulation_response = requests.get(circulation_url).json()

    gbp_response = []
    mkt_cap_dict = {}

    for i, item in enumerate(circulation_response["data"]):
        #in this response:
        #"q" is the quote currency
        #"b" is the base currency
        #"cs" is the amount of base currency in circulation
        if circulation_response["data"][i]["q"] == "GBP":
            gbp_response.append(circulation_response["data"][i])

    for i, item in enumerate(gbp_response):
        base = gbp_response[i]["b"]
        in_circulation = float(gbp_response[i]["cs"])
        params = {
            "symbol": (base+"GBP")
        }
        price_response = requests.get(price_url, params=params).json()
        price = float(list(price_response.values())[1])
        mkt_cap_dict[base] = price*in_circulation


    sorted_mkt_cap = {key: val for key, val in sorted(mkt_cap_dict.items(), key=lambda x: x[1], reverse=True)}

    for key, val in sorted_mkt_cap.items():
        sorted_mkt_cap[key] = format(val, ".2f")

    for key, val in sorted_mkt_cap.items():
        sorted_mkt_cap[key] = format(float(val), ",")


    return sorted_mkt_cap



#sorted_mkt_cap is a dict containing the market cap (in gbp) descending of the 
#crypto/gbp pairs listed on binance, with their according symbol name





