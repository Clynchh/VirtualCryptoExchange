import requests
import json
from math import sqrt

def format_2dp(n):
    n_to_2dp = format(n, ".2f")
    n_with_commas = format(float(n_to_2dp), ",")
    return n_with_commas


def generate_report(portfolio_dict):
  report = []
  portfolio_value = 0
  future_portfolio = 0
  candlestick_url = "https://api.binance.com/api/v3/klines"
  price_url = "https://api.binance.com/api/v3/avgPrice"
  keys = portfolio_dict.keys()
  values = list(portfolio_dict.values())
  for i, key in enumerate(keys):
    if values[i] != 0:
      candlestick_params = {
        "interval": "1d",
        "limit": 500,
        "symbol": key+"GBP"
      }

      response = requests.get(candlestick_url, params=candlestick_params).json()
      MA_cummulative = 0
      sample_size = len(response)
      for j, item in enumerate(response):
        MA_cummulative += float(item[4])

      MA = MA_cummulative/sample_size

      #print(f"{sample_size}-day moving avg. for {key} is £{format_2dp(MA)}")

      SD_cummulative = 0
      for k, item in enumerate(response):
        mean_squared = MA**2
        x_squared = (float(item[4]))**2
        SD_cummulative += x_squared

      SD = sqrt((SD_cummulative/sample_size)-mean_squared)
      #print(f"{sample_size}-day standard deviation for {key} is £{format_2dp(SD)}")
      
      price_url = "https://api.binance.com/api/v3/avgPrice"
      price_params = {
        "symbol": key+"GBP"
      }
      price_response = requests.get(price_url, price_params).json()
      price = float(price_response["price"])
      #print(f"The price of {key} is {price}")

      difference = price - MA
      #print(f"The difference between {key}'s price and moving avg. is {format_2dp(difference)}")

      sd_proportion = difference/SD
      report.append(f"{key} is currently {format_2dp(sd_proportion)} standard deviations away from the moving average")

      if sd_proportion > 0:
        if sd_proportion > 1:
          report.append(f"{key} is extremely overvalued. It is recommended that you sell your position in {key}")
        elif sd_proportion > 0.5:
          report.append(f"{key} is overvalued. You may want to consider selling some/all of your position in {key}")
        else:
          report.append(f"{key} is insignificantly overvalued. It is recommended that you hold on to your position in {key} but be wary of market movements")
      elif sd_proportion < 0:
        if sd_proportion < -1:
          report.append(f"{key} is extremely undervalued. It is recommended that you increase your position in {key}")
        elif sd_proportion < -0.5:
          report.append(f"{key} is undervalued. You may want to consider increasing your position in {key} slightly")
        else:
          report.append(f"{key} is insignificantly undervalued. It is recommended that you hold on to your position in {key} but be wary of market movements")
      else:
        report.append(f"{key} is perfectly values accoring to the market. It is recommended that you do nothing to alter your position.")

      
      asset_value = portfolio_dict[key] * price
      report.append(f"The total value of your {key} is £{format_2dp(asset_value)}")
      portfolio_value += asset_value
      future_value = asset_value * (1-(sd_proportion/10))
      #the future price of an asset tends to move opposite to the direction it is from the mean (according to mean reversion)
      report.append(f"According to the mean reversion model, the predicted value of your {key} is {format_2dp(future_value)}")

      future_portfolio += future_value

      if asset_value != 0:
          asset_price_change = ((future_value - asset_value)/asset_value)*100
      else:
          asset_price_change = 0


      if future_value < price:
        report.append(f"Your {key} is predicted to decrease by {format_2dp(asset_price_change)}%\n\n")
      elif future_value > price:
        report.append(f"Your {key} is predicted to increase by {format_2dp(asset_price_change)}%\n\n")
      else:
        report.append(f"The value of your {key} is not expected to change in the near future\n\n")

  #print(f"The total value of your portfolio is £{format_2dp(portfolio_value + user_1GBP_balance)}")
  report.append(f"According to the mean reversion model, the predicted value of your crypto assets is {format_2dp(future_portfolio)}")
  if portfolio_value != 0:
    portfolio_change = ((future_portfolio-portfolio_value)/portfolio_value)*100
  else:
    portfolio_change = 0

  if future_portfolio < portfolio_value:
    report.append(f"This is a predicted decrease in value of {format_2dp(portfolio_change)}%")
  elif future_portfolio > portfolio_value:
    report.append(f"This is a predicted increase in value of {format_2dp(portfolio_change)}%")
  else:
    report.append(f"The value of your portfolio is not expected to change in the near future")
  
  return report

