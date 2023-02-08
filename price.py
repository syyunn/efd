from polygon import RESTClient
import polygon
from dotenv import load_dotenv
import os
import pandas as pd

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')
api_key = os.getenv("POLYGON_APIKEY")
print(api_key)
client = RESTClient(api_key=api_key)

from octopus.db import PostgresqlManager
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
df = pm.execute_sql(fetchall=True, sql=
                # """
                # select distinct ticker, trans_date from senate_annual_4b sb
                #    inner join senate_annual sa on sa.report_type_url  = sb.report_url
                # """
                """
                select distinct sb.ticker, trans_date from senate_annual_4b sb
                   inner join senate_annual sa on sa.report_type_url  = sb.report_url
				   left join price p on (p.ticker = sb.ticker and trans_date =p."date")
                where vwap is null and sb.ticker is not null
                """
                )
for ticker, date in df: # name and ticker pairs
    # get price
    try:
        bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=date, to=date)
        vwap = bars[0].vwap

        sql_insert = """
        INSERT INTO price(ticker, date, vwap)
        VALUES(%s, %s, %s)
        """
        pm.execute_sql(
                    sql=sql_insert,
                    parameters=(
                        ticker,
                        date,
                        vwap,
                    ),
                    commit=True,
                )
    except polygon.exceptions.NoResultsError as e:
        pass
    