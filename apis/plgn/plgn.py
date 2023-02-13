from polygon import RESTClient
from dotenv import load_dotenv
import os

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

def get_price_change(ticker, date1, date2, amnt=15000):
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date1, to=date2)

    units = amnt / bars[0].vwap
    return (bars[1].vwap - bars[0].vwap) * units

def get_price(ticker, date):
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date, to=date)
    return bars[0].vwap

if __name__ == "__main__":
    print(get_price("SPY", "2021-06-04"))      
    print(get_price_change("SPY", "2021-06-04", "2021-12-16"))
pass