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
            url = tds[0].find('a')['href']
            party = tds[1].text
            df.loc[len(df.index)] = [n_th_congress, first_name, last_name, party, 'https://en.wikipedia.org/' + url]   
    return df


if __name__ == "__main__":
    df = get_senators(n_th_congress=118)
    # df = parse_annual(url="https://efdsearch.senate.gov//search/view/annual/2f72a35a-adad-4555-8341-01eacbd507d3/")
    pass