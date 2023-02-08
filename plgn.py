from polygon import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

ticker = "ARKQ"

# # List Aggregates (Bars)
# bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_="2023-01-09", to="2023-01-10")
# for bar in bars:
#     print(bar)
#     print(datetime.fromtimestamp(bar.timestamp/1000.0))

def get_price_change(ticker, date1, date2, amnt=15000):
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date1, to=date2)

    units = amnt / bars[0].vwap
    return (bars[1].vwap - bars[0].vwap) * units

print(get_price_change("ARKQ", "2021-06-04", "2021-12-16"))