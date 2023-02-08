from pyrh import Robinhood
from dotenv import load_dotenv
import os

env = load_dotenv('/Users/syyun/Dropbox (MIT)/efd/.env')

rh = Robinhood(username="syyun@mit.edu", password=os.getenv("ROBINHOOD_PASSWORD"), store_session=True)
rh.login()
rh.print_quote("AAPL")