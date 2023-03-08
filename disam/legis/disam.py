import json

import pandas as pd
import psycopg2
import argparse

from octopus.ggl import GoogleManager
from octopus.basic import BasicManager
from octopus.db import PostgresqlManager


parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", type=int, default=100)
parser.add_argument("--n_th_instance", type=int, default=None)
args = parser.parse_args()

sql_insert_client_name_and_url = """
INSERT INTO disambiguation.clients_by_requests(client_name, url)
VALUES(%s, %s)
"""

batch_size = args.batch_size
n_th_instance = args.n_th_instance
offset = batch_size * n_th_instance

sql_select_legislator_names_to_request = f"""
select distinct c.client_name from lobbyview.relational___lda.clientships c 
left join disambiguation.clients_by_requests cbr on cbr.client_name =  c.client_name 
where cbr.url is NULL
order by c.client_name asc
limit {batch_size} offset {offset}
"""

print(sql_select_client_names_to_request)


def parse_href(href):
    splits = href.split("/")
    return splits[0] + "//" + splits[2]


def _add_https_prefix(url):
    if 'http' in url:
        return url
    else:
        return "https://" + url


def _manual_postfix(href, first_href):
    bm = BasicManager(use_vpn_if_needed=True)
    if href == "https://www.dnb.com":
        bs = bm.get(first_href)
        a = bs.find("a", string="Website")
        return a["href"]

    elif href == "https://www.bloomberg.com":
        bs = bm.get(first_href)
        scripts = bs.find_all("script")
        meta = json.loads(scripts[1].string)
        url = meta["url"]
        return url

    else:
        return href
    pass


def disambiguate(name):
    try:
        gm = GoogleManager(use_vpn_if_needed=True)
        bs = gm.search_google(name)
        div_id_search = bs.find("div", {"id": "search"})
        first_href = div_id_search.find("a")
        first_href = first_href["href"]
        # href = parse_href(first_href)
        href = first_href
        # href = _manual_postfix(href, first_href)
        href = _add_https_prefix(href)

        pm = PostgresqlManager()
        pm.execute_sql(sql=sql_insert_client_name_and_url, parameters=(name, href),  commit=True)
        print(name)
        print(href)

        return href
    except (TypeError, IndexError, psycopg2.errors.UniqueViolation, AttributeError, psycopg2.OperationalError) as e:
        # TypeError for NoneType
        # Index Error for
        print(e)
        return None


if __name__ == "__main__":
    # df = pd.read_csv("./samsung_regis_client_names.csv")
    # df = pd.read_csv("./all_regis_client_names.csv")
    pm = PostgresqlManager()
    data = pm.execute_sql(sql=sql_select_client_names_to_request, fetchall=True, commit=False)
    df = pm.convert_fetchall_to_pd(data)
    print(df)
    df.rename(columns={0: 'client_name'}, inplace=True)
    # df = pd.read_csv("./all_distinct_client_names.csv")
    # df = df.sample(frac=1).reset_index(drop=True)
    df["url"] = df.apply(lambda x: disambiguate(x.client_name), axis=1)
    pass