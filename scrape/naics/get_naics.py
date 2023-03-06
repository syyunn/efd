from octopus.db import PostgresqlManager
import psycopg2
# pm1 = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
# df = pm1.execute_sql(fetchall=True, sql=
#             f"""
#             with arr_a as (
#                 select ticker, array_agg(distinct asset_name order by asset_name asc) as arr from senate_annual_4a
#                 group by ticker
#                 )
#                 , arr_b as (
#                 select ticker, array_agg(distinct asset_name order by asset_name asc) as arr from senate_annual_4b
#                 group by ticker
#                 )
#                 , uni as (
#                 select * from arr_a
#                 union
#                 select * from arr_b
#                 )
#                 select distinct ticker, arr[1] from uni
#                 -- order by ticker asc
#             """
#                 )

# # pickle df
# import pickle
# with open("df.pickle", "wb") as f:
#     pickle.dump(df, f)

# load pickle
import pickle
with open("df.pickle", "rb") as f:
    df = pickle.load(f)

if __name__ == "__main__":
    pm2 = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")

    for ticker, asset_name in df:
        url = None
        print(asset_name)
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
                continue
            # check whether href is a valid url
            url_cand = a.attrs["href"]
            if "https://www.naics.com/company-profile-page/" in url_cand:
                url = url_cand
                sql_insert_client_name_and_url = """
                INSERT INTO _sandbox_suyeol.ticker_naics_url (ticker, asset_name, naics_url)
                VALUES(%s, %s, %s)
                """
                try:
                    pm2.execute_sql(
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
            try:
                pm2.execute_sql(
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



