from octopus.db import PostgresqlManager
import psycopg2
from tqdm import tqdm
from dotenv import load_dotenv
# env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", type=int, default=100)
parser.add_argument("--n_th_instance", type=int, default=1)
args = parser.parse_args()

offset = args.batch_size * args.n_th_instance


pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
# pm = PostgresqlManager(dotenv_path="/home/ubuntu/.envlv")

df = pm.execute_sql(fetchall=True, sql=
            f"""
WITH alr AS (
  SELECT DISTINCT ticker FROM _sandbox_suyeol.ticker_naics_url
  WHERE naics_url IS NOT NULL or naics_url = 'Not found'
), agg_hft AS (
  SELECT hft.ticker, ARRAY_AGG(hft.asset_name) AS asset_names
  FROM "_sandbox_suyeol".house_fd_transactions hft 
  WHERE hft.ticker NOT IN (SELECT * FROM alr)
  GROUP BY hft.ticker
)
SELECT agg_hft.ticker, MIN(asset_name) AS asset_name
FROM agg_hft, UNNEST(agg_hft.asset_names) AS asset_name
GROUP BY agg_hft.ticker
limit {args.batch_size} offset {offset};
                """
                )

if __name__ == "__main__":
    sql_insert_client_name_and_url = """
INSERT INTO _sandbox_suyeol.ticker_naics_url (ticker, asset_name, naics_url)
VALUES(%s, %s, %s)
"""

    for ticker, asset_name in tqdm(df):
        print(ticker, asset_name)
        url = None
        asset_name_comps = asset_name.replace("\n", "").replace("\t", "").split(" ")
        asset_name_partial = " ".join(asset_name_comps[:2])
        query = ticker.replace("\n", "").replace("\t", "").replace(" ", "") + " " + asset_name_partial + " " + "NAICS"
        # query = ticker.replace("\n", "").replace("\t", "").replace(" ", "") + " " + "naics association"
        from octopus.ggl import GoogleManager
        gm = GoogleManager(use_vpn_if_needed=False)
        bs = gm.search_google(text=query)
        a_comps = bs.find_all("a")
        for a in a_comps:
            # check whether a has href
            if "href" not in a.attrs:
                continue # check next a comp
            # check whether href is a valid url
            url_cand = a.attrs["href"]
            if "https://www.naics.com/company-profile-page/" in url_cand:
                url = url_cand
                print(url)
                try:
                    pm.execute_sql(
                        sql=sql_insert_client_name_and_url,
                        parameters=(
                            ticker,
                            asset_name,
                            url
                        ),
                        commit=True,
                    )
                except psycopg2.errors.UniqueViolation as e:
                    print(e)
                    pass
                break # this point is important to make it faster
        if url is None:
            url = "Not found"
            print(url)
            try:
                pm.execute_sql(
                    sql=sql_insert_client_name_and_url,
                    parameters=(
                        ticker,
                        asset_name,
                        url
                    ),
                    commit=True,
                )
            except psycopg2.errors.UniqueViolation as e:
                print(e)



