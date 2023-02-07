from polygon import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

ticker = "NFRA"

# List Aggregates (Bars)
bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_="2023-01-09", to="2023-01-10")
for bar in bars:
    print(bar)
    print(datetime.fromtimestamp(bar.timestamp/1000.0))