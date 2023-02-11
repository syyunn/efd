from bs4 import BeautifulSoup
import pandas as pd
from dateutil import parser
from tqdm import tqdm


def parse_annual(url, insert=True):
    import selenium
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless") # only in case you wanna run it in headless
    # from lobbyview.db import PostgresqlManager

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), options=options
    )

    # get base url and click on agreement
    base_url = "https://efdsearch.senate.gov/search/"
    driver.get(base_url)
    driver.find_element(By.ID, "agree_statement").click() 

    # go to actual target url which contains the annual report
    driver.get(url)
    html = driver.page_source

    bs = BeautifulSoup(html, "html.parser")
    sections = bs.find_all("section")
    p4b = sections[4]
    tbody = p4b.find("tbody") # this locates part4b transactions
    if tbody:
        trs = tbody.find_all("tr")
    else:
        return None

    df = pd.DataFrame({
        'report_url': [],
        'owner': [],
        'ticker': [],
        'ticker_url': [],
        'asset_name': [],
        'trans_type': [],
        'trans_date': [],
        'amount_min': [],
        'amount_max': [],
        'comment': [],
        })

    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) > 0:
            owner = tds[2].text
            if tds[3].find("a") != None:
                ticker = tds[3].find("a").text
                if tds[3].find("a")["href"] != None:
                    ticker_url = tds[3].find("a")["href"]
                else:
                    ticker_url = None
            else:
                ticker = None
                ticker_url = None

            asset_name = tds[4].text.replace('\n', '').strip()
            trans_type = tds[5].text
            trans_date = parser.parse(tds[6].text)
            amount = tds[7].text
            amount_min = amount.split('-')[0].replace('$', '').replace(' ', '').replace(',', '')
            amount_max = amount.split('-')[1].replace('$', '').replace(' ', '').replace(',', '')
            comment = tds[8].text.replace('\n', '').strip()

            df.loc[len(df.index)] = [url, owner, ticker, ticker_url, asset_name, trans_type, trans_date, amount_min, amount_max, comment]  

            if insert == False:
                continue
            else:
                # insert into postgresql
                from octopus.db import PostgresqlManager
                import psycopg2
                pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
                sql_insert_client_name_and_url = """
                INSERT INTO senate_annual_4b(report_url, owner, ticker, ticker_url, asset_name, trans_type, trans_date, amount_min, amount_max, comment)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                try:
                    pm.execute_sql(
                        sql=sql_insert_client_name_and_url,
                        parameters=(
                            url,
                            owner,
                            ticker,
                            ticker_url,
                            asset_name,
                            trans_type,
                            trans_date,
                            amount_min,
                            amount_max,
                            comment
                            ),
                        commit=True,
                    )
                except psycopg2.errors.UniqueViolation as e:
                    print(e)
                    pass
                pass


            pass
    pass


    driver.close()
    pass

if __name__ == "__main__":
    congress = 114
    years = reversed([year for year in range(2014, 2021)])

    for year in years:
        print("congress, year:", congress, year)
        from octopus.db import PostgresqlManager
        pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
        df = pm.execute_sql(fetchall=True, sql=
                    f"""select * from senate_annual sa 
                        inner join senator s on sa.url = s.url
                        where report_type ilike '%annual%{year}%' and s.congress = {congress}"""
                        )
        # df = df[36:] # this is to restart from somewhere in case of errors
        for row in tqdm(df):
            url = row[5] #url of annual report
            print(url)
            parse_annual(url=url)
        pass
        pass
