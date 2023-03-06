from octopus.db import PostgresqlManager
import psycopg2

from dotenv import load_dotenv
# env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')

# pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
pm = PostgresqlManager(dotenv_path="/home/ubuntu/.envlv")

df = pm.execute_sql(fetchall=True, sql=
            f"""
             with arr_a as (
                select ticker, array_agg(distinct asset_name order by asset_name asc) as arr from _sandbox_suyeol.senate_annual_4a
                group by ticker
                )
                , arr_b as (
                select ticker, array_agg(distinct asset_name order by asset_name asc) as arr from _sandbox_suyeol.senate_annual_4b
                group by ticker
                )
                , uni as (
                select * from arr_a
                union
                select * from arr_b
                )
                select  distinct uni.ticker, arr[1] as ticker_name from uni
                	left join _sandbox_suyeol.ticker_naics_url tnu on tnu.ticker = uni.ticker
            	where tnu.naics_url is  null
                """
                )

if __name__ == "__main__":
    sql_insert_client_name_and_url = """
INSERT INTO _sandbox_suyeol.ticker_naics_url (ticker, asset_name, naics_url)
VALUES(%s, %s, %s)
"""

    for ticker, asset_name in df:
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
                break
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



