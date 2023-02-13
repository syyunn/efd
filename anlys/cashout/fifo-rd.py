### implement fifo-random amount

import pandas as pd
import random
import numpy as np

result = pd.DataFrame({
        'first_name': [],
        'last_name': [],
        'ticker': [],

        'cash(amount_min)': [],
        'buy(amount_min)': [],
        'cashout(amount_min)': [],
        'matched_buy (amount_min)': [],
        'return(amount_min)': [],

        'cash(amount_max)': [],
        'buy(amount_max)': [],
        'cashout(amount_max)': [],
        'matched_buy (amount_max)': [],
        'return(amount_max)': [],

        'cash(amount_med)': [], # median of the amount_min and amount_max
        'buy(amount_med)': [],
        'cashout(amount_med)': [],
        'matched_buy (amount_med)': [],
        'return(amount_med)': []

        })

congress = 118

from octopus.db import PostgresqlManager
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
df = pm.execute_sql(fetchall=True, sql=
                f"""
                with union4ab as (
                    select * from senate_annual_4a saa 
                    union
                    select * from senate_annual_4b sab 
                )
                select distinct sa.first_name, sa.last_name, u.ticker from union4ab u
                    inner join senate_annual sa on sa.report_type_url  = u.report_url
                    inner join senator s on s.url = sa.url
                    -- where s.congress = {congress}
                order by first_name, last_name
                """
                )

row = ('Angus S', 'King, Jr.', 'ARKK')
row = ('Angus S', 'King, Jr.', 'QQQ')

backslash_char = '\''
trnscs = pm.execute_sql(fetchall=True, sql=
            f"""
            with union4ab as (
                select * from senate_annual_4a saa 
                union
                select * from senate_annual_4b sab 
            )
            select distinct first_name, last_name, p.ticker, trans_type, trans_date, amount_min, vwap, amount_max from union4ab u
                inner join senate_annual sa on sa.report_type_url  = u.report_url 
                inner join price p on (p.ticker=u.ticker and p.date=u.trans_date)
            where first_name = {backslash_char}{row[0]}{backslash_char} and last_name = {backslash_char}{row[1]}{backslash_char} and u.ticker = {backslash_char}{row[2]}{backslash_char} and vwap is not null
            order by trans_date asc
            """
            )



return_rds = []
return_rd_mean_prev = 0.1
return_rd_std_prev = 0.1

i = 0
def compute_return_rd():
    cash_random = 0
    purchase_units_random = []
    cashout_random = 0
    buy_random = 0 # this is the sum of the money spent on buying stocks and securities
    matched_buy_random = 0


    trnsc_types = [trnsc[3] for trnsc in trnscs]
    for idx, trnsc in enumerate(trnscs): # all transactions of a name and ticker pair
            ticker = trnsc[2]
            ps = trnsc[3] # purchase or sale
            date = trnsc[4]
            amount_min = trnsc[5]
            vwap = trnsc[6]
            amount_max = trnsc[7]
            # random select one value between amount_min and amount_max
            amount_random = random.uniform(amount_min, amount_max)
            # print(amount_min, amount_max, amount_random)
            
            future_transactions = trnsc_types[idx+1:]
            if "Purchase" in ps and set(["Purchase"]) == set(future_transactions): # if there's no more sales in the future, just end the loop
                break

            def _cash_out(purchase_units, cash, ps, amount, vwap, buy, cash_out, matched_buy):
                if "Purchase" in ps:
                    units = amount / vwap # this is the minimum amount of units purchased
                    purchase_units.append((units, vwap))
                    cash -= amount
                    buy += amount
                elif "Sale" in ps:
                    units = amount / vwap # minimum units estimated as being sold.
                    for idx, purchase in enumerate(purchase_units):
                        stock, purchase_price = purchase
                        if units == 0:
                            break                           
                        if units >= stock:
                            units -= stock
                            purchase_units[idx] = (0, purchase_price)
                            matched_buy += stock * purchase_price
                            cash_out += stock * vwap
                            cash += stock * vwap
                        elif units < stock:
                            units -= units
                            purchase_units[idx] = (stock - units, purchase_price)
                            matched_buy += units * purchase_price
                            cash_out += units * vwap
                            cash += units * vwap                            
                return purchase_units, cash, buy, cash_out, matched_buy
            
            purchase_units_random, cash_random, buy_random, cashout_random, matched_buy_random   = _cash_out(purchase_units_random, cash_random, ps, amount_random, vwap, buy_random, cashout_random, matched_buy_random)

    return_rd = (cashout_random - abs(matched_buy_random)) * 100 / abs(matched_buy_random) if matched_buy_random != 0 else 0
    return return_rd

warm_up = 10000
for i in range(warm_up):
    return_rd = compute_return_rd()
    return_rds.append(return_rd)

return_rd_mean_prev = np.mean(return_rds)
return_rd_std_prev = np.std(return_rds)

while abs(return_rd_mean_prev-np.mean(return_rds)) < 1e-5 and abs(return_rd_std_prev-np.std(return_rds)) < 1e-5:
    return_rd = compute_return_rd()
    return_rds.append(return_rd)

# Plot density using a kernel density estimation (KDE)
import numpy as np
import matplotlib.pyplot as plt

plt.hist(return_rds, bins=100, density=True, alpha=0.7, color='b')
plt.title('Density Plot of Data')
plt.xlabel('Value')
plt.ylabel('Density')
print("Show")
plt.show()