import yfinance as yf
import inspect

tsla = yf.Ticker("TSLA")
# print(tsla)
"""
returns
<yfinance.Ticker object at 0x1a1715e898>
"""

# get stock info
# print(tsla.info)

"""
returns:
{
 'quoteType': 'EQUITY',
 'quoteSourceName': 'Nasdaq Real Time Price',
 'currency': 'USD',
 'shortName': 'Microsoft Corporation',
 'exchangeTimezoneName': 'America/New_York',
  ...
 'symbol': 'MSFT'
}
"""

# get historical market data, here max is 5 years.
# print(tsla.history(period="1d", interval="1m"))

tesla_daily = tsla.history(period="1d", interval="1m", prepost=True)

print(tesla_daily)

tesla_daily.to_csv("out.csv")
# print(tesla_daily.columns)
# print(tsla.options)

f = tsla.option_chain('2020-02-27').calls
f.to_csv('chain.csv')
g = tsla.option_chain('2020-03-05').calls
g.to_csv('chain2.csv')

# print(f.columns)

