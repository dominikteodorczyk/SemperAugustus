"""
Main file of the program.
This is where the source code is located, which runs the program 
and controls its flow.

In the current version of the application, the main file calls 
the trading sessions on the defined assets (possibly all available 
in the XTB offer: 
https://www.xtb.com/en/trading-services/account-information/market-specification#forex
"""


from src.trading.broker import TradingSession

def main():
    # List of trading instruments to include in the session
    trading_instruments = ['EURUSD']  #'USDJPY','GBPUSD','US500','AUDUSD','USDCHF','USDCAD','GBPCHF'    
    session = TradingSession(trading_instruments)
    session.session_init()
   
if __name__ == '__main__':
    main()