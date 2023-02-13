import pandas as pd
from tqdm import tqdm

import polygon
from polygon import RESTClient
from dotenv import load_dotenv
import os

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

def get_price(ticker, date):
    bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date, to=date)
    return bars[0].vwap

### DO NOT DELETE THIS COMMENT BLOCK ###

# congress = 118

# from octopus.db import PostgresqlManager
# pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
# df = pm.execute_sql(fetchall=True, sql=
#                 f"""
#                 with union4ab as (
#                     select * from senate_annual_4a saa 
#                     union
#                     select * from senate_annual_4b sab 
#                 )
#                 select distinct sa.first_name, sa.last_name, u.ticker from union4ab u
#                     inner join senate_annual sa on sa.report_type_url  = u.report_url
#                     inner join senator s on s.url = sa.url
#                     -- where s.congress = {congress}
#                 order by first_name, last_name
#                 """
#                 )

# chains = []

# for row in tqdm(df): # name and ticker pairs
#     backslash_char = '\''
#     trnscs = pm.execute_sql(fetchall=True, sql=
#                 f"""
#                 with union4ab as (
#                     select * from senate_annual_4a saa 
#                     union
#                     select * from senate_annual_4b sab 
#                 )
#                 select distinct first_name, last_name, p.ticker, trans_type, trans_date, amount_min, vwap, amount_max from union4ab u
#                     inner join senate_annual sa on sa.report_type_url  = u.report_url 
#                     inner join price p on (p.ticker=u.ticker and p.date=u.trans_date)
#                 where first_name = {backslash_char}{row[0]}{backslash_char} and last_name = {backslash_char}{row[1]}{backslash_char} and u.ticker = {backslash_char}{row[2]}{backslash_char} and vwap is not null
#                 order by trans_date asc
#                 """
#                 )
#     # check whether purchase and sale both in the transactions
#     pass
#     trnsc_types = [trnsc[3] for trnsc in trnscs]
#     trnsc_types_string = ''.join(['p' if trnsc_type == 'Purchase' else 's' for trnsc_type in trnsc_types])

#     if 'p' in trnsc_types_string and 's' in trnsc_types_string:
#         m = True
#         pad = 0
#         while m:
#             import re 
#             m  = re.search(r"p+s+", trnsc_types_string)
#             if (m is not None) and len(trnsc_types_string) >= 2:
#                 # chains.append(trnsc_types_string[m.start():m.end()])
#                 chains.append(trnscs[m.start()+pad:m.end()+pad])
#                 trnsc_types_string = trnsc_types_string[m.end():]
#                 pad += m.end() 
#                 pass
#             else:
#                 break
#             pass
#     else:
#         continue

import pickle
# with open("./anlys/pppsss/chains.pickle", "wb") as f:
#     pickle.dump(chains, f)

with open("./anlys/pppsss/chains.pickle", "rb") as f:
    chains = pickle.load(f)

normalized_avg_margins =[]   
normalized_avg_margins_spy =[]

for chain in tqdm(chains):
    puchase_prices =[]
    sale_prices = []

    purchase_spy_prices = []
    sale_spy_prices = []

    for trnsc in chain:
        date = trnsc[4]
        try:
            spy = get_price('SPY', date)
        except polygon.exceptions.NoResultsError as e:
            print('SPY', date, e)
        
        if trnsc[3] == 'Purchase':
            puchase_prices.append(trnsc[6])
            purchase_spy_prices.append(spy)
        else:
            sale_prices.append(trnsc[6])
            sale_spy_prices.append(spy)
    avg_purchase_price = sum(puchase_prices)/len(puchase_prices)
    avg_sale_price = sum(sale_prices)/len(sale_prices)
    
    avg_purchase_spy_price = sum(purchase_spy_prices)/len(purchase_spy_prices)
    avg_sale_spy_price = sum(sale_spy_prices)/len(sale_spy_prices)

    normalized_avg_margins.append((avg_sale_price - avg_purchase_price)*100/avg_purchase_price)
    normalized_avg_margins_spy.append((avg_sale_spy_price - avg_purchase_spy_price)*100/avg_purchase_spy_price)
    pass

with open("./anlys/pppsss/nmavg_margins.pickle", "wb") as f:
    pickle.dump(normalized_avg_margins, f)
with open("./anlys/pppsss/nmavg_margins_spy.pickle", "wb") as f:
    pickle.dump(normalized_avg_margins_spy, f)

# whether beats the market by manual threshold
threshold = 5
print(len([margin for margin in normalized_avg_margins if margin > threshold]))
print(len([margin for margin in normalized_avg_margins if margin < threshold]))
print(len([margin for margin in normalized_avg_margins if margin == threshold]))

# whether beats the market over passive index fund
print(len([margin-spy for margin, spy in zip(normalized_avg_margins, normalized_avg_margins_spy) if margin > spy]))
print(len([margin-spy for margin, spy in zip(normalized_avg_margins, normalized_avg_margins_spy) if margin < spy]))
print(len([margin-spy for margin, spy in zip(normalized_avg_margins, normalized_avg_margins_spy) if margin == spy]))

# how strongly they've beaten the market


import matplotlib.pyplot as plt

# Define the data for the plot
x = normalized_avg_margins
y = [0 for _ in normalized_avg_margins]

# Create the plot
plt.scatter(x, y)

# Add labels to the axes
plt.xlabel('X axis')
plt.ylabel('Y axis')

# Show the plot
plt.savefig("./anlys/pppsss/normalized_avg_margins.png")
# plt.show()
# plt.close()
pass

import numpy as np

# Define a sample list
# Find the index of the top 5 largest elements
top_5_indices = np.argsort(normalized_avg_margins)[-5:]

# Print the index of the top 5 largest elements
print("The index of the top 5 largest elements:", top_5_indices)
print(np.array(normalized_avg_margins)[top_5_indices])
print(np.array(chains)[top_5_indices[-5]])

# draw with pppssss w/ graph
# filter to compare with that periods' S&P 500
