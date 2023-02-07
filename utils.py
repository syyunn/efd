import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_senators(n_th_congress):
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
            df.loc[len(df.index)] = [n_th_congress, first_name, last_name, party, 'https://en.wikipedia.org/' + url]   
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
                        url                    ),
                    commit=True,
                )
            except psycopg2.errors.UniqueViolation:
                pass
            pass


    return df

def parse_annual(firstname, lastname, url):
    import selenium
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    # from lobbyview.db import PostgresqlManager

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )

    # get base url and click on agreement
    base_url = "https://efdsearch.senate.gov/search/"
    driver.get(base_url)
    driver.find_element(By.ID, "agree_statement").click() 

    # go to actual target url which contains the annual report
    driver.get(url)
    html = driver.page_source

    bs = BeautifulSoup(html, "html.parser")
    tables = bs.find_all("table")
    tbody = tables[3].find("tbody")
    trs = tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) > 1:
            print(tds[0].text, tds[1].text)
    pass



    pass




if __name__ == "__main__":
    for i in range(114, 118): # other than this period, the format of the wikipedia page is different
        df = get_senators(n_th_congress=i)
    # df = get_senators(n_th_congress=118)
    # # df = parse_annual(url="https://efdsearch.senate.gov//search/view/annual/2f72a35a-adad-4555-8341-01eacbd507d3/")
    pass