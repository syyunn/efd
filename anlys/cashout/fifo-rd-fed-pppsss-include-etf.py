### implement fifo-random amount - demeaned by fed rates

import pandas as pd
import random
import numpy as np
from dotenv import load_dotenv
from datetime import datetime


result = pd.DataFrame({
        'bioguide_id': [],
        'first_name': [],
        'last_name': [],
        'idx': [],
        'start_date': [],
        'end_date': [],
        'ticker': [],
        'return(mean)': [],
        'return(std)': []
        })

from octopus.db import PostgresqlManager
load_dotenv("/Users/syyun/Dropbox (MIT)/efd/.envlv", override=True)
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
df = pm.execute_sql(fetchall=True, sql=
                f"""
                with union4ab as (
                    select * from _sandbox_suyeol.senate_annual_4a saa 
                    union
                    select * from _sandbox_suyeol.senate_annual_4b sab 
                )
                select distinct bioguide_id, sa.first_name, sa.last_name, u.ticker from union4ab u
                    inner join _sandbox_suyeol.senate_annual sa on sa.report_type_url  = u.report_url
                    inner join _sandbox_suyeol.senator_bioguide sb on sb.first_name = sa.first_name and sb.last_name = sa.last_name
                   -- inner join _sandbox_suyeol.senator s on s.url = sa.url
                order by first_name, last_name
                """
                )

# row = ('Angus S', 'King, Jr.', 'ARKK')
# row = ('Angus S', 'King, Jr.', 'QQQ')

# read fed rates
fed_rates = pd.read_csv("external-data/FEDFUNDS.csv")

from tqdm import tqdm

