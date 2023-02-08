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

# print(get_price_change("BND", "2021-06-04", "2021-12-16"))

result = pd.DataFrame({
        'first_name': [],
        'last_name': [],
        'ticker': [],
        'cash': []
        })

from octopus.db import PostgresqlManager
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
df = pm.execute_sql(fetchall=True, sql=
                """
                select distinct first_name, last_name, ticker from senate_annual_4b sb
                   inner join senate_annual sa on sa.report_type_url  = sb.report_url
                   order by first_name, last_name
                """
                )
for row in df: # name and ticker pairs
    backslash_char = '\''
    trnscs = pm.execute_sql(fetchall=True, sql=
                f"""
                select distinct first_name, last_name, ticker, trans_type, trans_date, amount_min from senate_annual_4b sb 
                inner join senate_annual sa on sa.report_type_url  = sb.report_url 
                where first_name = {backslash_char}{row[0]}{backslash_char} and last_name = {backslash_char}{row[1]}{backslash_char} and ticker = {backslash_char}{row[2]}{backslash_char}
                order by trans_date asc
                """
                )
    # check only the cases which starts as purchase and ends as sell
    if len(trnscs) >1: # for the case of ticker is None
        # if "Purchase" in trnscs[0][3] and "Sale (Full)" in trnscs[-1][3]:
        # if "Purchase" in trnscs[0][3] and "Sale (Full)" in trnscs[-1][3]:
        #     print(row[0], row[1], row[2])
        cash = 0
        purchase_units = []

        ticker = trnscs[0][2]
        date = trnscs[0][4]

        try:
            bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date, to=date)
        except polygon.exceptions.NoResultsError as e: # in case ticker doesn't exist
            print("Ticker doesn't exist: ", ticker)
            continue

        for trnsc in trnscs: # all transactions of a name and ticker pair
            ticker = trnsc[2]
            ps = trnsc[3] # purchase or sale
            date = trnsc[4]
            amount = trnsc[5]
            bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date, to=date)

            current_holdings = sum(purchase_units)

            if "Purchase" in ps:
                units = amount / bars[0].vwap # this is the minimum amount of units purchased
                purchase_units.append(units)
                cash -= amount
            elif "Sale (Full)" in ps:
                units = amount / bars[0].vwap # minimum units estimated as being sold.
                if units > current_holdings: # this means we're missing previous data about purchasement
                    print("break! insufficient holdings to sell all", row[0], row[1], row[2])
                    break
                else:
                    purchase_units.append(-current_holdings) # sell all of the holdings
                    cash_out = current_holdings * bars[0].vwap
                    cash += cash_out      
            elif "Sale (Partial)" in ps:
                units = amount / bars[0].vwap # minimum amount estimated as being sold.
                if units > current_holdings: # this means we're missing previous data because one can't sell more than what they have
                    print("break! insufficient holdings to sell", row[0], row[1], row[2])
                    break
                else:
                    purchase_units.append(-units)
                    cash_out = units * bars[0].vwap
                    cash += cash_out
            pass
        result.loc[len(result.index)] = [row[0], row[1], row[2], cash]  
        print(row[0], row[1], row[2], cash)


    pass
pass
