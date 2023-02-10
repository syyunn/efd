from polygon import RESTClient
import polygon
from dotenv import load_dotenv
import os
import pandas as pd

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

def get_price_change(ticker, date1, date2, amnt=15000):
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date1, to=date2)

    units = amnt / bars[0].vwap
    return (bars[1].vwap - bars[0].vwap) * units

print(get_price_change("BND", "2021-06-04", "2021-12-16"))

pass