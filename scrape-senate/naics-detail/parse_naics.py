from octopus.db import PostgresqlManager
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import psycopg2
from tqdm import tqdm
# env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')

load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.envlv', override=True)
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
# pm = PostgresqlManager(dotenv_path="/home/ubuntu/.envlv")

df = pm.execute_sql(fetchall=True, sql= """
select ticker, tnu.naics_url from _sandbox_suyeol.ticker_naics_url tnu 	
	left join _sandbox_suyeol.ticker_naics tn on tn.naics_url  = tnu.naics_url  
	where tnu.naics_url != \'Not found\' and company_name is Null
    """)
                    
sql_insert = """
INSERT INTO _sandbox_suyeol.ticker_naics(naics_url, duns, company_name, trade_style, url, naics1, naics1_desc, naics2, naics2_desc, sic1, sic1_desc, sic2, sic2_desc, total_emp, sales_volume)
VALUES(%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for ticker, naics_url in tqdm(df):
    print(naics_url)
    response = requests.get(naics_url)
    bs = BeautifulSoup(response.content, 'html.parser')
    table = bs.find("table", attrs={"class": "companyDetail topCompanyDetail"})
    tds = table.find_all("td")
    duns = tds[0].text
    company_name = tds[1].text.replace("Company Name:", "").strip()
    trade_style = tds[2].text.replace("Tradestyle:", "").strip()
    if "URL:" in tds[7].text:
        url = "https://" + tds[7].text.replace("URL:", "").strip()
        total_emp = int(tds[8].text.replace("Total Emps:", "").replace(",","").strip())
        sales_volume = int(tds[10].text.replace("Sales Volume:", "").replace("$", "").replace(",","").replace("\'", "").strip())
        naics1 = tds[15].text.replace("NAICS 1:", "").strip()
        naics1_desc = tds[16].text.strip()
        naics2 = tds[17].text.replace("NAICS 2:", "").strip()
        naics2_desc = tds[18].text.strip()
        sic1 = tds[19].text.replace("SIC 1:", "").strip()
        sic1_desc = tds[20].text.strip()
        sic2 = tds[21].text.replace("SIC 2:", "").strip()
        sic2_desc = tds[22].text.strip()
    else:
        url = None
        total_emp = int(tds[7].text.replace("Total Emps:", "").replace(",","").strip())
        sales_volume = int(tds[9].text.replace("Sales Volume:", "").replace("$", "").replace(",","").replace("\'", "").strip())
        naics1 = tds[14].text.replace("NAICS 1:", "").strip()
        naics1_desc = tds[15].text.strip()
        naics2 = tds[16].text.replace("NAICS 2:", "").strip()
        naics2_desc = tds[17].text.strip()
        sic1 = tds[18].text.replace("SIC 1:", "").strip()
        sic1_desc = tds[19].text.strip()
        sic2 = tds[20].text.replace("SIC 2:", "").strip()
        sic2_desc = tds[21].text.strip()


    try:
        pm.execute_sql(
            sql=sql_insert,
            parameters=(
                naics_url,
                duns,
                company_name,
                trade_style,
                url,
                naics1,
                naics1_desc,
                naics2,
                naics2_desc,
                sic1,
                sic1_desc,
                sic2,
                sic2_desc,
                total_emp,
                sales_volume                
            ),
            commit=True,
        )
    except psycopg2.errors.UniqueViolation as e:
        print(e)
        pass
    pass                    
                    
if __name__ == "__main__":
    pass
                    

