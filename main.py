import psycopg2
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from dateutil import parser
# from lobbyview.db import PostgresqlManager
from octopus.db import PostgresqlManager


def scrape_one_page(df, driver, url):
    sql_insert_client_name_and_url = """
    INSERT INTO senate_annual(url, first_name, last_name, office, report_type, report_type_url, date_received)
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    """

    url_prefix = "https://efdsearch.senate.gov/"
    import time

    time.sleep(0.5)
    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")
    table = bs.find("table", {"id": "filedReports"})
    trs = table.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) > 1:
            first_name = tds[0].text
            last_name = tds[1].text
            office = tds[2].text
            report_type = tds[3].text
            report_type_url = tds[3].find("a")["href"]
            date_received = parser.parse(tds[4].text)
            df.loc[len(df.index)] = [
                url,
                first_name,
                last_name,
                office,
                report_type,
                url_prefix + report_type_url,
                date_received,
            ]
            pass
            pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
            try:
                pm.execute_sql(
                    sql=sql_insert_client_name_and_url,
                    parameters=(
                        url,
                        first_name,
                        last_name,
                        office,
                        report_type,
                        url_prefix + report_type_url,
                        date_received,
                    ),
                    commit=True,
                )
                # print("insert", (
                #         url,
                #         first_name,
                #         last_name,
                #         office,
                #         report_type,
                #         url_prefix + report_type_url,
                #         date_received,
                #     ))
            except psycopg2.errors.UniqueViolation:
                pass
            pass
        else:
            pass
    
    next_btn = driver.find_element(By.CSS_SELECTOR, ".paginate_button.next")
    
    try:
        driver.find_element(By.CSS_SELECTOR, ".paginate_button.next.disabled")
        next_btn = False
    except selenium.common.exceptions.NoSuchElementException:
        pass
    
    return next_btn


def scrape_insert_one_legislator(first_name, last_name, url):
    chrome_options = Options()
    chrome_options.add_argument("--headless") # only in case you wanna run it in headless
    chrome_options.add_experimental_option("detach", True)
    global browser  # this will prevent the browser variable from being garbage collected
    # from lobbyview.db import PostgresqlManager

    edf = "https://efdsearch.senate.gov/search/"
    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )
    driver.get(edf)

    # check the input box
    inputElement = driver.find_element(By.ID, "agree_statement").click()
    # this will automatically let the page turn into serach
    inputElement = driver.find_element(By.ID, "firstName").send_keys(first_name)
    inputElement = driver.find_element(By.ID, "lastName").send_keys(last_name)
    # this is to search Annual Report only
    inputElement = driver.find_element(By.ID, "reportTypeLabelAnnual").find_element(By.ID, "reportTypes").click()

    driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary").click()

    import pandas as pd

    df = pd.DataFrame(
        {
            "url": [],
            "firstname": [],
            "last_name": [],
            "url": [],
            "office": [],
            "report_type": [],
            "report_type_url": [],
            "date_received": [],
        }
    )

    next_btn = True
    while next_btn:
        next_btn = scrape_one_page(df, driver, url)
        if next_btn:
            next_btn.click()
    driver.close()


if __name__ == "__main__":
    from utils import get_senators
    congress = 117
    print("Congress", congress)
    df = get_senators(n_th_congress=congress) # this part can be replaced w/ db-fetch
    df = df.loc[16:, :]
    for row in df.itertuples():
        print(row.first_name, row.last_name, row.url)        
        scrape_insert_one_legislator(row.first_name,  row.last_name, row.url)
        pass
    # scrape_insert_one_legislator("Patty", "Murray", "https://en.wikipedia.org//wiki/Patty_Murray") # for test purpose
    pass