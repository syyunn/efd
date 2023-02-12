import pandas as pd
from tqdm import tqdm

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

chains = []

for row in df: # name and ticker pairs
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
    # check whether purchase and sale both in the transactions
    pass
    trnsc_types = [trnsc[3] for trnsc in trnscs]
    trnsc_types_string = ''.join(['p' if trnsc_type == 'Purchase' else 's' for trnsc_type in trnsc_types])

    if 'p' in trnsc_types_string and 's' in trnsc_types_string:
        m = True
        pad = 0
        while m:
            import re 
            m  = re.search(r"p+s+", trnsc_types_string)
            if (m is not None) and len(trnsc_types_string) >= 2:
                # chains.append(trnsc_types_string[m.start():m.end()])
                chains.append(trnscs[m.start()+pad:m.end()+pad])
                trnsc_types_string = trnsc_types_string[m.end():]
                pad += m.end() 
                pass
            else:
                break
            pass
    else:
        continue
 

#     # check only the cases which starts as purchase and ends as sell
#     if len(trnscs) >1: # for the case of ticker is None
#         cash_amin = 0
#         cash_amax = 0
#         cash_amed = 0

#         purchase_units_amin = []
#         purchase_units_amax = []
#         purchase_units_amed = []

#         cashout_amin = 0
#         buy_amin = 0 # this is the sum of the money spent on buying stocks and securities
#         matched_buy_amin = 0

#         cashout_amax = 0
#         buy_amax = 0 # this is the sum of the money spent on buying stocks and securities
#         matched_buy_amax = 0

#         cashout_amed = 0
#         buy_amed = 0 # this is the sum of the money spent on buying stocks and securities
#         matched_buy_amed = 0

#         trnsc_types = [trnsc[3] for trnsc in trnscs]
#         for idx, trnsc in enumerate(trnscs): # all transactions of a name and ticker pair
#             ticker = trnsc[2]
#             ps = trnsc[3] # purchase or sale
#             date = trnsc[4]
#             amount_min = trnsc[5]
#             vwap = trnsc[6]
#             amount_max = trnsc[7]
#             print("amount_min/max: ", amount_min, amount_max)
#             weight = 0.9
#             amount_med = weight * amount_min + (1-weight) * amount_max 

#             future_transactions = trnsc_types[idx+1:]
#             if "Purchase" in ps and set(["Purchase"]) == set(future_transactions): # if there's no more sales, just end the loop
#                 break

#             def _cash_out(purchase_units, cash, ps, amount, vwap, buy, cash_out, matched_buy):
#                 if "Purchase" in ps:
#                     units = amount / vwap # this is the minimum amount of units purchased
#                     purchase_units.append((units, vwap))
#                     cash -= amount
#                     buy += amount
#                 elif "Sale" in ps:
#                     units = amount / vwap # minimum units estimated as being sold.
#                     for idx, purchase in enumerate(purchase_units):
#                         stock, purchase_price = purchase
#                         if units == 0:
#                             break                           
#                         if units >= stock:
#                             units -= stock
#                             purchase_units[idx] = (0, purchase_price)
#                             matched_buy += stock * purchase_price
#                             cash_out += stock * vwap
#                             cash += stock * vwap
#                         elif units < stock:
#                             units -= units
#                             purchase_units[idx] = (stock - units, purchase_price)
#                             matched_buy += units * purchase_price
#                             cash_out += units * vwap
#                             cash += units * vwap                            
#                 return purchase_units, cash, buy, cash_out, matched_buy

#             purchase_units_amin, cash_amin, buy_amin, cashout_amin, matched_buy_amin   = _cash_out(purchase_units_amin, cash_amin, ps, amount_min, vwap, buy_amin, cashout_amin, matched_buy_amin)
#             purchase_units_amax, cash_amax, buy_amax, cashout_amax, matched_buy_amax = _cash_out(purchase_units_amax, cash_amax, ps, amount_max, vwap, buy_amax, cashout_amax, matched_buy_amax)
#             purchase_units_amed, cash_amed, buy_amed, cashout_amed, matched_buy_amed = _cash_out(purchase_units_amed, cash_amed, ps, amount_med, vwap, buy_amed, cashout_amed, matched_buy_amed)
#             pass

#         return_amin = (cashout_amin - abs(matched_buy_amin)) * 100 / abs(matched_buy_amin) if matched_buy_amin != 0 else 0
#         return_amax = (cashout_amax - abs(matched_buy_amin)) * 100/ abs(matched_buy_amax) if matched_buy_amax != 0 else 0
#         return_amed = (cashout_amed - abs(matched_buy_amin)) * 100/ abs(matched_buy_amed) if matched_buy_amed != 0 else 0

#         result.loc[len(result.index)] = [row[0], row[1], #name
#                                          row[2], #tiker
#                                          cash_amin, buy_amin, cashout_amin,  matched_buy_amin, return_amin, 
#                                          cash_amax, buy_amax, cashout_amax, matched_buy_amax, return_amax,
#                                          cash_amed, buy_amed, cashout_amed, matched_buy_amed, return_amed]
        
#         print(row[0], row[1], row[2], cash_amin, buy_amin, cashout_amin, matched_buy_amin, return_amin, cash_amax, buy_amax, cashout_amax, matched_buy_amax, return_amax, cash_amed, buy_amed, cashout_amed, matched_buy_amed, return_amed)    
#     pass

# def _get_above_return_ratio(amount="amount_min", return_threshold=0):
#     return len(result[result[f'return({amount})'] > return_threshold])/len(result) * 100

# ratio_min = _get_above_return_ratio("amount_min")
# ratio_max = _get_above_return_ratio("amount_max")
# ratio_med = _get_above_return_ratio("amount_med")

# pass
pass