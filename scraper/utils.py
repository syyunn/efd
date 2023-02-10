import requests
from bs4 import BeautifulSoup
import pandas as pd
from dateutil import parser
from tqdm import tqdm

def get_senators(n_th_congress, insert=False):
    wiki_url = f"https://en.wikipedia.org/wiki/List_of_United_States_senators_in_the_{n_th_congress}th_Congress"
    df = pd.DataFrame({
            'congress': [],
            'first_name': [],
            'last_name': [],
            'party': [],
            'url': [],
           })

    r = requests.get(wiki_url)

    html = r.text
    bs = BeautifulSoup(html, "html.parser")

    tables = bs.find_all('table')
    table = tables[1]
    trs = table.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) > 0:
            name = tds[0].text
            first_name, last_name = name.split(' ')[0].replace('\n', '').split('[')[0], name.split(' ')[-1].replace('\n', '').split('[')[0]
            url = "https://en.wikipedia.org/" + tds[0].find('a')['href']
            party = tds[1].text.replace('\n', '')
            
            # insert into pandas df
            df.loc[len(df.index)] = [n_th_congress, first_name, last_name, party, url]   

            if insert == False:
                continue
            else:
                # insert into postgresql
                from octopus.db import PostgresqlManager
                import psycopg2
                pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
                sql_insert_client_name_and_url = """
                INSERT INTO senator(congress, first_name, last_name, party, url)
                VALUES(%s, %s, %s, %s, %s)
                """

                try:
                    pm.execute_sql(
                        sql=sql_insert_client_name_and_url,
                        parameters=(
                            n_th_congress,
                            first_name,
                            last_name,
                            party,
                            url
                            ),
                        commit=True,
                    )
                except psycopg2.errors.UniqueViolation:
                    pass
                pass


    return df

if __name__ == "__main__":
    for i in range(114, 119): # other than this period, the format of the wikipedia page is different
        df = get_senators(n_th_congress=i, insert=True)
