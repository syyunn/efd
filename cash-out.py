import pandas as pd

result = pd.DataFrame({
        'first_name': [],
        'last_name': [],
        'ticker': [],
        'cash(amount_min)': [],
        'cash(amount_max)': []
        })

congress = 117

from octopus.db import PostgresqlManager
pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.env")
df = pm.execute_sql(fetchall=True, sql=
                f"""
                select distinct sa.first_name, sa.last_name, sb.ticker from senate_annual_4b sb
   inner join senate_annual sa on sa.report_type_url  = sb.report_url
   inner join senator s on s.url = sa.url
   where s.congress = {congress}
   order by first_name, last_name
                """
                )
for row in df: # name and ticker pairs
    backslash_char = '\''
    trnscs = pm.execute_sql(fetchall=True, sql=
                f"""
select distinct first_name, last_name, p.ticker, trans_type, trans_date, amount_min, vwap, amount_max from senate_annual_4b sb 
inner join senate_annual sa on sa.report_type_url  = sb.report_url 
inner join price p on (p.ticker=sb.ticker and p.date=sb.trans_date)
where first_name = {backslash_char}{row[0]}{backslash_char} and last_name = {backslash_char}{row[1]}{backslash_char} and sb.ticker = {backslash_char}{row[2]}{backslash_char}
order by trans_date asc
                """
                )
    # check only the cases which starts as purchase and ends as sell
    if len(trnscs) >1: # for the case of ticker is None
        cash_amin = 0
        cash_amax = 0

        purchase_units_amin = []
        purchase_units_amax = []

        for trnsc in trnscs: # all transactions of a name and ticker pair
            ticker = trnsc[2]
            ps = trnsc[3] # purchase or sale
            date = trnsc[4]
            amount_min = trnsc[5]
            vwap = trnsc[6]
            amount_max = trnsc[7]
            
            def _cash_out(purchase_units, cash, ps, amount, vwap):
                current_holdings = sum(purchase_units)

                if "Purchase" in ps:
                    units = amount / vwap # this is the minimum amount of units purchased
                    purchase_units.append(units)
                    cash -= amount
                elif "Sale" in ps:
                    units = amount / vwap # minimum units estimated as being sold.
                    if units > current_holdings: # this means we're missing previous data about purchasement
                        purchase_units.append(-current_holdings) # sell all of the holdings
                        cash_out = current_holdings * vwap
                        cash += cash_out                    
                    else:
                        purchase_units.append(-units)
                        cash_out = units * vwap
                        cash += cash_out
                return purchase_units, cash

            purchase_units_amin, cash_amin = _cash_out(purchase_units_amin, cash_amin, ps, amount_min, vwap)
            purchase_units_amax, cash_amax = _cash_out(purchase_units_amax, cash_amax, ps, amount_max, vwap)
            pass
        result.loc[len(result.index)] = [row[0], row[1], row[2], cash_amin, cash_amax]  
        print(row[0], row[1], row[2], cash_amin, cash_amax)


    pass
pass
