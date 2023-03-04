from octopus.db import PostgresqlManager
import psycopg2
import argparse
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", type=int, default=100)
parser.add_argument("--n_th_instance", type=int, default=None)
args = parser.parse_args()

offset = args.batch_size * args.n_th_instance

load_dotenv(".envlv", override=True)
pm = PostgresqlManager(dotenv_path=".envlv")

df = pm.execute_sql(fetchall=True, sql=
            f"""
            select distinct client_name from _sandbox_suyeol.client_ticker
            where ticker is null
            order by client_name asc
            limit {args.batch_size} offset {args.offset}
            """
                )

update_sql = f"""
            UPDATE _sandbox_suyeol.client_ticker
            SET exchange = %s, ticker = %s
            WHERE client_name = %s;
        """

for item in df:
    client = item[0]
    print(client)
    query = client + " " + "ticker"
    from octopus.ggl import GoogleManager
    gm = GoogleManager(use_vpn_if_needed=False)
    bs = gm.search_google(text=query)

    ticker_content = bs.find("div", class_="wx62f PZPZlf x7XAkb")
   
    if ticker_content is None:
        print("No ticker found")
        try:
            pm.execute_sql(
                sql=update_sql,
                parameters=(
                    "Not found",
                    "Not found",
                    client
                ),
                commit=True,
            )
        except psycopg2.errors.UniqueViolation as e:
            print(e)
    else:
        ticker_content = ticker_content.textc
        exchange = ticker_content.split(":")[0].strip()
        ticker = ticker_content.split(":")[1].strip()
        print(exchange, ticker)

        try:
            pm.execute_sql(
                sql=update_sql,
                parameters=(
                    exchange,
                    ticker,
                    client
                ),
                commit=True,
            )
        except psycopg2.errors.UniqueViolation as e:
            print(e)
            pass
