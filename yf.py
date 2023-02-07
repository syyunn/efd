import yfinance as yf

msft = yf.Ticker("NFRA")

# get all stock info (slow)
msft.info
# fast access to subset of stock info (opportunistic)
msft.fast_info

# get historical market data
hist = msft.history(period="1mo")

pass