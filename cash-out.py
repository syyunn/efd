import pandas as pd

result = pd.DataFrame({
        'first_name': [],
        'last_name': [],
        'ticker': [],
        'cash': []
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
select distinct first_name, last_name, p.ticker, trans_type, trans_date, amount_min, vwap from senate_annual_4b sb 
inner join senate_annual sa on sa.report_type_url  = sb.report_url 
inner join price p on (p.ticker=sb.ticker and p.date=sb.trans_date)
where first_name = {backslash_char}{row[0]}{backslash_char} and last_name = {backslash_char}{row[1]}{backslash_char} and sb.ticker = {backslash_char}{row[2]}{backslash_char}
order by trans_date asc
                """
                )
    # check only the cases which starts as purchase and ends as sell
    if len(trnscs) >1: # for the case of ticker is None
        # if "Purchase" in trnscs[0][3] and "Sale (Full)" in trnscs[-1][3]:
        # if "Purchase" in trnscs[0][3] and "Sale (Full)" in trnscs[-1][3]:
        #     print(row[0], row[1], row[2])
        cash = 0
        purchase_units = []

        for trnsc in trnscs: # all transactions of a name and ticker pair
            ticker = trnsc[2]
            ps = trnsc[3] # purchase or sale
            date = trnsc[4]
            amount = trnsc[5]
            vwap = trnsc[6]

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

            # elif "Sale (Full)" in ps:
            #     units = amount / bars[0].vwap # minimum units estimated as being sold.
            #     if units > current_holdings: # this means we're missing previous data about purchasement
            #         print("break! insufficient holdings to sell all", row[0], row[1], row[2])
            #         break
            #     else:
            #         purchase_units.append(-current_holdings) # sell all of the holdings
            #         cash_out = current_holdings * bars[0].vwap
            #         cash += cash_out      
            # elif "Sale (Partial)" in ps:
            #     units = amount / bars[0].vwap # minimum amount estimated as being sold.
            #     if units > current_holdings: # this means we're missing previous data because one can't sell more than what they have
            #         print("break! insufficient holdings to sell", row[0], row[1], row[2])
            #         break
            #     else:
            #         purchase_units.append(-units)
            #         cash_out = units * bars[0].vwap
            #         cash += cash_out
            pass
        result.loc[len(result.index)] = [row[0], row[1], row[2], cash]  
        print(row[0], row[1], row[2], cash)


    pass
pass