for row in tqdm(df): # name and ticker pairs
    print(row)
    senator = row[0] + row[1] + ' ' + row[2] 
    ticker = row[3]
    backslash_char = '\''
    trnscs = pm.execute_sql(fetchall=True, sql=
                f"""
                with union4ab as (
                    select * from _sandbox_suyeol.senate_annual_4a saa 
                    union
                    select * from _sandbox_suyeol.senate_annual_4b sab 
                )
                select distinct bioguide_id, p.ticker, trans_type, trans_date, amount_min, vwap, amount_max from union4ab u
                    inner join _sandbox_suyeol.senate_annual sa on sa.report_type_url  = u.report_url
                    inner join _sandbox_suyeol.senator_bioguide sb on sb.first_name = sa.first_name and sb.last_name = sa.last_name
                    inner join _sandbox_suyeol.price p on (p.ticker=u.ticker and p.date=u.trans_date)
                where bioguide_id = {backslash_char}{row[0]}{backslash_char} and u.ticker = {backslash_char}{row[3]}{backslash_char} and vwap is not null
                order by trans_date asc
                """
                )
    
    def find_subchains(transaction_chain):
        import re
        pattern = r'p+[^ps]*(?:s(?!p)[^ps]*)*s+'
        matches = re.finditer(pattern, transaction_chain)
        subchains = []
        for match in matches:
            start, end = match.start(), match.end()
            subchain = transaction_chain[start:end]
            longest_match = max(re.findall(r'p+[^ps]*s+', subchain), key=len)
            subchains.append((start, end, longest_match))
        return subchains
    
    transaction_chain = ''.join([t[2][0] for t in trnscs]).lower()
    subchains = find_subchains(transaction_chain)
    
    if len(subchains) == 0:
        print("No subchains found for", senator, ticker)
        continue
    else:
        print("Subchains found for", senator, ticker, len(subchains))
    
    for idx, subchain in enumerate(subchains):
        start, end, pattern = subchain
        trnscs_subchain = trnscs[start:end]

        start_date = trnscs[start][3]
        end_date = trnscs[end-1][3]

        return_rds = []

        def compute_return_rd(trnscs_subchain):

            cash_random = 0
            purchase_units_random = []
            cashout_random = 0
            buy_random = 0 # this is the sum of the money spent on buying stocks and securities
            matched_buy_random = 0


            trnsc_types = [trnsc[2] for trnsc in trnscs_subchain]
            for idx, trnsc in enumerate(trnscs): # all transactions of a name and ticker pair
                    ps = trnsc[2] # purchase or sale
                    date = datetime.strptime(trnsc[3], "%Y-%m-%d")
                    amount_min = trnsc[4]
                    vwap = trnsc[5]
                    amount_max = trnsc[6]
                    # random select one value between amount_min and amount_max
                    amount_random = random.uniform(amount_min, amount_max)
                    # print(amount_min, amount_max, amount_random)
                    
                    future_transactions = trnsc_types[idx+1:]

                    if "Purchase" in ps and set(["Purchase"]) == set(future_transactions): # if there's no more sales in the future, just end the loop
                        break

                    def _cash_out(purchase_units, cash, ps, amount, vwap, buy, cash_out, matched_buy, date):
                        if "Purchase" in ps:
                            units = amount / vwap # this is the minimum amount of units purchased
                            date_purchase = date.strftime('%Y-%m-01') # get the monthly rates
                            purchase_units.append((units, vwap, date_purchase)) # fed_rate is kind of opportunity cost
                            cash -= amount
                            buy += amount
                        elif "Sale" in ps:
                            date_sale = date.strftime('%Y-%m-01')
                            units = amount / vwap # minimum units estimated as being sold.
                            for idx, purchase in enumerate(purchase_units):
                                stock, purchase_price, date_purchase = purchase
                                if units == 0:
                                    break                           
                                if units >= stock:
                                    units -= stock
                                    purchase_units[idx] = (0, purchase_price, date_purchase)
                                    matched_buy += stock * purchase_price

                                    purchase_date_index = fed_rates.index[fed_rates['date'] == date_purchase]
                                    sale_date_index = fed_rates.index[fed_rates['date'] == date_sale]
                                    fed_rates_avg = np.mean(fed_rates.iloc[purchase_date_index[0]:sale_date_index[0]+1]['rate'])
                                    opp_cost = fed_rates_avg * stock * purchase_price / 100
                                    cash_out += stock * vwap - opp_cost
                                    cash += stock * vwap
                                elif units < stock:
                                    units -= units
                                    purchase_units[idx] = (stock - units, purchase_price, date_purchase)
                                    matched_buy += units * purchase_price

                                    purchase_date_index = fed_rates.index[fed_rates['date'] == date_purchase]
                                    sale_date_index = fed_rates.index[fed_rates['date'] == date_sale]
                                    fed_rates_avg = np.mean(fed_rates.iloc[purchase_date_index[0]:sale_date_index[0]+1]['rate'])
                                    opp_cost = fed_rates_avg * units * purchase_price / 100

                                    cash_out += units * vwap - opp_cost
                                    cash += units * vwap                            
                        return purchase_units, cash, buy, cash_out, matched_buy
                    
                    purchase_units_random, cash_random, buy_random, cashout_random, matched_buy_random   = _cash_out(purchase_units_random, cash_random, ps, amount_random, vwap, buy_random, cashout_random, matched_buy_random, date)

            return_rd = (cashout_random - abs(matched_buy_random)) * 100 / abs(matched_buy_random) if matched_buy_random != 0 else 0
            return return_rd

        warm_up = 1000
        for i in range(warm_up):
            return_rd = compute_return_rd(trnscs_subchain)
            return_rds.append(return_rd)

        return_rd_mean_prev = np.mean(return_rds)
        return_rd_std_prev = np.std(return_rds)

        # thres = 1e-3
        # i = 0
        # while abs(return_rd_mean_prev-np.mean(return_rds)) >= thres and abs(return_rd_std_prev-np.std(return_rds)) >= thres and i < 10000:
        #     return_rd = compute_return_rd()
        #     print(return_rd)
        #     return_rds.append(return_rd)
        #     return_rd_mean_prev = np.mean(return_rds)
        #     return_rd_std_prev = np.std(return_rds)
        #     i += 1

        print(row, np.mean(return_rds), np.std(return_rds))

        result.loc[len(result.index)] = [
            row[0],
            row[1],
            row[2],
            idx,
            start_date,
            end_date,
            row[3],
            np.mean(return_rds),
            np.std(return_rds)
        ]
        pass

        # Plot density using a kernel density estimation (KDE)
        import numpy as np  
        import matplotlib.pyplot as plt

        plt.hist(return_rds, bins=100, density=True, alpha=0.7, color='b')
        plt.title('Density Plot of Excess Return')
        plt.xlabel('Excess Return (%)')
        plt.ylabel('Density')
        # plt.show()
        plt.savefig(f'./anlys/cashout/rd-results-fed-pppsss-include-etf/{senator}-{ticker}-{idx}-{start_date}-{end_date}.png')
        plt.close()

import pickle
with open(f'./anlys/cashout/rd-results-fed-pppsss-include-etf.pkl', 'wb') as f:
    pickle.dump(result, f)
