from requests import get
import json

api_url = "https://api.binance.com/api/v3/klines"


params = {
        "symbol" : "BTCUSDT",
        "interval" : "1d",
        "limit" : 1
    }


def moving_average():
    while True:
        limit = int(round(float(input("Enter how many days MA: "))))
        params['limit'] = limit
        print(params['limit'])
        if 0<limit<1000:
            break
        print("Enter an integer between 1 and 999 (inclusive)")
    response = get(api_url, params=params).json()
    cummulative = 0.0
    for i, item in enumerate(response):
        #print(i, item[4])
        cummulative += float(item[4])

    MA = cummulative/params["limit"]
    print(f'{str(params["limit"])} day MA: {MA}')

    more_data()

def day_vol():
    response = get(api_url, params=params).json()

    QAvolume = 0.0
    baseVolume = 0.0
    for i, item in enumerate(response):
        QAvolume += float(item[7])
        baseVolume += float(item[5])

    print(f"24h trading volume: {QAvolume} {quote}")
    print(f"24h trading volume: {baseVolume} {base}")
    
    more_data()


def general_data():
    params["interval"] = input("Enter a custom time interval: (1m, 1h, 1d, 1w, 1M)")
    params["limit"] = int(input("Enter how many intervals: "))
    
    response = get(api_url, params=params).json()

    for i, response in enumerate(response):
        print(f"Data for interval {i}:")
        print(f"\t Open price: {response[1]}")
        print(f"\t Close price: {response[4]}")
        print(f"\t High price: {response[2]}")
        print(f"\t Low price: {response[3]}")
        if float(response[4]) < float(response[1]):
            movement = "Decrease"
        else:
            movement = "Increase"
        print(f"\t Price {movement} of: {(abs(float(response[4]) - float(response[1])))}")
    
    more_data()

def menu():
    global base, quote
    base = input("Enter the base currency (crypto): ").upper()
    quote = input("Enter the quote currency (stable/fiat)").upper()
    tradingPair = base + quote
    params["symbol"] = tradingPair
    print("Enter what metadata you would like: ")
    print("1. 24-hour trading volume")
    print("2. General ")
    print("3. N-day Moving Average")
    choice = int(input())
    while True:
        if choice == 1:
            day_vol()
            break
        elif choice == 2:
            general_data()
            break
        elif choice == 3:
            moving_average()
            break
        else:
            print("Enter a valid choice")
            choice = int(input())

def more_data():
    more = input("Do you want more data? (y/n)")
    while more.upper() not in ["Y", "N"]:
        print("Input a valid response: ")
        more = input("Do you want more data? (y/n)")
    if more.upper() == "Y":
        menu()

if __name__ == "__main__":
    menu()