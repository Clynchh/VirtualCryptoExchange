import json
import requests
api_url = "https://api.binance.com/api/v3/klines"

def moving_average(symbol, n):
    limit = n
    params = {
        "symbol" : symbol+"GBP",
        "interval" : "1d",
        "limit" : limit
    }
    response = requests.get(api_url, params=params).json()
    cummulative = 0.0
    for i, item in enumerate(response):
        #print(i, item[4])
        cummulative += float(item[4])

    MA = format(cummulative/params["limit"], ".2f")
    return MA


def day_vol(symbol):
    params = {
        "symbol": symbol+"GBP",
        "interval": "1w",
        "limit": 1
    }
    response = requests.get(api_url, params=params).json()

    quote_volume = 0
    for i, item in enumerate(response):
        quote_volume += float(item[7])
        quote_volume = format(quote_volume, ".2f")
        quote_volume = format(float(quote_volume), ",")
        return quote_volume

def price_change(symbol, time_frame):
    interval = "1" + str(time_frame)
    params = {
        "symbol": symbol+"GBP",
        "interval": interval,
        "limit": 2
    }
    response = requests.get(api_url, params=params).json()
    old_price = float(response[0][4])
    old_price = float(format(old_price, ".2f"))
    new_price = float(response[1][4])
    new_price = float(format(new_price, ".2f"))
    price_change = format(((new_price - old_price)/old_price) * 100, ".2f")
    return price_change
