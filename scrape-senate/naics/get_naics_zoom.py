from octopus.db import PostgresqlManager
import psycopg2
from tqdm import tqdm
from dotenv import load_dotenv
# env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", type=int, default=100)
parser.add_argument("--n_th_instance", type=int, default=0)
args = parser.parse_args()

offset = args.batch_size * args.n_th_instance
# load_dotenv("/Users/syyun/Dropbox (MIT)/efd/.envlv", override=True)
# pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
pm = PostgresqlManager(dotenv_path="/home/ubuntu/.envlv")

df = pm.execute_sql(fetchall=True, sql=
            f"""
select distinct tnu.ticker, tnu.asset_name  from "_sandbox_suyeol".ticker_naics_url tnu 
inner join "_sandbox_suyeol".comp c on c.ticker = tnu.ticker 
left join "_sandbox_suyeol".ticker_naics_zoom tnz on tnz.ticker  = tnu.ticker 
where (naics_url is null or naics_url ='Not found') and tnz.naics is null and c.is_company  is True
order by ticker asc
limit {args.batch_size} offset {offset};
                """
                )

if __name__ == "__main__":
    sql_insert_client_name_and_url = """
INSERT INTO _sandbox_suyeol.ticker_naics_zoom(ticker, asset_name, naics)
VALUES(%s, %s, %s)
"""

    for ticker, asset_name in tqdm(df):
        print(ticker, asset_name)
        url = None
        asset_name_comps = asset_name.replace("\n", "").replace("\t", "").split(" ")
        asset_name_partial = " ".join(asset_name_comps[:2])
        query = ticker.replace("\n", "").replace("\t", "").replace(" ", "").strip() + " " + asset_name_partial + " " + "NAICS Code:" + " " + "ZoomInfo"
        print(query)
        # query = ticker.replace("\n", "").replace("\t", "").replace(" ", "") + " " + "naics association"
        from octopus.ggl import GoogleManager
        gm = GoogleManager(use_vpn_if_needed=False)
        bs = gm.search_google(text=query)
        a_comps = bs.find_all("span", class_="hgKElc")
        
        if len(a_comps) > 0:
            t = a_comps[0].text
            import re

            match = re.search(r"NAICS:\s*(\d+,\d+)", t)
            if match:
                code = match.group(1).replace(",", "")
                print(f"NAICS code: {code}")
            else:
                print("NAICS code not found")
            pass

            try:
                pm.execute_sql(
                    sql=sql_insert_client_name_and_url,
                    parameters=(
                        ticker,
                        asset_name,
                        code
                    ),
                    commit=True,
                )
                print("added")
            except psycopg2.errors.UniqueViolation as e:
                print(e)

        else:
            ems = bs.find_all("em")
            if len(ems) > 0:
                try:
                    code = str(int(ems[0].text.replace(',', '')))
                    try:
                        pm.execute_sql(
                            sql=sql_insert_client_name_and_url,
                            parameters=(
                                ticker,
                                asset_name,
                                code
                            ),
                            commit=True,
                        )
                        print("added")
                    except psycopg2.errors.UniqueViolation as e:
                        print(e)
                except:
                    continue

