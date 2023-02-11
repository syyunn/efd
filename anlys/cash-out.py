import pandas as pd

result = pd.DataFrame({
        'first_name': [],
        'last_name': [],
        'ticker': [],
        'cash(amount_min)': [],
        'buy(amount_min)': [],
        'cashout(amount_min)': [],
        'cash(amount_max)': [],
        'buy(amount_max)': [],
        'cashout(amount_max)': [],
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
   where s.congress = {congress}
   order by first_name, last_name
                """
                )
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
    # check only the cases which starts as purchase and ends as sell
    if len(trnscs) >1: # for the case of ticker is None
        cash_amin = 0
        cash_amax = 0

        purchase_units_amin = []
        purchase_units_amax = []

        cashout_amin = 0
        buy_amin = 0 # this is the sum of the money spent on buying stocks and securities

        cashout_amax = 0
        buy_amax = 0 # this is the sum of the money spent on buying stocks and securities

        for trnsc in trnscs: # all transactions of a name and ticker pair
            ticker = trnsc[2]
            ps = trnsc[3] # purchase or sale
            date = trnsc[4]
            amount_min = trnsc[5]
            vwap = trnsc[6]
            amount_max = trnsc[7]
            
            def _cash_out(purchase_units, cash, ps, amount, vwap, buy, cashout):
                current_holdings = sum(purchase_units)

                if "Purchase" in ps:
                    units = amount / vwap # this is the minimum amount of units purchased
                    purchase_units.append(units)
                    cash -= amount
                    buy -= amount
                elif "Sale" in ps:
                    units = amount / vwap # minimum units estimated as being sold.
                    if units > current_holdings: # this means we're missing previous data about purchasement
                        purchase_units.append(-current_holdings) # sell all of the holdings
                        cash_out = current_holdings * vwap
                        cash += cash_out
                        cashout += cash_out
                    else:
                        purchase_units.append(-units)
                        cash_out = units * vwap
                        cash += cash_out
                        cashout += cash_out
                return purchase_units, cash, buy, cashout

            purchase_units_amin, cash_amin, buy_amin, cashout_amin   = _cash_out(purchase_units_amin, cash_amin, ps, amount_min, vwap, buy_amin, cashout_amin)
            purchase_units_amax, cash_amax, buy_amax, cashout_amax = _cash_out(purchase_units_amax, cash_amax, ps, amount_max, vwap, buy_amax, cashout_amax)
            pass
        result.loc[len(result.index)] = [row[0], row[1], row[2], cash_amin, buy_amin, cashout_amin, cash_amax, buy_amax, cashout_amax]  
        print(row[0], row[1], row[2], cash_amin, buy_amin, cashout_amin, cash_amax, buy_amax, cashout_amax)

    pass
pass
